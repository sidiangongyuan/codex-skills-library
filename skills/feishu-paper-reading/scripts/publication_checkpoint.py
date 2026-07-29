#!/usr/bin/env python3
"""Create and advance a credential-free Feishu publication checkpoint."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


SCHEMA_VERSION = 1
RUN_ID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)
DOCUMENT_ID_RE = re.compile(r"^[A-Za-z0-9_-]{6,256}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
CONNECTOR_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
ALLOWED_STATES = {
    "prepared",
    "create_in_flight",
    "outcome_unknown",
    "created",
    "verified",
}
UNKNOWN_REASONS = {
    "create_outcome_ambiguous",
    "timeout_after_send",
    "connection_lost_after_send",
    "process_interrupted_after_send",
}
ABORT_BEFORE_SEND_REASONS = {
    "cli_launch_failed_before_send",
    "local_argument_validation_failed",
    "local_payload_read_failed",
    "preflight_failed_before_send",
}
DELIVERY_ROUTES = {"lark-cli", "connector"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _ensure_regular_file(path: Path) -> None:
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"expected a regular file: {path}")


def _anchored_path(path: Path) -> Path:
    absolute = Path(os.path.abspath(os.fspath(path.expanduser())))
    try:
        parent = absolute.parent.resolve(strict=True)
    except OSError as error:
        raise ValueError(f"parent directory does not exist: {absolute.parent}") from error
    if not parent.is_dir() or parent.is_symlink():
        raise ValueError(f"unsafe parent directory: {absolute.parent}")
    return parent / absolute.name


def _valid_profile(value: str | None) -> bool:
    return bool(
        isinstance(value, str)
        and value
        and value == value.strip()
        and len(value) <= 128
        and not any(ord(character) < 32 for character in value)
    )


def _normalize_sha256(value: str | None, field: str) -> str:
    normalized = value.casefold() if isinstance(value, str) else ""
    if not SHA256_RE.fullmatch(normalized):
        raise ValueError(f"{field} must be a SHA-256 digest")
    return normalized


def _normalize_config_dir(
    value: str | None,
    *,
    verify_directory: bool,
) -> str:
    if value is None:
        return ""
    if not value or value != value.strip():
        raise ValueError("config_dir must be a non-empty absolute path")
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        raise ValueError("config_dir must be absolute")
    absolute = Path(os.path.abspath(os.fspath(candidate)))
    if verify_directory:
        try:
            metadata = absolute.lstat()
        except OSError as error:
            raise ValueError("config_dir must exist") from error
        reparse_point = bool(getattr(metadata, "st_file_attributes", 0) & 0x400)
        if (
            absolute.is_symlink()
            or reparse_point
            or not stat.S_ISDIR(metadata.st_mode)
        ):
            raise ValueError("config_dir must be a real directory")
        try:
            resolved = absolute.resolve(strict=True)
        except OSError as error:
            raise ValueError("config_dir cannot be resolved safely") from error
        if os.path.normcase(os.fspath(resolved)) != os.path.normcase(
            os.fspath(absolute)
        ):
            raise ValueError("config_dir must not traverse links or reparse points")
        return os.fspath(resolved)
    return os.fspath(absolute)


def _config_dir_identity(config_dir: str) -> str:
    normalized = _normalize_config_dir(config_dir, verify_directory=True)
    if not normalized:
        return ""
    metadata = Path(normalized).lstat()
    material = "\0".join(
        (
            os.path.normcase(normalized),
            str(metadata.st_dev),
            str(metadata.st_ino),
            str(stat.S_IFMT(metadata.st_mode)),
        )
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def _delivery_binding(
    *,
    delivery_route: str,
    lark_cli_path: str | None = None,
    executable_sha256: str | None = None,
    profile: str | None = None,
    brand: str | None = None,
    app_id_sha256: str | None = None,
    user_open_id_sha256: str | None = None,
    config_dir: str | None = None,
    config_dir_identity_sha256: str | None = None,
    data_dir: str | None = None,
    data_dir_identity_sha256: str | None = None,
    connector_id: str | None = None,
    connector_identity_sha256: str | None = None,
    verify_executable: bool,
) -> dict[str, str]:
    if delivery_route not in DELIVERY_ROUTES:
        raise ValueError("unsupported delivery_route")
    if delivery_route == "lark-cli":
        if (
            lark_cli_path is None
            or not _valid_profile(profile)
            or brand not in {"feishu", "lark"}
        ):
            raise ValueError("lark-cli delivery requires path, profile, and brand")
        if connector_id is not None or connector_identity_sha256 is not None:
            raise ValueError("connector binding fields cannot be mixed with lark-cli")
        executable = _anchored_path(Path(lark_cli_path))
        _ensure_regular_file(executable)
        approved_executable_sha256 = _normalize_sha256(
            executable_sha256,
            "executable_sha256",
        )
        if verify_executable and sha256_file(executable) != approved_executable_sha256:
            raise ValueError("lark-cli executable hash does not match its binding")
        assert profile is not None
        assert brand is not None
        normalized_config_dir = _normalize_config_dir(
            config_dir,
            verify_directory=verify_executable,
        )
        if normalized_config_dir:
            normalized_config_identity = (
                _config_dir_identity(normalized_config_dir)
                if verify_executable
                else _normalize_sha256(
                    config_dir_identity_sha256,
                    "config_dir_identity_sha256",
                )
            )
        else:
            if config_dir_identity_sha256 not in {None, ""}:
                raise ValueError(
                    "config_dir_identity_sha256 requires config_dir"
                )
            normalized_config_identity = ""
        normalized_data_dir = _normalize_config_dir(
            data_dir,
            verify_directory=verify_executable,
        )
        if normalized_data_dir and not normalized_config_dir:
            raise ValueError("data_dir requires config_dir")
        if normalized_data_dir:
            normalized_data_identity = (
                _config_dir_identity(normalized_data_dir)
                if verify_executable
                else _normalize_sha256(
                    data_dir_identity_sha256,
                    "data_dir_identity_sha256",
                )
            )
        else:
            if data_dir_identity_sha256 not in {None, ""}:
                raise ValueError("data_dir_identity_sha256 requires data_dir")
            normalized_data_identity = ""
        return {
            "delivery_route": "lark-cli",
            "lark_cli_path": str(executable),
            "executable_sha256": approved_executable_sha256,
            "profile": profile,
            "brand": brand,
            "app_id_sha256": _normalize_sha256(
                app_id_sha256,
                "app_id_sha256",
            ),
            "user_open_id_sha256": _normalize_sha256(
                user_open_id_sha256,
                "user_open_id_sha256",
            ),
            "config_dir": normalized_config_dir,
            "config_dir_identity_sha256": normalized_config_identity,
            "data_dir": normalized_data_dir,
            "data_dir_identity_sha256": normalized_data_identity,
        }

    cli_values = (
        lark_cli_path,
        executable_sha256,
        profile,
        brand,
        app_id_sha256,
        user_open_id_sha256,
        config_dir,
        config_dir_identity_sha256,
        data_dir,
        data_dir_identity_sha256,
    )
    if any(value is not None for value in cli_values):
        raise ValueError("lark-cli binding fields cannot be mixed with connector")
    if not isinstance(connector_id, str) or not CONNECTOR_ID_RE.fullmatch(connector_id):
        raise ValueError("connector_id must be a stable non-secret identifier")
    return {
        "delivery_route": "connector",
        "connector_id": connector_id,
        "connector_identity_sha256": _normalize_sha256(
            connector_identity_sha256,
            "connector_identity_sha256",
        ),
    }


def _stored_delivery_binding(payload: Any) -> dict[str, str]:
    if not isinstance(payload, dict):
        raise ValueError("checkpoint delivery_binding is missing")
    route = payload.get("delivery_route")
    allowed_keys = (
        {
            "delivery_route",
            "lark_cli_path",
            "executable_sha256",
            "profile",
            "brand",
            "app_id_sha256",
            "user_open_id_sha256",
            "config_dir",
            "config_dir_identity_sha256",
            "data_dir",
            "data_dir_identity_sha256",
        }
        if route == "lark-cli"
        else {
            "delivery_route",
            "connector_id",
            "connector_identity_sha256",
        }
    )
    if set(payload) != allowed_keys:
        raise ValueError("checkpoint delivery_binding fields are invalid")

    def optional_stored_string(field: str) -> str | None:
        value = payload.get(field)
        if value is None or value == "":
            return None
        if not isinstance(value, str):
            raise ValueError(f"checkpoint {field} must be a string")
        return value

    return _delivery_binding(
        delivery_route=str(route),
        lark_cli_path=payload.get("lark_cli_path"),
        executable_sha256=payload.get("executable_sha256"),
        profile=payload.get("profile"),
        brand=payload.get("brand"),
        app_id_sha256=payload.get("app_id_sha256"),
        user_open_id_sha256=payload.get("user_open_id_sha256"),
        config_dir=optional_stored_string("config_dir"),
        config_dir_identity_sha256=optional_stored_string(
            "config_dir_identity_sha256"
        ),
        data_dir=optional_stored_string("data_dir"),
        data_dir_identity_sha256=optional_stored_string(
            "data_dir_identity_sha256"
        ),
        connector_id=payload.get("connector_id"),
        connector_identity_sha256=payload.get("connector_identity_sha256"),
        verify_executable=False,
    )


def _validate_document_url(document_url: str) -> str:
    try:
        parsed = urlsplit(document_url)
        port = parsed.port
    except ValueError as error:
        raise ValueError("document_url is malformed") from error
    host = (parsed.hostname or "").casefold().rstrip(".")
    allowed_host = (
        host == "feishu.cn"
        or host.endswith(".feishu.cn")
        or host == "larksuite.com"
        or host.endswith(".larksuite.com")
        or host == "larkoffice.com"
        or host.endswith(".larkoffice.com")
    )
    path_match = re.fullmatch(
        r"/(?:docx|docs)/([A-Za-z0-9_-]{6,256})/?",
        parsed.path,
    )
    if (
        parsed.scheme != "https"
        or not allowed_host
        or parsed.username is not None
        or parsed.password is not None
        or port not in {None, 443}
        or parsed.query
        or parsed.fragment
        or path_match is None
    ):
        raise ValueError("document_url is not an expected Feishu/Lark HTTPS URL")
    return path_match.group(1)


def _write_atomic(path: Path, data: bytes, *, replace: bool) -> None:
    path = _anchored_path(path)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary = Path(temporary_name)
    try:
        try:
            os.fchmod(fd, stat.S_IRUSR | stat.S_IWUSR)
        except (AttributeError, OSError):
            pass
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        if replace:
            os.replace(temporary, path)
        else:
            try:
                os.link(temporary, path)
            except FileExistsError:
                raise FileExistsError(
                    f"refusing to overwrite existing file: {path}"
                ) from None
            except OSError as error:
                raise OSError(
                    f"exclusive atomic create is unavailable for: {path}"
                ) from error
            temporary.unlink()
    finally:
        if temporary.exists():
            temporary.unlink()


def _write_json(path: Path, payload: dict[str, Any], *, replace: bool) -> None:
    data = json.dumps(
        payload,
        ensure_ascii=True,
        indent=2,
        sort_keys=True,
    ).encode("utf-8") + b"\n"
    _write_atomic(path, data, replace=replace)


def _read_state(path: Path) -> dict[str, Any]:
    _ensure_regular_file(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("checkpoint must contain one JSON object")
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported checkpoint schema")
    if payload.get("state") not in ALLOWED_STATES:
        raise ValueError("invalid checkpoint state")
    run_id = payload.get("run_id")
    if not isinstance(run_id, str) or not RUN_ID_RE.fullmatch(run_id):
        raise ValueError("invalid checkpoint run_id")
    state = payload["state"]
    document_id = payload.get("document_id")
    if state in {"created", "verified"}:
        if not isinstance(document_id, str) or not DOCUMENT_ID_RE.fullmatch(document_id):
            raise ValueError("created or verified checkpoint has no valid document_id")
    elif document_id is not None:
        raise ValueError("uncreated checkpoint must not contain a document_id")
    document_url = payload.get("document_url")
    if document_url is not None:
        if not isinstance(document_url, str):
            raise ValueError("document_url must be a string or null")
        if _validate_document_url(document_url) != document_id:
            raise ValueError("document_url does not match document_id")
    delivery_verified = payload.get("delivery_verified")
    if not isinstance(delivery_verified, bool):
        raise ValueError("delivery_verified must be boolean")
    if delivery_verified != (state == "verified"):
        raise ValueError("delivery_verified is inconsistent with checkpoint state")
    for counter in ("attempt_count", "reconciliation_count"):
        value = payload.get(counter, 0)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{counter} must be a nonnegative integer")
    unknown_reason = payload.get("unknown_reason")
    if unknown_reason is not None and unknown_reason not in UNKNOWN_REASONS:
        raise ValueError("invalid unknown_reason")
    abort_reason = payload.get("abort_before_send_reason")
    if abort_reason is not None and abort_reason not in ABORT_BEFORE_SEND_REASONS:
        raise ValueError("invalid abort_before_send_reason")
    retry_confirmation = payload.get("retry_confirmation")
    if retry_confirmation not in {None, "user_confirmed_no_match"}:
        raise ValueError("invalid retry_confirmation")
    normalized_binding = _stored_delivery_binding(payload.get("delivery_binding"))
    if payload.get("delivery_binding") != normalized_binding:
        raise ValueError("delivery_binding is not normalized")
    return payload


@contextlib.contextmanager
def _state_lock(state_path: Path):
    state_path = _anchored_path(state_path)
    lock_path = state_path.with_name(f".{state_path.name}.lock")
    if not lock_path.exists():
        try:
            _write_atomic(lock_path, b"\0", replace=False)
        except FileExistsError:
            pass
    metadata = lock_path.lstat()
    if lock_path.is_symlink() or not stat.S_ISREG(metadata.st_mode):
        raise ValueError("checkpoint lock is not a regular file")
    descriptor = os.open(lock_path, os.O_RDWR)
    opened_metadata = os.fstat(descriptor)
    if (
        metadata.st_dev,
        metadata.st_ino,
        stat.S_IFMT(metadata.st_mode),
    ) != (
        opened_metadata.st_dev,
        opened_metadata.st_ino,
        stat.S_IFMT(opened_metadata.st_mode),
    ):
        os.close(descriptor)
        raise ValueError("checkpoint lock changed while opening")
    with os.fdopen(descriptor, "r+b") as handle:
        try:
            os.fchmod(handle.fileno(), stat.S_IRUSR | stat.S_IWUSR)
        except (AttributeError, OSError):
            pass
        if os.name == "nt":
            import msvcrt

            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _publication_footer(run_id: str, source_digest: str) -> bytes:
    return (
        "\n\n## Publication provenance\n\n"
        f"- Run ID: `{run_id}`\n"
        f"- Source report SHA-256: `{source_digest}`\n"
    ).encode("utf-8")


def prepare(
    report: Path,
    title: str,
    state_path: Path,
    payload_path: Path,
    *,
    delivery_binding: dict[str, str],
) -> dict[str, Any]:
    _ensure_regular_file(report)
    if not title.strip():
        raise ValueError("title must not be blank")
    report = report.resolve()
    state_path = _anchored_path(state_path)
    payload_path = _anchored_path(payload_path)
    if len({report, state_path, payload_path}) != 3:
        raise ValueError("report, state, and payload paths must be different")
    with _state_lock(state_path):
        if state_path.exists() or payload_path.exists():
            raise FileExistsError("checkpoint or publication payload already exists")

        source = report.read_bytes()
        source_digest = sha256_bytes(source)
        run_id = str(uuid.uuid4())
        separator = b"" if source.endswith(b"\n") else b"\n"
        publication = source + separator + _publication_footer(run_id, source_digest)
        publication_digest = sha256_bytes(publication)

        _write_atomic(payload_path, publication, replace=False)
        checkpoint: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "state": "prepared",
            "run_id": run_id,
            "title": title.strip(),
            "source_report": str(report),
            "source_sha256": source_digest,
            "publication_payload": str(payload_path),
            "publication_sha256": publication_digest,
            "prepared_at": utc_now(),
            "attempt_count": 0,
            "reconciliation_count": 0,
            "document_id": None,
            "document_url": None,
            "delivery_verified": False,
            "delivery_binding": delivery_binding,
        }
        try:
            _write_json(state_path, checkpoint, replace=False)
        except Exception:
            payload_path.unlink(missing_ok=True)
            raise
        return checkpoint


def begin_create(
    state_path: Path,
    *,
    delivery_binding: dict[str, str],
) -> dict[str, Any]:
    with _state_lock(state_path):
        checkpoint = _read_state(state_path)
        if checkpoint["state"] != "prepared" or checkpoint.get("document_id") is not None:
            raise ValueError("only a prepared publication may begin create")
        if checkpoint["delivery_binding"] != delivery_binding:
            raise ValueError("delivery binding changed since publication preparation")
        publication_payload = _anchored_path(
            Path(checkpoint["publication_payload"])
        )
        _ensure_regular_file(publication_payload)
        if sha256_file(publication_payload) != checkpoint["publication_sha256"]:
            raise ValueError("publication payload changed after preparation")
        checkpoint["state"] = "create_in_flight"
        checkpoint["create_started_at"] = utc_now()
        checkpoint["attempt_count"] = int(checkpoint.get("attempt_count", 0)) + 1
        _write_json(state_path, checkpoint, replace=True)
        return checkpoint


def mark_unknown(state_path: Path, reason: str) -> dict[str, Any]:
    if reason not in UNKNOWN_REASONS:
        raise ValueError("unknown_reason must be one of the fixed safe reason codes")
    with _state_lock(state_path):
        checkpoint = _read_state(state_path)
        if (
            checkpoint["state"] != "create_in_flight"
            or checkpoint.get("document_id") is not None
        ):
            raise ValueError("only an in-flight create without a document ID may become outcome_unknown")
        checkpoint["state"] = "outcome_unknown"
        checkpoint["unknown_at"] = utc_now()
        checkpoint["unknown_reason"] = reason
        _write_json(state_path, checkpoint, replace=True)
        return checkpoint


def abort_before_send(state_path: Path, reason: str) -> dict[str, Any]:
    if reason not in ABORT_BEFORE_SEND_REASONS:
        raise ValueError("abort_reason must be one of the fixed safe reason codes")
    with _state_lock(state_path):
        checkpoint = _read_state(state_path)
        if (
            checkpoint["state"] != "create_in_flight"
            or checkpoint.get("document_id") is not None
        ):
            raise ValueError("only an in-flight create proven unsent may be aborted")
        checkpoint["state"] = "prepared"
        checkpoint["aborted_before_send_at"] = utc_now()
        checkpoint["abort_before_send_reason"] = reason
        _write_json(state_path, checkpoint, replace=True)
        return checkpoint


def confirm_no_match_and_retry(
    state_path: Path,
    *,
    user_confirmed_no_match: bool,
) -> dict[str, Any]:
    if not user_confirmed_no_match:
        raise ValueError("explicit user confirmation of no matching document is required")
    with _state_lock(state_path):
        checkpoint = _read_state(state_path)
        if (
            checkpoint["state"] != "outcome_unknown"
            or checkpoint.get("document_id") is not None
        ):
            raise ValueError("only a reconciled outcome_unknown publication may retry")
        checkpoint["state"] = "prepared"
        checkpoint["retry_authorized_at"] = utc_now()
        checkpoint["retry_confirmation"] = "user_confirmed_no_match"
        checkpoint["reconciliation_count"] = (
            int(checkpoint.get("reconciliation_count", 0)) + 1
        )
        _write_json(state_path, checkpoint, replace=True)
        return checkpoint


def record_created(
    state_path: Path,
    document_id: str,
    document_url: str | None,
) -> dict[str, Any]:
    if not DOCUMENT_ID_RE.fullmatch(document_id):
        raise ValueError("invalid document_id")
    if document_url:
        if _validate_document_url(document_url) != document_id:
            raise ValueError("document_url does not match document_id")

    with _state_lock(state_path):
        checkpoint = _read_state(state_path)
        existing_document_id = checkpoint.get("document_id")
        if existing_document_id is not None:
            if existing_document_id != document_id:
                raise ValueError("refusing to replace an existing document_id")
            if checkpoint["state"] in {"created", "verified"}:
                return checkpoint
            raise ValueError("checkpoint has a document ID in an invalid state")
        if checkpoint["state"] not in {"create_in_flight", "outcome_unknown"}:
            raise ValueError("begin create before recording a document")
        checkpoint["state"] = "created"
        checkpoint["document_id"] = document_id
        checkpoint["document_url"] = document_url
        checkpoint["created_at"] = utc_now()
        checkpoint.pop("unknown_reason", None)
        _write_json(state_path, checkpoint, replace=True)
        return checkpoint


def record_verified(state_path: Path) -> dict[str, Any]:
    with _state_lock(state_path):
        checkpoint = _read_state(state_path)
        if checkpoint["state"] != "created" or not checkpoint.get("document_id"):
            raise ValueError("record a created document before marking it verified")
        checkpoint["state"] = "verified"
        checkpoint["delivery_verified"] = True
        checkpoint["verified_at"] = utc_now()
        _write_json(state_path, checkpoint, replace=True)
        return checkpoint


def _safe_summary(checkpoint: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "schema_version",
        "state",
        "run_id",
        "title",
        "source_sha256",
        "publication_sha256",
        "document_id",
        "document_url",
        "delivery_verified",
        "delivery_binding",
        "attempt_count",
        "reconciliation_count",
        "prepared_at",
        "create_started_at",
        "aborted_before_send_at",
        "abort_before_send_reason",
        "retry_authorized_at",
        "retry_confirmation",
        "created_at",
        "verified_at",
        "unknown_at",
        "unknown_reason",
    )
    return {key: checkpoint[key] for key in keys if key in checkpoint}


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="feishu-publication-test-") as directory:
        root = Path(directory).resolve(strict=True)
        report = root / "report.md"
        report.write_text("# Report\n\nEvidence.\n", encoding="utf-8")
        state = root / "publication.json"
        payload = root / "publication.md"
        connector_binding = _delivery_binding(
            delivery_route="connector",
            connector_id="self-test-connector",
            connector_identity_sha256="1" * 64,
            verify_executable=True,
        )
        prepared = prepare(
            report,
            "Recent papers",
            state,
            payload,
            delivery_binding=connector_binding,
        )
        assert prepared["state"] == "prepared"
        assert RUN_ID_RE.fullmatch(prepared["run_id"])
        body = payload.read_text(encoding="utf-8")
        assert prepared["run_id"] in body
        assert prepared["source_sha256"] in body
        assert sha256_bytes(payload.read_bytes()) == prepared["publication_sha256"]

        in_flight = begin_create(state, delivery_binding=connector_binding)
        assert in_flight["state"] == "create_in_flight"
        unknown = mark_unknown(state, "timeout_after_send")
        assert unknown["state"] == "outcome_unknown"
        retryable = confirm_no_match_and_retry(
            state,
            user_confirmed_no_match=True,
        )
        assert retryable["state"] == "prepared"
        assert retryable["reconciliation_count"] == 1
        assert begin_create(
            state,
            delivery_binding=connector_binding,
        )["attempt_count"] == 2
        created = record_created(
            state,
            "doxcnExample123",
            "https://example.feishu.cn/docx/doxcnExample123",
        )
        assert created["state"] == "created"
        assert record_created(
            state,
            "doxcnExample123",
            "https://example.feishu.cn/docx/doxcnExample123",
        )["document_id"] == "doxcnExample123"
        try:
            record_created(state, "doxcnDifferent456", None)
        except ValueError:
            pass
        else:
            raise AssertionError("a recorded document ID must never be replaced")
        try:
            mark_unknown(state, "timeout_after_send")
        except ValueError:
            pass
        else:
            raise AssertionError("created must never regress to outcome_unknown")
        verified = record_verified(state)
        assert verified["delivery_verified"] is True
        try:
            prepare(
                report,
                "Duplicate",
                state,
                root / "second.md",
                delivery_binding=connector_binding,
            )
        except FileExistsError:
            pass
        else:
            raise AssertionError("prepare must not replace an existing checkpoint")

        abort_state = root / "abort.json"
        abort_payload = root / "abort.md"
        prepare(
            report,
            "Abort before send",
            abort_state,
            abort_payload,
            delivery_binding=connector_binding,
        )
        begin_create(abort_state, delivery_binding=connector_binding)
        aborted = abort_before_send(abort_state, "local_argument_validation_failed")
        assert aborted["state"] == "prepared"
        assert begin_create(
            abort_state,
            delivery_binding=connector_binding,
        )["attempt_count"] == 2

        url_state = root / "url.json"
        url_payload = root / "url.md"
        prepare(
            report,
            "URL validation",
            url_state,
            url_payload,
            delivery_binding=connector_binding,
        )
        begin_create(url_state, delivery_binding=connector_binding)
        try:
            record_created(
                url_state,
                "doxcnExample123",
                "https://example.feishu.cn/docx/doxcnExample123?token=secret",
            )
        except ValueError:
            pass
        else:
            raise AssertionError("document URLs with query strings must be rejected")
        lark_created = record_created(
            url_state,
            "doxcnExample123",
            "https://example.larkoffice.com/docx/doxcnExample123",
        )
        assert lark_created["state"] == "created"

        concurrent_state = root / "concurrent.json"
        concurrent_payload = root / "concurrent.md"
        barrier = threading.Barrier(2)
        outcomes: list[str] = []

        def concurrent_prepare() -> None:
            barrier.wait()
            try:
                prepare(
                    report,
                    "Concurrent create",
                    concurrent_state,
                    concurrent_payload,
                    delivery_binding=connector_binding,
                )
            except FileExistsError:
                outcomes.append("conflict")
            else:
                outcomes.append("created")

        threads = [threading.Thread(target=concurrent_prepare) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        assert sorted(outcomes) == ["conflict", "created"]

        integrity_state = root / "integrity.json"
        integrity_payload = root / "integrity.md"
        prepare(
            report,
            "Integrity binding",
            integrity_state,
            integrity_payload,
            delivery_binding=connector_binding,
        )
        integrity_payload.write_text("tampered", encoding="utf-8")
        try:
            begin_create(
                integrity_state,
                delivery_binding=connector_binding,
            )
        except ValueError:
            pass
        else:
            raise AssertionError("tampered publication payload must block create")

        cli_executable = root / ("lark-cli.exe" if os.name == "nt" else "lark-cli")
        cli_executable.write_bytes(b"pinned executable")
        with contextlib.suppress(OSError):
            cli_executable.chmod(0o700)
        cli_binding = _delivery_binding(
            delivery_route="lark-cli",
            lark_cli_path=str(cli_executable),
            executable_sha256=sha256_file(cli_executable),
            profile="codex-paper-reading",
            brand="feishu",
            app_id_sha256="2" * 64,
            user_open_id_sha256="3" * 64,
            config_dir=str(root),
            verify_executable=True,
        )
        binding_state = root / "binding.json"
        binding_payload = root / "binding.md"
        prepare(
            report,
            "Bound identity",
            binding_state,
            binding_payload,
            delivery_binding=cli_binding,
        )
        config_only_state = root / "config-only.json"
        config_only_payload = root / "config-only.md"
        prepare(
            report,
            "Existing profile binding",
            config_only_state,
            config_only_payload,
            delivery_binding=cli_binding,
        )
        config_only_in_flight = begin_create(
            config_only_state,
            delivery_binding=cli_binding,
        )
        assert config_only_in_flight["state"] == "create_in_flight"
        assert config_only_in_flight["delivery_binding"]["data_dir"] == ""
        changed_binding = {
            **cli_binding,
            "profile": "different-profile",
        }
        try:
            begin_create(binding_state, delivery_binding=changed_binding)
        except ValueError:
            pass
        else:
            raise AssertionError("changed profile binding must block create")
        alternate_config_dir = root / "alternate-config"
        alternate_config_dir.mkdir()
        changed_config_binding = {
            **cli_binding,
            "config_dir": str(alternate_config_dir),
        }
        try:
            begin_create(
                binding_state,
                delivery_binding=changed_config_binding,
            )
        except ValueError:
            pass
        else:
            raise AssertionError("changed config-dir binding must block create")
        cli_executable.write_bytes(b"replaced executable")
        try:
            begin_create(
                binding_state,
                delivery_binding=_delivery_binding(
                    delivery_route="lark-cli",
                    lark_cli_path=str(cli_executable),
                    executable_sha256=cli_binding["executable_sha256"],
                    profile=cli_binding["profile"],
                    brand=cli_binding["brand"],
                    app_id_sha256=cli_binding["app_id_sha256"],
                    user_open_id_sha256=cli_binding["user_open_id_sha256"],
                    config_dir=cli_binding["config_dir"],
                    verify_executable=True,
                ),
            )
        except ValueError:
            pass
        else:
            raise AssertionError("replaced executable must block create")

        symlink_target = root / "symlink-target.txt"
        symlink_target.write_bytes(b"must remain unchanged")
        symlink_path = root / "atomic-link.json"
        try:
            symlink_path.symlink_to(symlink_target)
        except OSError:
            pass
        else:
            _write_atomic(symlink_path, b"replacement entry\n", replace=True)
            assert symlink_target.read_bytes() == b"must remain unchanged"
            assert not symlink_path.is_symlink()
            assert symlink_path.read_bytes() == b"replacement entry\n"

        lock_state = root / "lock-symlink.json"
        lock_target = root / "lock-target.txt"
        lock_target.write_bytes(b"must remain unchanged")
        lock_path = root / ".lock-symlink.json.lock"
        try:
            lock_path.symlink_to(lock_target)
        except OSError:
            pass
        else:
            try:
                with _state_lock(lock_state):
                    raise AssertionError("symlinked lock must not be entered")
            except ValueError:
                pass
            assert lock_target.read_bytes() == b"must remain unchanged"


def _add_binding_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--delivery-route",
        choices=sorted(DELIVERY_ROUTES),
        required=True,
    )
    parser.add_argument("--lark-cli")
    parser.add_argument("--approved-executable-sha256")
    parser.add_argument("--profile")
    parser.add_argument("--brand", choices=("feishu", "lark"))
    parser.add_argument("--app-id-sha256")
    parser.add_argument("--user-open-id-sha256")
    parser.add_argument("--config-dir")
    parser.add_argument("--data-dir")
    parser.add_argument("--connector-id")
    parser.add_argument("--connector-identity-sha256")


def _binding_from_args(args: argparse.Namespace) -> dict[str, str]:
    return _delivery_binding(
        delivery_route=args.delivery_route,
        lark_cli_path=args.lark_cli,
        executable_sha256=args.approved_executable_sha256,
        profile=args.profile,
        brand=args.brand,
        app_id_sha256=args.app_id_sha256,
        user_open_id_sha256=args.user_open_id_sha256,
        config_dir=args.config_dir,
        data_dir=args.data_dir,
        connector_id=args.connector_id,
        connector_identity_sha256=args.connector_identity_sha256,
        verify_executable=True,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare and atomically advance a credential-free Feishu publication "
            "checkpoint. This script never calls Feishu."
        )
    )
    parser.add_argument("--self-test", action="store_true")
    subparsers = parser.add_subparsers(dest="command")

    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("--report", type=Path, required=True)
    prepare_parser.add_argument("--title", required=True)
    prepare_parser.add_argument("--state", type=Path, required=True)
    prepare_parser.add_argument("--payload", type=Path, required=True)
    _add_binding_arguments(prepare_parser)

    unknown_parser = subparsers.add_parser("mark-unknown")
    unknown_parser.add_argument("--state", type=Path, required=True)
    unknown_parser.add_argument(
        "--reason",
        choices=sorted(UNKNOWN_REASONS),
        default="create_outcome_ambiguous",
    )

    begin_parser = subparsers.add_parser("begin-create")
    begin_parser.add_argument("--state", type=Path, required=True)
    _add_binding_arguments(begin_parser)

    abort_parser = subparsers.add_parser("abort-before-send")
    abort_parser.add_argument("--state", type=Path, required=True)
    abort_parser.add_argument(
        "--reason",
        choices=sorted(ABORT_BEFORE_SEND_REASONS),
        required=True,
    )

    retry_parser = subparsers.add_parser("confirm-no-match-and-retry")
    retry_parser.add_argument("--state", type=Path, required=True)
    retry_parser.add_argument(
        "--user-confirmed-no-match",
        action="store_true",
        help="attest that the user checked Feishu and explicitly approved retry",
    )

    created_parser = subparsers.add_parser("record-created")
    created_parser.add_argument("--state", type=Path, required=True)
    created_parser.add_argument("--document-id", required=True)
    created_parser.add_argument("--document-url")

    verified_parser = subparsers.add_parser("record-verified")
    verified_parser.add_argument("--state", type=Path, required=True)

    show_parser = subparsers.add_parser("show")
    show_parser.add_argument("--state", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.self_test:
            run_self_test()
            result: dict[str, Any] = {"self_test": "passed"}
        elif args.command == "prepare":
            result = _safe_summary(
                prepare(
                    args.report,
                    args.title,
                    args.state,
                    args.payload,
                    delivery_binding=_binding_from_args(args),
                )
            )
        elif args.command == "mark-unknown":
            result = _safe_summary(mark_unknown(args.state, args.reason))
        elif args.command == "begin-create":
            result = _safe_summary(
                begin_create(
                    args.state,
                    delivery_binding=_binding_from_args(args),
                )
            )
        elif args.command == "abort-before-send":
            result = _safe_summary(abort_before_send(args.state, args.reason))
        elif args.command == "confirm-no-match-and-retry":
            result = _safe_summary(
                confirm_no_match_and_retry(
                    args.state,
                    user_confirmed_no_match=args.user_confirmed_no_match,
                )
            )
        elif args.command == "record-created":
            result = _safe_summary(
                record_created(args.state, args.document_id, args.document_url)
            )
        elif args.command == "record-verified":
            result = _safe_summary(record_verified(args.state))
        elif args.command == "show":
            result = _safe_summary(_read_state(args.state))
        else:
            raise ValueError("choose a command or --self-test")
    except Exception as error:
        print(
            json.dumps(
                {"ok": False, "error": type(error).__name__, "message": str(error)},
                ensure_ascii=True,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps({"ok": True, **result}, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
