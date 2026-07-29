#!/usr/bin/env python3
"""Run a bounded Feishu/Lark user authorization without exposing credentials.

The helper owns one blocking ``lark-cli auth login`` child. Child output is
treated as sensitive: stdout is parsed into a tiny safe event, stderr is
drained and discarded, and neither stream is returned or written to disk.
The child is parent-death-contained so an abruptly terminated helper cannot
leave an authorization process running.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import io
import json
import os
import queue
import re
import select
import signal
import stat
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO, Callable
from urllib.parse import unquote, urlsplit, urlunsplit

from feishu_process_environment import build_isolated_cli_environment


REQUIRED_SCOPES = "docx:document:create docx:document:readonly"
DEFAULT_TIMEOUT_SECONDS = 600.0
MAX_TIMEOUT_SECONDS = 1800.0
TERMINATION_GRACE_SECONDS = 3.0
STALE_ACTIVE_GRACE_SECONDS = 5.0
MAX_EVENT_BYTES = 256 * 1024
MAX_STATE_BYTES = 16 * 1024

STATE_FIELDS = frozenset(
    {
        "state",
        "verification_url",
        "expires_at",
        "pid",
        "started_at",
        "updated_at",
        "finished_at",
        "reason",
        "brand",
        "profile",
        "executable_sha256",
        "config_dir",
        "config_dir_identity_sha256",
        "data_dir",
        "data_dir_identity_sha256",
    }
)
TERMINAL_STATES = frozenset({"succeeded", "failed", "timed_out", "cancelled"})
ACTIVE_STATES = frozenset({"starting", "pending"})
VALID_STATES = frozenset(
    {
        *ACTIVE_STATES,
        *TERMINAL_STATES,
        "absent",
        "expired",
        "cleaned",
    }
)
VALID_REASONS = frozenset(
    {
        "login_process_starting",
        "awaiting_user_verification",
        "authorization_completed",
        "lark_cli_not_found",
        "lark_cli_path_invalid",
        "lark_cli_hash_mismatch",
        "login_launch_failed",
        "login_process_failed",
        "authorization_completion_unverified",
        "authorization_timed_out",
        "authorization_cancelled",
        "unexpected_authorization_failure",
        "state_file_conflict",
        "state_file_invalid",
        "no_state_file",
        "authorization_expired",
        "authorization_process_not_running",
        "cleanup_refused_active_authorization",
        "state_file_removed",
    }
)
REASONS_BY_STATE = {
    "starting": frozenset(
        {"login_process_starting", "cleanup_refused_active_authorization"}
    ),
    "pending": frozenset(
        {
            "awaiting_user_verification",
            "cleanup_refused_active_authorization",
        }
    ),
    "succeeded": frozenset({"authorization_completed"}),
    "failed": frozenset(
        {
            "lark_cli_not_found",
            "lark_cli_path_invalid",
            "lark_cli_hash_mismatch",
            "login_launch_failed",
            "login_process_failed",
            "authorization_completion_unverified",
            "unexpected_authorization_failure",
            "state_file_conflict",
            "state_file_invalid",
            "authorization_process_not_running",
        }
    ),
    "timed_out": frozenset({"authorization_timed_out"}),
    "cancelled": frozenset({"authorization_cancelled"}),
    "absent": frozenset({"no_state_file"}),
    "expired": frozenset({"authorization_expired"}),
    "cleaned": frozenset({"no_state_file", "state_file_removed"}),
}
OFFICIAL_HOSTS = {
    "auto": frozenset({"accounts.feishu.cn", "accounts.larksuite.com"}),
    "feishu": frozenset({"accounts.feishu.cn"}),
    "lark": frozenset({"accounts.larksuite.com"}),
}
URL_KEY_PRIORITY = (
    "verification_uri_complete",
    "verification_uri",
    "verification_url",
)
SECRET_KEY_MARKERS = (
    "token",
    "secret",
    "password",
    "cookie",
    "device_code",
    "user_code",
    "authorization",
)


@dataclass(frozen=True)
class SafeEvent:
    """The only information permitted to leave the child-output parser."""

    verification_url: str | None = None
    expires_at: float | None = None
    authorization_complete: bool = False


Emitter = Callable[[dict[str, Any]], None]
ProcessFactory = Callable[..., Any]
_UNSET = object()


@contextlib.contextmanager
def _temporary_environment(overrides: dict[str, str]):
    original = os.environ.copy()
    try:
        os.environ.update(overrides)
        yield
    finally:
        os.environ.clear()
        os.environ.update(original)


def _utc_timestamp(value: float | None = None) -> str:
    instant = dt.datetime.fromtimestamp(
        time.time() if value is None else value,
        tz=dt.timezone.utc,
    )
    return instant.isoformat(timespec="seconds").replace("+00:00", "Z")


def _parse_timestamp(value: Any) -> float | None:
    if not isinstance(value, str) or len(value) > 40:
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.timestamp()


def _normalized_key(value: Any) -> str:
    text = str(value)
    result: list[str] = []
    for index, character in enumerate(text):
        if (
            index
            and character.isupper()
            and (text[index - 1].islower() or text[index - 1].isdigit())
        ):
            result.append("_")
        result.append(character.casefold() if character.isalnum() else "_")
    return "_".join(part for part in "".join(result).split("_") if part)


def _secret_values(
    value: Any,
    *,
    include_user_code: bool = True,
    depth: int = 0,
) -> set[str]:
    if depth > 8:
        return set()
    found: set[str] = set()
    if isinstance(value, dict):
        for key, child in list(value.items())[:128]:
            normalized = _normalized_key(key)
            if (
                any(marker in normalized for marker in SECRET_KEY_MARKERS)
                or normalized == "code"
            ):
                if (
                    isinstance(child, str)
                    and child
                    and (include_user_code or normalized != "user_code")
                ):
                    found.add(child)
            else:
                found.update(
                    _secret_values(
                        child,
                        include_user_code=include_user_code,
                        depth=depth + 1,
                    )
                )
    elif isinstance(value, list):
        for child in value[:128]:
            found.update(
                _secret_values(
                    child,
                    include_user_code=include_user_code,
                    depth=depth + 1,
                )
            )
    return found


def _candidate_values(
    value: Any,
    wanted_keys: frozenset[str],
    *,
    depth: int = 0,
) -> list[Any]:
    if depth > 8:
        return []
    found: list[Any] = []
    if isinstance(value, dict):
        for key, child in list(value.items())[:128]:
            if _normalized_key(key) in wanted_keys:
                found.append(child)
            if isinstance(child, (dict, list)):
                found.extend(
                    _candidate_values(child, wanted_keys, depth=depth + 1)
                )
    elif isinstance(value, list):
        for child in value[:128]:
            found.extend(_candidate_values(child, wanted_keys, depth=depth + 1))
    return found


def _validate_verification_url(
    value: Any,
    *,
    brand: str,
    secret_values: set[str],
    allow_opaque_suffix: bool = False,
) -> str | None:
    if not isinstance(value, str) or not 1 <= len(value) <= 2048:
        return None
    if any(ord(character) < 32 for character in value):
        return None
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError:
        return None
    hostname = (parsed.hostname or "").casefold().rstrip(".")
    if (
        parsed.scheme.casefold() != "https"
        or hostname not in OFFICIAL_HOSTS[brand]
        or parsed.username is not None
        or parsed.password is not None
        or port not in {None, 443}
        or not parsed.path.startswith("/")
        or parsed.fragment
        or "\\" in parsed.path
    ):
        return None
    if not allow_opaque_suffix and parsed.query:
        return None

    decoded = unquote(value)
    for secret in secret_values:
        if len(secret) >= 3 and (secret in value or secret in decoded):
            return None

    if not allow_opaque_suffix:
        # Bare verification URLs are fixed pages. Reject opaque path
        # components that could smuggle a user code into the trusted origin.
        for component in parsed.path.split("/"):
            if len(component) > 64:
                return None
        return urlunsplit(("https", hostname, parsed.path, "", ""))

    # verification_uri_complete is defined by the official endpoint as an
    # opaque URL. Preserve it byte-for-byte after validating its origin and
    # excluding every secret except the user code embedded by that endpoint.
    return value


def _expiry_from_payload(
    payload: Any,
    *,
    now: float,
    deadline: float,
) -> float:
    candidates: list[float] = []
    for value in _candidate_values(
        payload,
        frozenset({"expires_in", "expires_at", "expiration"}),
    ):
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            numeric = float(value)
            if numeric > 10_000_000_000:
                numeric /= 1000.0
            if numeric < 10_000_000:
                numeric = now + numeric
            candidates.append(numeric)
        elif isinstance(value, str):
            parsed = _parse_timestamp(value)
            if parsed is not None:
                candidates.append(parsed)
    usable = [candidate for candidate in candidates if candidate > now]
    return min([deadline, *usable])


def _safe_event_from_payload(
    payload: Any,
    *,
    brand: str,
    now: float,
    deadline: float,
) -> SafeEvent:
    completion = _valid_completion_event(payload)
    for key in URL_KEY_PRIORITY:
        candidates = _candidate_values(payload, frozenset({key}))
        for candidate in candidates:
            complete_url = key == "verification_uri_complete"
            secrets = _secret_values(
                payload,
                include_user_code=not complete_url,
            )
            validated = _validate_verification_url(
                candidate,
                brand=brand,
                secret_values=secrets,
                allow_opaque_suffix=complete_url,
            )
            if validated is not None:
                return SafeEvent(
                    verification_url=validated,
                    expires_at=_expiry_from_payload(
                        payload,
                        now=now,
                        deadline=deadline,
                    ),
                    authorization_complete=completion,
                )
    return SafeEvent(authorization_complete=completion)


def _scope_values(payload: dict[str, Any], key: str) -> set[str] | None:
    value = payload.get(key)
    if not isinstance(value, list) or len(value) > 256:
        return None
    result: set[str] = set()
    for item in value:
        if not isinstance(item, str) or not item or len(item) > 256:
            return None
        result.add(item)
    return result


def _valid_completion_event(payload: Any) -> bool:
    if not isinstance(payload, dict):
        return False
    if payload.get("event") != "authorization_complete":
        return False
    missing = _scope_values(payload, "missing")
    requested = _scope_values(payload, "requested")
    granted = _scope_values(payload, "granted")
    required = set(REQUIRED_SCOPES.split())
    return (
        missing == set()
        and requested is not None
        and granted is not None
        and required.issubset(requested)
        and required.issubset(granted)
    )


def _read_stdout_events(
    stream: BinaryIO,
    events: queue.Queue[SafeEvent | None],
    *,
    brand: str,
    deadline: float,
) -> None:
    try:
        while True:
            raw_line = stream.readline(MAX_EVENT_BYTES + 1)
            if not raw_line:
                break
            if len(raw_line) > MAX_EVENT_BYTES:
                continue
            try:
                payload = json.loads(raw_line.decode("utf-8", errors="replace"))
            except (UnicodeError, json.JSONDecodeError, TypeError, ValueError):
                continue
            safe = _safe_event_from_payload(
                payload,
                brand=brand,
                now=time.time(),
                deadline=deadline,
            )
            if safe.verification_url is not None or safe.authorization_complete:
                events.put(safe)
    except Exception:
        pass
    finally:
        events.put(None)


def _discard_stream(stream: BinaryIO) -> None:
    try:
        while stream.read(64 * 1024):
            pass
    except Exception:
        pass


def _sanitize_state(
    payload: Any,
    *,
    brand: str = "auto",
    profile: str | None = None,
    approved_executable_sha256: str | None = None,
    config_dir: Any = _UNSET,
    config_dir_identity_sha256: Any = _UNSET,
    data_dir: Any = _UNSET,
    data_dir_identity_sha256: Any = _UNSET,
) -> dict[str, Any] | None:
    if not isinstance(payload, dict) or not set(payload).issubset(STATE_FIELDS):
        return None
    state = payload.get("state")
    reason = payload.get("reason")
    if (
        state not in VALID_STATES
        or reason not in VALID_REASONS
        or reason not in REASONS_BY_STATE[state]
    ):
        return None

    result: dict[str, Any] = {"state": state, "reason": reason}
    unbound_failure_reasons = {
        "lark_cli_not_found",
        "lark_cli_path_invalid",
        "lark_cli_hash_mismatch",
        "state_file_conflict",
        "state_file_invalid",
    }
    binding_required = (
        state in ACTIVE_STATES
        or state in {"succeeded", "timed_out", "cancelled", "expired"}
        or (state == "failed" and reason not in unbound_failure_reasons)
    )
    state_brand = payload.get("brand")
    state_profile = payload.get("profile")
    executable_sha256 = payload.get("executable_sha256")
    binding_present = (
        state_brand is not None
        and state_profile is not None
        and executable_sha256 is not None
    )
    if binding_required and not binding_present:
        return None
    if any(
        value is not None
        for value in (state_brand, state_profile, executable_sha256)
    ) and not binding_present:
        return None
    if binding_present:
        if state_brand not in {"feishu", "lark"}:
            return None
        if brand != "auto" and state_brand != brand:
            return None
        result["brand"] = state_brand
        if _validated_profile(state_profile) is None:
            return None
        if profile is not None and state_profile != profile:
            return None
        result["profile"] = state_profile
        if not isinstance(executable_sha256, str) or not re.fullmatch(
            r"[0-9a-f]{64}",
            executable_sha256,
        ):
            return None
        if (
            approved_executable_sha256 is not None
            and executable_sha256 != approved_executable_sha256.casefold()
        ):
            return None
        result["executable_sha256"] = executable_sha256
        state_config_dir = payload.get("config_dir")
        state_config_identity = payload.get("config_dir_identity_sha256")
        if state_config_dir is not None:
            normalized_state_config_dir = _normalized_config_dir(
                state_config_dir,
                must_exist=False,
            )
            if normalized_state_config_dir is None:
                return None
            result["config_dir"] = normalized_state_config_dir
            if (
                not isinstance(state_config_identity, str)
                or not re.fullmatch(r"[0-9a-f]{64}", state_config_identity)
            ):
                return None
            result["config_dir_identity_sha256"] = state_config_identity
        elif state_config_identity is not None:
            return None
        if config_dir is not _UNSET and config_dir is not None:
            normalized_expected_config_dir = _normalized_config_dir(
                config_dir,
                must_exist=False,
            )
            if (
                normalized_expected_config_dir is None
                or state_config_dir != normalized_expected_config_dir
            ):
                return None
        elif config_dir is None and state_config_dir is not None:
            return None
        if config_dir_identity_sha256 is not _UNSET:
            if config_dir_identity_sha256 is None:
                if state_config_identity is not None:
                    return None
            elif state_config_identity != config_dir_identity_sha256:
                return None
        state_data_dir = payload.get("data_dir")
        state_data_identity = payload.get("data_dir_identity_sha256")
        if state_data_dir is not None:
            if state_config_dir is None:
                return None
            normalized_state_data_dir = _normalized_config_dir(
                state_data_dir,
                must_exist=False,
            )
            if normalized_state_data_dir is None:
                return None
            if (
                not isinstance(state_data_identity, str)
                or not re.fullmatch(r"[0-9a-f]{64}", state_data_identity)
            ):
                return None
            result["data_dir"] = normalized_state_data_dir
            result["data_dir_identity_sha256"] = state_data_identity
        elif state_data_identity is not None:
            return None
        if data_dir is not _UNSET and data_dir is not None:
            normalized_expected_data_dir = _normalized_config_dir(
                data_dir,
                must_exist=False,
            )
            if (
                normalized_expected_data_dir is None
                or state_data_dir != normalized_expected_data_dir
            ):
                return None
        elif data_dir is None and state_data_dir is not None:
            return None
        if data_dir_identity_sha256 is not _UNSET:
            if data_dir_identity_sha256 is None:
                if state_data_identity is not None:
                    return None
            elif state_data_identity != data_dir_identity_sha256:
                return None
    for field in ("started_at", "updated_at", "finished_at", "expires_at"):
        if field in payload:
            if _parse_timestamp(payload[field]) is None:
                return None
            result[field] = payload[field]
    if "pid" in payload:
        pid = payload["pid"]
        if isinstance(pid, bool) or not isinstance(pid, int) or not 0 < pid < 2**63:
            return None
        result["pid"] = pid
    if "verification_url" in payload:
        if state != "pending":
            return None
        validated = _validate_verification_url(
            payload["verification_url"],
            brand=brand,
            secret_values=set(),
            allow_opaque_suffix=True,
        )
        if validated is None:
            return None
        result["verification_url"] = validated
    if state in TERMINAL_STATES and "verification_url" in result:
        return None
    return result


def _state_bytes(payload: dict[str, Any]) -> bytes:
    sanitized = _sanitize_state(payload)
    if sanitized is None:
        raise ValueError("invalid safe state")
    return (
        json.dumps(
            sanitized,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def _write_initial_state(path: Path, payload: dict[str, Any]) -> None:
    data = _state_bytes(payload)
    descriptor = os.open(
        path,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL,
        0o600,
    )
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        with contextlib.suppress(OSError):
            path.unlink()
        raise


def _replace_state(path: Path, payload: dict[str, Any]) -> None:
    data = _state_bytes(payload)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            with contextlib.suppress(OSError):
                os.chmod(temporary, 0o600)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        with contextlib.suppress(OSError):
            temporary.unlink()


def _read_state(
    path: Path,
    *,
    brand: str = "auto",
    profile: str | None = None,
    approved_executable_sha256: str | None = None,
    config_dir: Any = _UNSET,
    config_dir_identity_sha256: Any = _UNSET,
    data_dir: Any = _UNSET,
    data_dir_identity_sha256: Any = _UNSET,
) -> dict[str, Any] | None:
    try:
        metadata = path.lstat()
        if path.is_symlink() or not stat.S_ISREG(metadata.st_mode):
            return None
        if metadata.st_size > MAX_STATE_BYTES:
            return None
        with path.open("rb") as handle:
            data = handle.read(MAX_STATE_BYTES + 1)
        if len(data) > MAX_STATE_BYTES:
            return None
        payload = json.loads(data.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    return _sanitize_state(
        payload,
        brand=brand,
        profile=profile,
        approved_executable_sha256=approved_executable_sha256,
        config_dir=config_dir,
        config_dir_identity_sha256=config_dir_identity_sha256,
        data_dir=data_dir,
        data_dir_identity_sha256=data_dir_identity_sha256,
    )


def _emit_json(payload: dict[str, Any]) -> None:
    safe = _sanitize_state(payload)
    if safe is None:
        safe = {
            "state": "failed",
            "reason": "unexpected_authorization_failure",
            "updated_at": _utc_timestamp(),
        }
    print(json.dumps(safe, ensure_ascii=True, sort_keys=True), flush=True)


def _command_for(
    executable: str,
    profile: str,
) -> list[str]:
    return [
        executable,
        "--profile",
        profile,
        "auth",
        "login",
        "--scope",
        REQUIRED_SCOPES,
        "--json",
    ]


def _validated_executable(
    value: str | None,
) -> str | None:
    if not value:
        return None
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        return None
    try:
        metadata = candidate.lstat()
        if not stat.S_ISREG(metadata.st_mode) or candidate.is_symlink():
            return None
        suffix = candidate.suffix.casefold()
        if suffix in {".bat", ".cmd", ".ps1"}:
            return None
        if os.name == "nt" and suffix != ".exe":
            return None
        if os.name != "nt" and not os.access(candidate, os.X_OK):
            return None
    except OSError:
        return None
    return os.fspath(candidate)


def _validated_profile(value: Any) -> str | None:
    if not isinstance(value, str) or not value or value != value.strip():
        return None
    if len(value) > 128 or any(ord(character) < 32 for character in value):
        return None
    return value


def _normalized_config_dir(
    value: Any,
    *,
    must_exist: bool,
) -> str | None:
    if not isinstance(value, str) or not value or value != value.strip():
        return None
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        return None
    absolute = Path(os.path.abspath(os.fspath(candidate)))
    if must_exist:
        try:
            metadata = absolute.lstat()
        except OSError:
            return None
        reparse_point = bool(
            getattr(metadata, "st_file_attributes", 0) & 0x400
        )
        if (
            absolute.is_symlink()
            or reparse_point
            or not stat.S_ISDIR(metadata.st_mode)
        ):
            return None
        try:
            resolved = absolute.resolve(strict=True)
        except OSError:
            return None
        if os.path.normcase(os.fspath(resolved)) != os.path.normcase(
            os.fspath(absolute)
        ):
            return None
        return os.fspath(resolved)
    return os.fspath(absolute)


def _config_dir_identity(config_dir: str) -> str | None:
    normalized = _normalized_config_dir(config_dir, must_exist=True)
    if normalized is None:
        return None
    try:
        metadata = Path(normalized).lstat()
    except OSError:
        return None
    material = "\0".join(
        (
            os.path.normcase(normalized),
            str(metadata.st_dev),
            str(metadata.st_ino),
            str(stat.S_IFMT(metadata.st_mode)),
        )
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def _sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class _WindowsJob:
    def __init__(self, handle: int, close_handle: Callable[[int], Any]) -> None:
        self._handle = handle
        self._close_handle = close_handle

    def close(self) -> None:
        if self._handle:
            self._close_handle(self._handle)
            self._handle = 0


class _PosixProcess:
    def __init__(self, pid: int, stdout_fd: int, stderr_fd: int) -> None:
        self.pid = pid
        self.stdout = os.fdopen(stdout_fd, "rb", buffering=0)
        self.stderr = os.fdopen(stderr_fd, "rb", buffering=0)
        self._returncode: int | None = None

    @staticmethod
    def _decode_status(status_value: int) -> int:
        return os.waitstatus_to_exitcode(status_value)

    def poll(self) -> int | None:
        if self._returncode is not None:
            return self._returncode
        try:
            waited_pid, status_value = os.waitpid(self.pid, os.WNOHANG)
        except ChildProcessError:
            return self._returncode
        if waited_pid == self.pid:
            self._returncode = self._decode_status(status_value)
        return self._returncode

    def wait(self, timeout: float | None = None) -> int:
        deadline = None if timeout is None else time.time() + timeout
        while True:
            returncode = self.poll()
            if returncode is not None:
                return returncode
            if deadline is not None and time.time() >= deadline:
                raise subprocess.TimeoutExpired(["contained-lark-cli"], timeout)
            time.sleep(0.05)

    def _signal_group(self, signal_value: int) -> None:
        with contextlib.suppress(ProcessLookupError):
            os.killpg(self.pid, signal_value)
            return
        with contextlib.suppress(ProcessLookupError):
            os.kill(self.pid, signal_value)

    def terminate(self) -> None:
        self._signal_group(signal.SIGTERM)

    def kill(self) -> None:
        self._signal_group(signal.SIGKILL)


class _PosixWatchdog:
    def __init__(self, control_fd: int, watchdog_pid: int) -> None:
        self._control_fd = control_fd
        self._watchdog_pid = watchdog_pid

    def close(self) -> None:
        if self._control_fd >= 0:
            with contextlib.suppress(OSError):
                os.write(self._control_fd, b"D")
            with contextlib.suppress(OSError):
                os.close(self._control_fd)
            self._control_fd = -1
        if self._watchdog_pid:
            deadline = time.time() + 2.0
            while time.time() < deadline:
                try:
                    waited, _ = os.waitpid(self._watchdog_pid, os.WNOHANG)
                except ChildProcessError:
                    waited = self._watchdog_pid
                if waited == self._watchdog_pid:
                    self._watchdog_pid = 0
                    break
                time.sleep(0.05)


def _kill_posix_group(pid: int) -> None:
    with contextlib.suppress(ProcessLookupError):
        os.killpg(pid, signal.SIGTERM)
    deadline = time.time() + TERMINATION_GRACE_SECONDS
    while time.time() < deadline:
        if not _pid_is_alive(pid):
            return
        time.sleep(0.05)
    with contextlib.suppress(ProcessLookupError):
        os.killpg(pid, signal.SIGKILL)


def _start_posix_contained(
    command: list[str],
    process_kwargs: dict[str, Any],
) -> tuple[_PosixProcess, _PosixWatchdog]:
    environment = process_kwargs.get("env")
    if environment is None:
        environment = os.environ.copy()
    if not isinstance(environment, dict) or not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in environment.items()
    ):
        raise ValueError("contained process environment must contain strings")
    working_directory = process_kwargs.get("cwd")
    if working_directory is not None:
        working_directory = os.fspath(working_directory)
    stdout_read, stdout_write = os.pipe()
    stderr_read, stderr_write = os.pipe()
    gate_read, gate_write = os.pipe()
    control_read, control_write = os.pipe()
    ready_read, ready_write = os.pipe()
    parent_pid = os.getpid()
    child_pid = os.fork()
    if child_pid == 0:
        try:
            for descriptor in (
                stdout_read,
                stderr_read,
                gate_write,
                control_read,
                control_write,
                ready_read,
                ready_write,
            ):
                os.close(descriptor)
            os.setsid()
            if os.read(gate_read, 1) != b"G" or os.getppid() != parent_pid:
                os._exit(125)
            os.close(gate_read)
            devnull = os.open(os.devnull, os.O_RDONLY)
            os.dup2(devnull, 0)
            os.dup2(stdout_write, 1)
            os.dup2(stderr_write, 2)
            for descriptor in (devnull, stdout_write, stderr_write):
                if descriptor > 2:
                    os.close(descriptor)
            if working_directory is not None:
                os.chdir(working_directory)
            os.execve(command[0], command, environment)
        except BaseException:
            os._exit(126)

    watchdog_pid = 0
    try:
        watchdog_pid = os.fork()
        if watchdog_pid == 0:
            try:
                for descriptor in (
                    stdout_read,
                    stdout_write,
                    stderr_read,
                    stderr_write,
                    gate_read,
                    gate_write,
                    control_write,
                    ready_read,
                ):
                    os.close(descriptor)
                os.write(ready_write, b"R")
                os.close(ready_write)
                while True:
                    readable, _, _ = select.select([control_read], [], [], 0.2)
                    if readable:
                        value = os.read(control_read, 1)
                        if value == b"D":
                            os._exit(0)
                        if value == b"":
                            _kill_posix_group(child_pid)
                            os._exit(0)
                    if os.getppid() != parent_pid:
                        _kill_posix_group(child_pid)
                        os._exit(0)
            except BaseException:
                _kill_posix_group(child_pid)
                os._exit(1)

        for descriptor in (
            stdout_write,
            stderr_write,
            gate_read,
            control_read,
            ready_write,
        ):
            os.close(descriptor)
        readable, _, _ = select.select([ready_read], [], [], 5.0)
        if not readable or os.read(ready_read, 1) != b"R":
            raise RuntimeError("authorization watchdog did not become ready")
        os.close(ready_read)
        os.write(gate_write, b"G")
        os.close(gate_write)
        return (
            _PosixProcess(child_pid, stdout_read, stderr_read),
            _PosixWatchdog(control_write, watchdog_pid),
        )
    except BaseException:
        for descriptor in (
            stdout_read,
            stdout_write,
            stderr_read,
            stderr_write,
            gate_read,
            gate_write,
            control_read,
            control_write,
            ready_read,
            ready_write,
        ):
            with contextlib.suppress(OSError):
                os.close(descriptor)
        with contextlib.suppress(ProcessLookupError):
            os.kill(child_pid, signal.SIGKILL)
        if watchdog_pid:
            with contextlib.suppress(ProcessLookupError):
                os.kill(watchdog_pid, signal.SIGKILL)
        raise


def _start_windows_contained(
    command: list[str],
    process_kwargs: dict[str, Any],
) -> tuple[Any, _WindowsJob]:
    import ctypes
    from ctypes import wintypes

    class IO_COUNTERS(ctypes.Structure):
        _fields_ = [
            ("ReadOperationCount", ctypes.c_ulonglong),
            ("WriteOperationCount", ctypes.c_ulonglong),
            ("OtherOperationCount", ctypes.c_ulonglong),
            ("ReadTransferCount", ctypes.c_ulonglong),
            ("WriteTransferCount", ctypes.c_ulonglong),
            ("OtherTransferCount", ctypes.c_ulonglong),
        ]

    class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_longlong),
            ("PerJobUserTimeLimit", ctypes.c_longlong),
            ("LimitFlags", wintypes.DWORD),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", wintypes.DWORD),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", wintypes.DWORD),
            ("SchedulingClass", wintypes.DWORD),
        ]

    class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
            ("IoInfo", IO_COUNTERS),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    ntdll = ctypes.WinDLL("ntdll", use_last_error=True)
    kernel32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    kernel32.CreateJobObjectW.restype = wintypes.HANDLE
    kernel32.SetInformationJobObject.argtypes = [
        wintypes.HANDLE,
        ctypes.c_int,
        ctypes.c_void_p,
        wintypes.DWORD,
    ]
    kernel32.SetInformationJobObject.restype = wintypes.BOOL
    kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
    ntdll.NtResumeProcess.argtypes = [wintypes.HANDLE]
    ntdll.NtResumeProcess.restype = ctypes.c_long

    job_handle = kernel32.CreateJobObjectW(None, None)
    if not job_handle:
        raise OSError("could not create authorization containment job")
    job = _WindowsJob(int(job_handle), kernel32.CloseHandle)
    process: Any | None = None
    try:
        information = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        information.BasicLimitInformation.LimitFlags = 0x00002000
        if not kernel32.SetInformationJobObject(
            job_handle,
            9,
            ctypes.byref(information),
            ctypes.sizeof(information),
        ):
            raise OSError("could not configure authorization containment job")
        process = subprocess.Popen(
            command,
            creationflags=0x00000004,
            **process_kwargs,
        )
        process_handle = wintypes.HANDLE(int(process._handle))
        if not kernel32.AssignProcessToJobObject(job_handle, process_handle):
            raise OSError("could not bind authorization process to containment job")
        if ntdll.NtResumeProcess(process_handle) != 0:
            raise OSError("could not resume contained authorization process")
        return process, job
    except BaseException:
        if process is not None:
            with contextlib.suppress(Exception):
                process.kill()
        job.close()
        raise


def _start_contained_process(
    command: list[str],
    *,
    process_factory: ProcessFactory,
    process_kwargs: dict[str, Any],
) -> tuple[Any, Any | None]:
    if process_factory is not subprocess.Popen:
        return process_factory(command, **process_kwargs), None
    if os.name == "nt":
        return _start_windows_contained(command, process_kwargs)
    return _start_posix_contained(command, process_kwargs)


def _terminate_owned_child(process: Any) -> None:
    if process.poll() is not None:
        return
    with contextlib.suppress(Exception):
        process.terminate()
    try:
        process.wait(timeout=TERMINATION_GRACE_SECONDS)
        return
    except Exception:
        pass
    if process.poll() is None:
        with contextlib.suppress(Exception):
            process.kill()
        with contextlib.suppress(Exception):
            process.wait(timeout=TERMINATION_GRACE_SECONDS)


def _pid_is_alive(pid: int) -> bool:
    """Check liveness without sending a signal or taking process ownership."""

    if os.name == "nt":
        try:
            import ctypes
            from ctypes import wintypes

            process_query_limited_information = 0x1000
            still_active = 259
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel32.OpenProcess.argtypes = [
                wintypes.DWORD,
                wintypes.BOOL,
                wintypes.DWORD,
            ]
            kernel32.OpenProcess.restype = wintypes.HANDLE
            kernel32.GetExitCodeProcess.argtypes = [
                wintypes.HANDLE,
                ctypes.POINTER(wintypes.DWORD),
            ]
            kernel32.GetExitCodeProcess.restype = wintypes.BOOL
            kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
            kernel32.CloseHandle.restype = wintypes.BOOL
            handle = kernel32.OpenProcess(
                process_query_limited_information,
                False,
                pid,
            )
            if not handle:
                # ERROR_INVALID_PARAMETER is the documented result for a PID
                # that does not exist. Access-denied and other failures are
                # indeterminate, so callers that gate cleanup must fail closed.
                return ctypes.get_last_error() != 87
            try:
                exit_code = wintypes.DWORD()
                if not kernel32.GetExitCodeProcess(
                    handle,
                    ctypes.byref(exit_code),
                ):
                    return True
                return exit_code.value == still_active
            finally:
                kernel32.CloseHandle(handle)
        except Exception:
            return True
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except (OSError, PermissionError):
        return True
    return True


def _terminal_state(
    *,
    state: str,
    reason: str,
    pid: int | None,
    started_at: str,
    binding: dict[str, str] | None = None,
) -> dict[str, Any]:
    now = _utc_timestamp()
    result: dict[str, Any] = {
        "state": state,
        "reason": reason,
        "started_at": started_at,
        "updated_at": now,
        "finished_at": now,
    }
    if pid is not None:
        result["pid"] = pid
    if binding is not None:
        result.update(binding)
    return result


def run_authorization(
    *,
    state_path: Path,
    brand: str,
    profile: str,
    timeout_seconds: float,
    lark_cli_path: str,
    approved_executable_sha256: str,
    config_dir: str | None = None,
    data_dir: str | None = None,
    process_factory: ProcessFactory = subprocess.Popen,
    emit: Emitter = _emit_json,
) -> int:
    """Start, monitor, and finish one credential-silent authorization."""

    executable = _validated_executable(lark_cli_path)
    validated_profile = _validated_profile(profile)
    normalized_config_dir = (
        _normalized_config_dir(config_dir, must_exist=True)
        if config_dir is not None
        else None
    )
    normalized_data_dir = (
        _normalized_config_dir(data_dir, must_exist=True)
        if data_dir is not None
        else None
    )
    expected_sha256 = approved_executable_sha256.casefold()
    if (
        brand not in {"feishu", "lark"}
        or executable is None
        or validated_profile is None
        or not re.fullmatch(r"[0-9a-f]{64}", expected_sha256)
        or (config_dir is not None and normalized_config_dir is None)
        or (data_dir is not None and normalized_data_dir is None)
        or (normalized_data_dir is not None and normalized_config_dir is None)
    ):
        emit(
            {
                "state": "failed",
                "reason": "lark_cli_path_invalid",
                "updated_at": _utc_timestamp(),
                "finished_at": _utc_timestamp(),
            }
        )
        return 3
    try:
        actual_sha256 = _sha256_file(executable)
    except OSError:
        actual_sha256 = ""
    if actual_sha256 != expected_sha256:
        emit(
            {
                "state": "failed",
                "reason": "lark_cli_hash_mismatch",
                "updated_at": _utc_timestamp(),
                "finished_at": _utc_timestamp(),
            }
        )
        return 3
    binding = {
        "brand": brand,
        "profile": validated_profile,
        "executable_sha256": actual_sha256,
    }
    if normalized_config_dir is not None:
        binding["config_dir"] = normalized_config_dir
        config_identity = _config_dir_identity(normalized_config_dir)
        if config_identity is None:
            emit(
                {
                    "state": "failed",
                    "reason": "lark_cli_path_invalid",
                    "updated_at": _utc_timestamp(),
                    "finished_at": _utc_timestamp(),
                }
            )
            return 3
        binding["config_dir_identity_sha256"] = config_identity
    if normalized_data_dir is not None:
        data_identity = _config_dir_identity(normalized_data_dir)
        if data_identity is None:
            emit(
                {
                    "state": "failed",
                    "reason": "lark_cli_path_invalid",
                    "updated_at": _utc_timestamp(),
                    "finished_at": _utc_timestamp(),
                }
            )
            return 3
        binding["data_dir"] = normalized_data_dir
        binding["data_dir_identity_sha256"] = data_identity
    started_epoch = time.time()
    deadline = started_epoch + timeout_seconds
    started_at = _utc_timestamp(started_epoch)
    starting = {
        "state": "starting",
        "reason": "login_process_starting",
        "started_at": started_at,
        "updated_at": started_at,
        "expires_at": _utc_timestamp(deadline),
        **binding,
    }
    try:
        _write_initial_state(state_path, starting)
    except FileExistsError:
        emit(
            {
                "state": "failed",
                "reason": "state_file_conflict",
                "updated_at": _utc_timestamp(),
                "finished_at": _utc_timestamp(),
            }
        )
        return 4
    except OSError:
        emit(
            {
                "state": "failed",
                "reason": "unexpected_authorization_failure",
                "updated_at": _utc_timestamp(),
                "finished_at": _utc_timestamp(),
            }
        )
        return 5
    emit(starting)

    command = _command_for(executable, validated_profile)
    child_environment = build_isolated_cli_environment(
        config_dir=normalized_config_dir,
        data_dir=normalized_data_dir,
    )
    containment: Any | None = None
    try:
        executable_still_matches = _sha256_file(executable) == actual_sha256
    except OSError:
        executable_still_matches = False
    config_dir_still_matches = (
        normalized_config_dir is None
        or _config_dir_identity(normalized_config_dir)
        == binding.get("config_dir_identity_sha256")
    )
    data_dir_still_matches = (
        normalized_data_dir is None
        or _config_dir_identity(normalized_data_dir)
        == binding.get("data_dir_identity_sha256")
    )
    if (
        not executable_still_matches
        or not config_dir_still_matches
        or not data_dir_still_matches
    ):
        terminal = _terminal_state(
            state="failed",
            reason=(
                "lark_cli_hash_mismatch"
                if not executable_still_matches
                else "state_file_invalid"
            ),
            pid=None,
            started_at=started_at,
            binding=binding,
        )
        _replace_state(state_path, terminal)
        emit(terminal)
        return 3
    try:
        process, containment = _start_contained_process(
            command,
            process_factory=process_factory,
            process_kwargs={
                "stdin": subprocess.DEVNULL,
                "stdout": subprocess.PIPE,
                "stderr": subprocess.PIPE,
                "bufsize": 0,
                "env": child_environment,
            },
        )
    except Exception:
        terminal = _terminal_state(
            state="failed",
            reason="login_launch_failed",
            pid=None,
            started_at=started_at,
            binding=binding,
        )
        _replace_state(state_path, terminal)
        emit(terminal)
        return 3

    try:
        pid = int(process.pid)
        running = {
            **starting,
            "pid": pid,
            "updated_at": _utc_timestamp(),
        }
        _replace_state(state_path, running)

        events: queue.Queue[SafeEvent | None] = queue.Queue()
        stdout_thread = threading.Thread(
            target=_read_stdout_events,
            args=(process.stdout, events),
            kwargs={"brand": brand, "deadline": deadline},
            daemon=True,
        )
        stderr_thread = threading.Thread(
            target=_discard_stream,
            args=(process.stderr,),
            daemon=True,
        )
        stdout_thread.start()
        stderr_thread.start()
    except Exception:
        _terminate_owned_child(process)
        if containment is not None:
            containment.close()
        terminal = _terminal_state(
            state="failed",
            reason="unexpected_authorization_failure",
            pid=None,
            started_at=started_at,
            binding=binding,
        )
        with contextlib.suppress(OSError):
            _replace_state(state_path, terminal)
        emit(terminal)
        return 5

    stdout_finished = False
    completion_verified = False
    terminal_state: dict[str, Any] | None = None
    try:
        while terminal_state is None:
            remaining = deadline - time.time()
            if remaining <= 0:
                _terminate_owned_child(process)
                terminal_state = _terminal_state(
                    state="timed_out",
                    reason="authorization_timed_out",
                    pid=pid,
                    started_at=started_at,
                    binding=binding,
                )
                break
            try:
                event = events.get(timeout=min(0.2, remaining))
            except queue.Empty:
                event = ...
            if event is None:
                stdout_finished = True
            elif isinstance(event, SafeEvent):
                if event.authorization_complete:
                    completion_verified = True
                if event.verification_url is not None:
                    pending = {
                        "state": "pending",
                        "reason": "awaiting_user_verification",
                        "verification_url": event.verification_url,
                        "expires_at": _utc_timestamp(
                            event.expires_at or deadline
                        ),
                        "pid": pid,
                        "started_at": started_at,
                        "updated_at": _utc_timestamp(),
                        **binding,
                    }
                    _replace_state(state_path, pending)
                    emit(pending)

            returncode = process.poll()
            if returncode is not None and stdout_finished:
                verified_success = returncode == 0 and completion_verified
                terminal_state = _terminal_state(
                    state="succeeded" if verified_success else "failed",
                    reason=(
                        "authorization_completed"
                        if verified_success
                        else "authorization_completion_unverified"
                        if returncode == 0
                        else "login_process_failed"
                    ),
                    pid=pid,
                    started_at=started_at,
                    binding=binding,
                )
    except KeyboardInterrupt:
        _terminate_owned_child(process)
        terminal_state = _terminal_state(
            state="cancelled",
            reason="authorization_cancelled",
            pid=pid,
            started_at=started_at,
            binding=binding,
        )
    except Exception:
        _terminate_owned_child(process)
        terminal_state = _terminal_state(
            state="failed",
            reason="unexpected_authorization_failure",
            pid=pid,
            started_at=started_at,
            binding=binding,
        )
    finally:
        stdout_thread.join(timeout=1.0)
        stderr_thread.join(timeout=1.0)

    assert terminal_state is not None
    if containment is not None:
        containment.close()
    _replace_state(state_path, terminal_state)
    emit(terminal_state)
    return 0 if terminal_state["state"] == "succeeded" else 2


def status(
    state_path: Path,
    *,
    brand: str,
    profile: str,
    approved_executable_sha256: str,
    config_dir: str | None = None,
    data_dir: str | None = None,
    emit: Emitter = _emit_json,
) -> int:
    if config_dir is not None:
        normalized_config_dir = _normalized_config_dir(
            config_dir,
            must_exist=True,
        )
        if normalized_config_dir is None:
            emit(
                {
                    "state": "failed",
                    "reason": "state_file_invalid",
                    "updated_at": _utc_timestamp(),
                }
            )
            return 2
        config_dir = normalized_config_dir
        config_dir_identity = _config_dir_identity(config_dir)
        if config_dir_identity is None:
            emit(
                {
                    "state": "failed",
                    "reason": "state_file_invalid",
                    "updated_at": _utc_timestamp(),
                }
            )
            return 2
    else:
        config_dir_identity = None
    if data_dir is not None:
        normalized_data_dir = _normalized_config_dir(
            data_dir,
            must_exist=True,
        )
        if normalized_data_dir is None or config_dir is None:
            emit(
                {
                    "state": "failed",
                    "reason": "state_file_invalid",
                    "updated_at": _utc_timestamp(),
                }
            )
            return 2
        data_dir = normalized_data_dir
        data_dir_identity = _config_dir_identity(data_dir)
        if data_dir_identity is None:
            emit(
                {
                    "state": "failed",
                    "reason": "state_file_invalid",
                    "updated_at": _utc_timestamp(),
                }
            )
            return 2
    else:
        data_dir_identity = None
    if not state_path.exists():
        emit(
            {
                "state": "absent",
                "reason": "no_state_file",
                "updated_at": _utc_timestamp(),
            }
        )
        return 1
    current = _read_state(
        state_path,
        brand=brand,
        profile=profile,
        approved_executable_sha256=approved_executable_sha256,
        config_dir=config_dir,
        config_dir_identity_sha256=config_dir_identity,
        data_dir=data_dir,
        data_dir_identity_sha256=data_dir_identity,
    )
    if current is None:
        emit(
            {
                "state": "failed",
                "reason": "state_file_invalid",
                "updated_at": _utc_timestamp(),
            }
        )
        return 2
    expires_at = _parse_timestamp(current.get("expires_at"))
    if current["state"] in ACTIVE_STATES and expires_at is not None:
        if expires_at <= time.time():
            expired = {
                "state": "expired",
                "reason": "authorization_expired",
                "updated_at": _utc_timestamp(),
            }
            for field in (
                "pid",
                "started_at",
                "brand",
                "profile",
                "executable_sha256",
                "config_dir",
                "config_dir_identity_sha256",
                "data_dir",
                "data_dir_identity_sha256",
            ):
                if field in current:
                    expired[field] = current[field]
            emit(expired)
            return 2
    pid = current.get("pid")
    updated_at = _parse_timestamp(current.get("updated_at"))
    stale = (
        updated_at is not None
        and time.time() - updated_at >= STALE_ACTIVE_GRACE_SECONDS
    )
    if (
        current["state"] in ACTIVE_STATES
        and isinstance(pid, int)
        and stale
        and not _pid_is_alive(pid)
    ):
        stopped = {
            "state": "failed",
            "reason": "authorization_process_not_running",
            "updated_at": _utc_timestamp(),
            "finished_at": _utc_timestamp(),
            "pid": pid,
        }
        for field in (
            "started_at",
            "brand",
            "profile",
            "executable_sha256",
            "config_dir",
            "config_dir_identity_sha256",
            "data_dir",
            "data_dir_identity_sha256",
        ):
            if field in current:
                stopped[field] = current[field]
        emit(stopped)
        return 2
    emit(current)
    return 0


def cleanup(
    state_path: Path,
    *,
    brand: str,
    profile: str,
    approved_executable_sha256: str,
    config_dir: str | None = None,
    data_dir: str | None = None,
    emit: Emitter = _emit_json,
) -> int:
    if config_dir is not None:
        normalized_config_dir = _normalized_config_dir(
            config_dir,
            must_exist=True,
        )
        if normalized_config_dir is None:
            emit(
                {
                    "state": "failed",
                    "reason": "state_file_invalid",
                    "updated_at": _utc_timestamp(),
                }
            )
            return 2
        config_dir = normalized_config_dir
        config_dir_identity = _config_dir_identity(config_dir)
        if config_dir_identity is None:
            emit(
                {
                    "state": "failed",
                    "reason": "state_file_invalid",
                    "updated_at": _utc_timestamp(),
                }
            )
            return 2
    else:
        config_dir_identity = None
    if data_dir is not None:
        normalized_data_dir = _normalized_config_dir(
            data_dir,
            must_exist=True,
        )
        if normalized_data_dir is None or config_dir is None:
            emit(
                {
                    "state": "failed",
                    "reason": "state_file_invalid",
                    "updated_at": _utc_timestamp(),
                }
            )
            return 2
        data_dir = normalized_data_dir
        data_dir_identity = _config_dir_identity(data_dir)
        if data_dir_identity is None:
            emit(
                {
                    "state": "failed",
                    "reason": "state_file_invalid",
                    "updated_at": _utc_timestamp(),
                }
            )
            return 2
    else:
        data_dir_identity = None
    if not state_path.exists():
        emit(
            {
                "state": "cleaned",
                "reason": "no_state_file",
                "updated_at": _utc_timestamp(),
            }
        )
        return 0
    current = _read_state(
        state_path,
        brand=brand,
        profile=profile,
        approved_executable_sha256=approved_executable_sha256,
        config_dir=config_dir,
        config_dir_identity_sha256=config_dir_identity,
        data_dir=data_dir,
        data_dir_identity_sha256=data_dir_identity,
    )
    if current is None:
        emit(
            {
                "state": "failed",
                "reason": "state_file_invalid",
                "updated_at": _utc_timestamp(),
            }
        )
        return 2
    expires_at = _parse_timestamp(current.get("expires_at"))
    active = current["state"] in ACTIVE_STATES
    expired = expires_at is not None and expires_at <= time.time()
    pid = current.get("pid")
    process_may_be_active = isinstance(pid, int) and _pid_is_alive(pid)
    updated_at = _parse_timestamp(current.get("updated_at"))
    recently_updated = (
        updated_at is not None
        and time.time() - updated_at < STALE_ACTIVE_GRACE_SECONDS
    )
    starting_without_pid = pid is None and recently_updated
    if active and (process_may_be_active or starting_without_pid):
        response = {
            "state": current["state"],
            "reason": "cleanup_refused_active_authorization",
            "updated_at": _utc_timestamp(),
        }
        for field in (
            "pid",
            "started_at",
            "expires_at",
            "brand",
            "profile",
            "executable_sha256",
            "config_dir",
            "config_dir_identity_sha256",
            "data_dir",
            "data_dir_identity_sha256",
        ):
            if field in current:
                response[field] = current[field]
        emit(response)
        return 2
    try:
        state_path.unlink()
    except OSError:
        emit(
            {
                "state": "failed",
                "reason": "unexpected_authorization_failure",
                "updated_at": _utc_timestamp(),
            }
        )
        return 2
    emit(
        {
            "state": "cleaned",
            "reason": "state_file_removed",
            "updated_at": _utc_timestamp(),
        }
    )
    return 0


class _FakeProcess:
    def __init__(self, command: list[str], stdout: bytes, stderr: bytes) -> None:
        self.command = command
        self.stdout = io.BytesIO(stdout)
        self.stderr = io.BytesIO(stderr)
        self.pid = 4242
        self._returncode = 0

    def poll(self) -> int:
        return self._returncode

    def wait(self, timeout: float | None = None) -> int:
        del timeout
        return self._returncode

    def terminate(self) -> None:
        self._returncode = -15

    def kill(self) -> None:
        self._returncode = -9


def _containment_probe_parent() -> int:
    process, _containment = _start_contained_process(
        [
            sys.executable,
            "-c",
            "import time; time.sleep(30)",
        ],
        process_factory=subprocess.Popen,
        process_kwargs={
            "stdin": subprocess.DEVNULL,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "bufsize": 0,
        },
    )
    print(process.pid, flush=True)
    os._exit(0)


def run_self_test() -> None:
    device_code = "DEVICE_CODE_MUST_NEVER_ESCAPE_8675309"
    user_code = "USER_CODE_MUST_NEVER_ESCAPE_2468"
    token = "ACCESS_TOKEN_MUST_NEVER_ESCAPE_0123456789"
    fake_complete_url = (
        "https://accounts.feishu.cn/device"
        f"?user_code={user_code}&source=lark-cli"
    )
    fake_output = (
        json.dumps(
            {
                "event": "authorization_pending",
                "verification_uri": "https://accounts.feishu.cn/device",
                "verification_uri_complete": fake_complete_url,
                "expires_in": 300,
                "device_code": device_code,
                "user_code": user_code,
                "access_token": token,
            }
        ).encode("utf-8")
        + b"\n"
        + json.dumps(
            {
                "event": "authorization_complete",
                "access_token": token,
                "refresh_token": token,
                "requested": REQUIRED_SCOPES.split(),
                "granted": [*REQUIRED_SCOPES.split(), "offline_access"],
                "missing": [],
            }
        ).encode("utf-8")
        + b"\n"
    )
    fake_stderr = f"debug device_code={device_code} token={token}\n".encode()
    captured_commands: list[list[str]] = []
    emitted: list[dict[str, Any]] = []

    def fake_factory(command: list[str], **kwargs: Any) -> _FakeProcess:
        del kwargs
        captured_commands.append(list(command))
        return _FakeProcess(command, fake_output, fake_stderr)

    with tempfile.TemporaryDirectory() as temporary_directory:
        state_path = Path(temporary_directory) / "auth-state.json"
        fake_lark_cli = Path(temporary_directory) / (
            "lark-cli.exe" if os.name == "nt" else "lark-cli"
        )
        fake_lark_cli.touch(mode=0o700)
        with contextlib.suppress(OSError):
            fake_lark_cli.chmod(0o700)
        fake_digest = _sha256_file(os.fspath(fake_lark_cli))
        shim = Path(temporary_directory) / "lark-cli.cmd"
        shim.write_text("@echo off\n", encoding="utf-8")
        assert _validated_executable(os.fspath(shim)) is None

        mismatch_emitted: list[dict[str, Any]] = []
        mismatch_code = run_authorization(
            state_path=Path(temporary_directory) / "hash-mismatch.json",
            brand="feishu",
            profile="codex-paper-reading",
            timeout_seconds=5,
            lark_cli_path=os.fspath(fake_lark_cli),
            approved_executable_sha256="0" * 64,
            process_factory=lambda *_args, **_kwargs: (_ for _ in ()).throw(
                AssertionError("a hash-mismatched executable must not run")
            ),
            emit=lambda payload: mismatch_emitted.append(dict(payload)),
        )
        assert mismatch_code != 0
        assert mismatch_emitted[-1]["reason"] == "lark_cli_hash_mismatch"
        assert not (Path(temporary_directory) / "hash-mismatch.json").exists()

        captured_stdout = io.StringIO()
        captured_stderr = io.StringIO()
        with contextlib.redirect_stdout(captured_stdout), contextlib.redirect_stderr(
            captured_stderr
        ):
            returncode = run_authorization(
                state_path=state_path,
                brand="feishu",
                profile="codex-paper-reading",
                timeout_seconds=5,
                lark_cli_path=os.fspath(fake_lark_cli),
                approved_executable_sha256=fake_digest,
                process_factory=fake_factory,
                emit=lambda payload: emitted.append(dict(payload)),
            )
        assert returncode == 0
        assert captured_commands == [
            [
                os.fspath(fake_lark_cli),
                "--profile",
                "codex-paper-reading",
                "auth",
                "login",
                "--scope",
                REQUIRED_SCOPES,
                "--json",
            ]
        ]
        flattened = "\n".join(
            (
                state_path.read_text(encoding="utf-8"),
                json.dumps(emitted, sort_keys=True),
                captured_stdout.getvalue(),
                captured_stderr.getvalue(),
                json.dumps(captured_commands),
            )
        )
        for secret in (device_code, token):
            assert secret not in flattened
        assert f'"user_code": "{user_code}"' not in flattened
        terminal = _read_state(state_path)
        assert terminal is not None
        assert terminal["state"] == "succeeded"
        assert "verification_url" not in terminal
        assert any(
            item.get("verification_url") == fake_complete_url
            for item in emitted
        )
        pending_events = [
            item for item in emitted if item.get("state") == "pending"
        ]
        assert pending_events
        assert pending_events[-1]["brand"] == "feishu"
        assert pending_events[-1]["profile"] == "codex-paper-reading"
        assert pending_events[-1]["executable_sha256"] == fake_digest
        assert not any(
            forbidden in argument
            for command in captured_commands
            for argument in command
            for forbidden in (
                "--no-wait",
                "--device-code",
                device_code,
                user_code,
                token,
            )
        )

        assert (
            status(
                state_path,
                brand="feishu",
                profile="wrong-profile",
                approved_executable_sha256=fake_digest,
                emit=lambda _: None,
            )
            != 0
        )
        assert (
            status(
                state_path,
                brand="feishu",
                profile="codex-paper-reading",
                approved_executable_sha256=fake_digest,
                emit=lambda _: None,
            )
            == 0
        )
        assert (
            cleanup(
                state_path,
                brand="feishu",
                profile="codex-paper-reading",
                approved_executable_sha256=fake_digest,
                emit=lambda _: None,
            )
            == 0
        )
        assert not state_path.exists()

        dedicated_config_dir = Path(temporary_directory) / "dedicated-config"
        dedicated_config_dir.mkdir(mode=0o700)
        dedicated_data_dir = dedicated_config_dir / "data"
        dedicated_data_dir.mkdir(mode=0o700)
        dedicated_state = Path(temporary_directory) / "dedicated-auth.json"
        captured_environments: list[dict[str, str]] = []

        def dedicated_factory(
            command: list[str],
            **kwargs: Any,
        ) -> _FakeProcess:
            environment = kwargs.get("env")
            assert isinstance(environment, dict)
            captured_environments.append(dict(environment))
            return _FakeProcess(command, fake_output, fake_stderr)

        with _temporary_environment(
            {
                "LARKSUITE_CLI_APP_SECRET": token,
                "LARKSUITE_CLI_CONFIG_DIR": "must-not-survive",
                "LARKSUITE_CLI_PROXY_ENABLE": "true",
                "LARKSUITE_CLI_PROXY_ADDRESS": "https://127.0.0.1:9443",
                "LARKSUITE_CLI_CA_PATH": token,
                "LARKSUITE_CLI_PROFILE": "ambient-profile",
                "HTTPS_PROXY": "https://127.0.0.1:9443",
                "SSL_CERT_FILE": token,
                "OPENCLAW_HOME": "must-not-survive",
                "OPENCLAW_CLI": "must-not-survive",
                "HERMES_SESSION_KEY": token,
            }
        ):
            dedicated_code = run_authorization(
                state_path=dedicated_state,
                brand="feishu",
                profile="codex-paper-reading-isolated",
                timeout_seconds=5,
                lark_cli_path=os.fspath(fake_lark_cli),
                approved_executable_sha256=fake_digest,
                config_dir=os.fspath(dedicated_config_dir),
                data_dir=os.fspath(dedicated_data_dir),
                process_factory=dedicated_factory,
                emit=lambda _: None,
            )
        assert dedicated_code == 0
        assert captured_environments
        dedicated_environment = captured_environments[-1]
        assert (
            dedicated_environment["LARKSUITE_CLI_CONFIG_DIR"]
            == os.fspath(dedicated_config_dir)
        )
        assert dedicated_environment["LARKSUITE_CLI_DATA_DIR"] == os.fspath(
            dedicated_data_dir
        )
        for forbidden_variable in (
            "LARKSUITE_CLI_APP_SECRET",
            "LARKSUITE_CLI_PROXY_ENABLE",
            "LARKSUITE_CLI_PROXY_ADDRESS",
            "LARKSUITE_CLI_CA_PATH",
            "LARKSUITE_CLI_PROFILE",
            "HTTPS_PROXY",
            "SSL_CERT_FILE",
            "OPENCLAW_HOME",
            "OPENCLAW_CLI",
            "HERMES_SESSION_KEY",
        ):
            assert forbidden_variable not in dedicated_environment
        dedicated_payload = _read_state(dedicated_state)
        assert dedicated_payload is not None
        assert dedicated_payload["config_dir"] == os.fspath(dedicated_config_dir)
        assert re.fullmatch(
            r"[0-9a-f]{64}",
            dedicated_payload["config_dir_identity_sha256"],
        )
        assert (
            status(
                dedicated_state,
                brand="feishu",
                profile="codex-paper-reading-isolated",
                approved_executable_sha256=fake_digest,
                config_dir=os.fspath(dedicated_config_dir),
                data_dir=os.fspath(dedicated_data_dir),
                emit=lambda _: None,
            )
            == 0
        )
        original_config_dir = Path(temporary_directory) / "original-config"
        dedicated_config_dir.rename(original_config_dir)
        dedicated_config_dir.mkdir(mode=0o700)
        replacement_data_dir = dedicated_config_dir / "data"
        replacement_data_dir.mkdir(mode=0o700)
        assert (
            status(
                dedicated_state,
                brand="feishu",
                profile="codex-paper-reading-isolated",
                approved_executable_sha256=fake_digest,
                config_dir=os.fspath(dedicated_config_dir),
                data_dir=os.fspath(replacement_data_dir),
                emit=lambda _: None,
            )
            != 0
        )

        clean_exit_path = Path(temporary_directory) / "clean-exit-state.json"

        def incomplete_factory(
            command: list[str],
            **kwargs: Any,
        ) -> _FakeProcess:
            del kwargs
            return _FakeProcess(
                command,
                (
                    json.dumps(
                        {
                            "event": "device_authorization",
                            "verification_uri_complete": fake_complete_url,
                            "user_code": user_code,
                            "device_code": device_code,
                        }
                    ).encode("utf-8")
                    + b"\n"
                ),
                fake_stderr,
            )

        incomplete_emitted: list[dict[str, Any]] = []
        incomplete_code = run_authorization(
            state_path=clean_exit_path,
            brand="feishu",
            profile="codex-paper-reading",
            timeout_seconds=5,
            lark_cli_path=os.fspath(fake_lark_cli),
            approved_executable_sha256=fake_digest,
            process_factory=incomplete_factory,
            emit=lambda payload: incomplete_emitted.append(dict(payload)),
        )
        assert incomplete_code != 0
        incomplete_state = _read_state(clean_exit_path)
        assert incomplete_state is not None
        assert incomplete_state["state"] == "failed"
        assert (
            incomplete_state["reason"]
            == "authorization_completion_unverified"
        )
        incomplete_flattened = "\n".join(
            (
                clean_exit_path.read_text(encoding="utf-8"),
                json.dumps(incomplete_emitted, sort_keys=True),
            )
        )
        for secret in (device_code, token):
            assert secret not in incomplete_flattened

        recoverable_path = Path(temporary_directory) / "recoverable.json"
        _write_initial_state(
            recoverable_path,
            {
                "state": "pending",
                "reason": "awaiting_user_verification",
                "verification_url": "https://accounts.feishu.cn/device",
                "expires_at": _utc_timestamp(time.time() + 300),
                "pid": os.getpid(),
                "started_at": _utc_timestamp(),
                "updated_at": _utc_timestamp(),
                "brand": "feishu",
                "profile": "codex-paper-reading",
                "executable_sha256": fake_digest,
            },
        )
        recoverable_status: list[dict[str, Any]] = []
        assert (
            status(
                recoverable_path,
                brand="feishu",
                profile="codex-paper-reading",
                approved_executable_sha256=fake_digest,
                emit=lambda payload: recoverable_status.append(dict(payload)),
            )
            == 0
        )
        assert recoverable_status[-1]["state"] == "pending"
        assert (
            cleanup(
                recoverable_path,
                brand="feishu",
                profile="codex-paper-reading",
                approved_executable_sha256=fake_digest,
                emit=lambda _: None,
            )
            != 0
        )

    assert (
        _validate_verification_url(
            "https://evil.example/device",
            brand="auto",
            secret_values=set(),
        )
        is None
    )
    assert (
        _validate_verification_url(
            f"https://accounts.feishu.cn/device?code={user_code}",
            brand="auto",
            secret_values={user_code},
            allow_opaque_suffix=True,
        )
        is None
    )
    direct_command = _command_for("/verified/lark-cli", "codex-paper-reading")
    assert direct_command == [
        "/verified/lark-cli",
        "--profile",
        "codex-paper-reading",
        "auth",
        "login",
        "--scope",
        REQUIRED_SCOPES,
        "--json",
    ]

    unexpected_exit = _safe_event_from_payload(
        {"event": "authorization_complete", "missing": []},
        brand="auto",
        now=time.time(),
        deadline=time.time() + 5,
    )
    assert unexpected_exit.authorization_complete is False
    assert _validated_executable("relative/lark-cli") is None
    assert _validated_executable(os.path.abspath("missing-lark-cli")) is None

    probe_parent = subprocess.Popen(
        [sys.executable, os.path.abspath(__file__), "--containment-probe-parent"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert probe_parent.stdout is not None
    child_pid_text = probe_parent.stdout.readline().strip()
    assert child_pid_text.isdigit()
    contained_child_pid = int(child_pid_text)
    assert probe_parent.wait(timeout=10) == 0
    containment_deadline = time.time() + 8.0
    while _pid_is_alive(contained_child_pid) and time.time() < containment_deadline:
        time.sleep(0.1)
    assert not _pid_is_alive(contained_child_pid)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run or inspect one credential-silent Feishu/Lark authorization."
        )
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--status", action="store_true")
    mode.add_argument("--cleanup", action="store_true")
    mode.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--state-file",
        help="explicit path for the ephemeral authorization state JSON",
    )
    parser.add_argument(
        "--brand",
        choices=tuple(OFFICIAL_HOSTS),
        default="auto",
        help="restrict the accepted verification host (default: auto)",
    )
    parser.add_argument(
        "--lark-cli",
        help="absolute path to the approved standalone lark-cli executable",
    )
    parser.add_argument(
        "--approved-executable-sha256",
        help="exact executable SHA-256 returned by the verified installer",
    )
    parser.add_argument(
        "--profile",
        help="exact named lark-cli profile to use for this authorization",
    )
    parser.add_argument(
        "--config-dir",
        help=(
            "optional absolute dedicated lark-cli configuration directory; "
            "when supplied it is bound into authorization state"
        ),
    )
    parser.add_argument(
        "--data-dir",
        help=(
            "optional absolute protected-data directory paired with a "
            "dedicated config directory"
        ),
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=(
            "authorization timeout in seconds "
            f"(default: {DEFAULT_TIMEOUT_SECONDS:g}, max: "
            f"{MAX_TIMEOUT_SECONDS:g})"
        ),
    )
    args = parser.parse_args(argv)
    if not args.self_test and not args.state_file:
        parser.error("--state-file is required")
    if not args.self_test and (
        args.brand == "auto"
        or not args.approved_executable_sha256
        or not args.profile
    ):
        parser.error(
            "authorization state operations require explicit --brand, --profile, "
            "and --approved-executable-sha256"
        )
    mutating_run = not args.self_test and not args.status and not args.cleanup
    if mutating_run:
        if (
            not args.lark_cli
        ):
            parser.error(
                "authorization requires explicit --lark-cli in addition to the "
                "state binding arguments"
            )
    if not 1 <= args.timeout_seconds <= MAX_TIMEOUT_SECONDS:
        parser.error(
            f"--timeout-seconds must be between 1 and {MAX_TIMEOUT_SECONDS:g}"
        )
    return args


def main(argv: list[str] | None = None) -> int:
    effective_argv = sys.argv[1:] if argv is None else argv
    if effective_argv == ["--containment-probe-parent"]:
        return _containment_probe_parent()
    args = parse_args(effective_argv)
    if args.self_test:
        run_self_test()
        print(json.dumps({"self_test": "passed"}, sort_keys=True))
        return 0

    assert args.state_file is not None
    expanded = Path(args.state_file).expanduser()
    state_path = Path(os.path.abspath(os.fspath(expanded)))
    if not state_path.parent.is_dir():
        _emit_json(
            {
                "state": "failed",
                "reason": "unexpected_authorization_failure",
                "updated_at": _utc_timestamp(),
            }
        )
        return 5
    if args.status:
        assert args.profile is not None
        assert args.approved_executable_sha256 is not None
        return status(
            state_path,
            brand=args.brand,
            profile=args.profile,
            approved_executable_sha256=args.approved_executable_sha256,
            config_dir=args.config_dir,
            data_dir=args.data_dir,
        )
    if args.cleanup:
        assert args.profile is not None
        assert args.approved_executable_sha256 is not None
        return cleanup(
            state_path,
            brand=args.brand,
            profile=args.profile,
            approved_executable_sha256=args.approved_executable_sha256,
            config_dir=args.config_dir,
            data_dir=args.data_dir,
        )
    try:
        assert args.lark_cli is not None
        assert args.approved_executable_sha256 is not None
        assert args.profile is not None
        return run_authorization(
            state_path=state_path,
            brand=args.brand,
            profile=args.profile,
            timeout_seconds=args.timeout_seconds,
            lark_cli_path=args.lark_cli,
            approved_executable_sha256=args.approved_executable_sha256,
            config_dir=args.config_dir,
            data_dir=args.data_dir,
        )
    except Exception:
        _emit_json(
            {
                "state": "failed",
                "reason": "unexpected_authorization_failure",
                "updated_at": _utc_timestamp(),
            }
        )
        return 5


if __name__ == "__main__":
    raise SystemExit(main())
