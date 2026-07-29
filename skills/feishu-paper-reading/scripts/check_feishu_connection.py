#!/usr/bin/env python3
"""Run a read-only preflight for the local Feishu CLI connection.

The checker never installs packages, starts a login, changes configuration, or
prints command output verbatim. It probes only local executable availability,
version commands, ``lark-cli auth status``, and the required document scopes.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable

from feishu_process_environment import build_isolated_cli_environment


SCHEMA_VERSION = 1
DEFAULT_TIMEOUT_SECONDS = 5.0
MAX_TIMEOUT_SECONDS = 30.0
REQUIRED_SCOPES = (
    "docx:document:create",
    "docx:document:readonly",
)
REQUIRED_SCOPE_ARGUMENT = " ".join(REQUIRED_SCOPES)
RECOGNIZED_BRANDS = {"feishu", "lark"}
ACTIONABLE_STATES = {
    "absent",
    "cli_review_required",
    "profile_selection_required",
    "configuration_required",
    "authorization_required",
    "scope_incomplete",
    "identity_confirmation_required",
    "identity_mismatch",
    "authorization_ready",
}

ANSI_OSC = re.compile(r"\x1b\][^\x07]*(?:\x07|\x1b\\)")
ANSI_CSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
SECRET_KEY = (
    r"(?:access[_-]?token|refresh[_-]?token|id[_-]?token|app[_-]?secret|"
    r"client[_-]?secret|authorization|cookie|password|private[_-]?key)"
)
SECRET_ASSIGNMENT = re.compile(
    rf"(?i)([\"']?{SECRET_KEY}[\"']?\s*[:=]\s*)"
    r"(\"[^\"\r\n]*\"|'[^'\r\n]*'|[^\s,;}]+)"
)
BEARER_TOKEN = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+")
JWT_TOKEN = re.compile(
    r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"
    r"(?:\.[A-Za-z0-9_-]{8,})?\b"
)
URL_SECRET = re.compile(
    rf"(?i)([?&](?:token|code|state|{SECRET_KEY})=)[^&#\s]+"
)
LONG_TOKEN = re.compile(
    r"(?<![A-Za-z0-9_-])"
    r"(?=[A-Za-z0-9_-]{24,}(?![A-Za-z0-9_-]))"
    r"(?=[A-Za-z0-9_-]*[A-Za-z])"
    r"(?=[A-Za-z0-9_-]*\d)"
    r"[A-Za-z0-9_-]+"
)

SECRET_FIELD_NAMES = {
    "access_token",
    "refreshtoken",
    "refresh_token",
    "id_token",
    "app_secret",
    "client_secret",
    "authorization",
    "cookie",
    "password",
    "private_key",
}
CONFIG_BOOLEAN_KEYS = {
    "configured",
    "configuration_present",
    "app_configured",
    "has_config",
    "credentials_configured",
}
AUTH_BOOLEAN_KEYS = {
    "authenticated",
    "authorized",
    "connected",
    "logged_in",
    "is_authenticated",
    "is_authorized",
    "ok",
    "ready",
    "valid",
    "verified",
}
CONFIG_REQUIRED_KEYS = {
    "configuration_required",
    "needs_configuration",
    "requires_configuration",
}
AUTH_REQUIRED_KEYS = {
    "authentication_required",
    "authorization_required",
    "login_required",
    "needs_authentication",
    "needs_authorization",
    "requires_authentication",
    "requires_authorization",
}
CONFIG_STATUSES = {
    "configuration_required",
    "configuration required",
    "not_configured",
    "not configured",
    "unconfigured",
    "missing_configuration",
    "missing configuration",
}
AUTH_STATUSES = {
    "authorization_required",
    "authorization required",
    "authentication_required",
    "authentication required",
    "unauthenticated",
    "unauthorized",
    "not_authenticated",
    "not authenticated",
    "not_authorized",
    "not authorized",
    "not_logged_in",
    "not logged in",
    "expired",
    "invalid",
}
CONFIG_TEXT_MARKERS = (
    "not configured",
    "configuration required",
    "missing configuration",
    "missing app id",
    "missing app secret",
    "missing client id",
    "missing client secret",
    "no configuration",
    "未配置",
    "缺少配置",
    "请先配置",
)
AUTH_TEXT_MARKERS = (
    "auth required",
    "authorization required",
    "authentication required",
    "not authenticated",
    "not authorized",
    "not logged in",
    "login required",
    "please log in",
    "please login",
    "unauthenticated",
    "unauthorized",
    "token expired",
    "invalid token",
    "no active session",
    "未登录",
    "未授权",
    "需要登录",
    "需要授权",
    "登录已过期",
    "授权已过期",
)


@dataclass(frozen=True)
class SafeIdentityFingerprint:
    brand: str
    app_id_sha256: str
    user_open_id_sha256: str


@dataclass(frozen=True)
class CommandResult:
    returncode: int | None
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False
    launch_failed: bool = False
    identity_fingerprint: SafeIdentityFingerprint | None = None


Runner = Callable[[str, list[str], float], CommandResult]
Which = Callable[[str], str | None]
Hasher = Callable[[str], str]

def sanitize_output(value: str) -> str:
    """Remove terminal control sequences and redact credential-shaped values."""

    value = ANSI_OSC.sub("", value)
    value = ANSI_CSI.sub("", value)

    def redact_assignment(match: re.Match[str]) -> str:
        original = match.group(2)
        quote = original[0] if original[:1] in {'"', "'"} else ""
        unquoted = original.strip("\"'").strip().casefold()
        if unquoted in {"", "false", "none", "null"}:
            return match.group(0)
        return f"{match.group(1)}{quote}[REDACTED]{quote}"

    value = SECRET_ASSIGNMENT.sub(redact_assignment, value)
    value = BEARER_TOKEN.sub("Bearer [REDACTED]", value)
    value = JWT_TOKEN.sub("[REDACTED]", value)
    value = URL_SECRET.sub(r"\1[REDACTED]", value)
    value = LONG_TOKEN.sub("[REDACTED]", value)
    return value.replace("\x00", "")


def _extract_raw_json_for_identity(value: str) -> Any | None:
    """Parse raw in-memory CLI JSON only for immediate identity hashing."""

    cleaned = ANSI_CSI.sub("", ANSI_OSC.sub("", value)).replace("\x00", "").strip()
    if not cleaned:
        return None
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    decoder = json.JSONDecoder()
    candidates: list[Any] = []
    index = 0
    while index < len(cleaned):
        opening_indexes = [
            found
            for found in (cleaned.find("{", index), cleaned.find("[", index))
            if found >= 0
        ]
        if not opening_indexes:
            break
        start = min(opening_indexes)
        try:
            payload, consumed = decoder.raw_decode(cleaned[start:])
        except json.JSONDecodeError:
            index = start + 1
            continue
        candidates.append(payload)
        index = start + consumed
    return candidates[-1] if candidates else None


def _safe_identity_from_raw(value: str) -> SafeIdentityFingerprint | None:
    payload = _extract_raw_json_for_identity(value)
    if not isinstance(payload, dict):
        return None
    identities = payload.get("identities")
    user = identities.get("user") if isinstance(identities, dict) else None
    app_id = payload.get("appId")
    brand = payload.get("brand")
    open_id = user.get("openId") if isinstance(user, dict) else None
    values = (app_id, brand, open_id)
    if not all(
        isinstance(item, str)
        and item
        and item == item.strip()
        and len(item) <= 512
        and not any(ord(character) < 32 for character in item)
        for item in values
    ):
        return None
    normalized_brand = brand.casefold()
    if normalized_brand not in RECOGNIZED_BRANDS:
        return None
    return SafeIdentityFingerprint(
        brand=normalized_brand,
        app_id_sha256=_fingerprint(app_id),
        user_open_id_sha256=_fingerprint(open_id),
    )


def run_command(
    executable: str,
    arguments: list[str],
    timeout_seconds: float,
    *,
    config_dir: str | None = None,
    data_dir: str | None = None,
) -> CommandResult:
    """Run one bounded read-only command and retain only sanitized output."""

    environment = build_isolated_cli_environment(
        config_dir=config_dir,
        data_dir=data_dir,
    )
    try:
        completed = subprocess.run(
            [executable, *arguments],
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout_seconds,
            check=False,
            env=environment,
        )
    except subprocess.TimeoutExpired:
        return CommandResult(returncode=None, timed_out=True)
    except (OSError, ValueError):
        return CommandResult(returncode=None, launch_failed=True)

    raw_output = f"{completed.stdout}\n{completed.stderr}"
    identity_fingerprint = (
        _safe_identity_from_raw(raw_output)
        if "auth" in arguments and "status" in arguments
        else None
    )
    result = CommandResult(
        returncode=completed.returncode,
        stdout=sanitize_output(completed.stdout),
        stderr=sanitize_output(completed.stderr),
        identity_fingerprint=identity_fingerprint,
    )
    del raw_output
    del completed
    return result


def extract_json(value: str) -> Any | None:
    """Extract the last JSON object or array from otherwise noisy CLI output."""

    cleaned = sanitize_output(value).strip()
    if not cleaned:
        return None
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    decoder = json.JSONDecoder()
    candidates: list[Any] = []
    index = 0
    while index < len(cleaned):
        opening_indexes = [
            found
            for found in (cleaned.find("{", index), cleaned.find("[", index))
            if found >= 0
        ]
        if not opening_indexes:
            break
        start = min(opening_indexes)
        try:
            payload, consumed = decoder.raw_decode(cleaned[start:])
        except json.JSONDecodeError:
            index = start + 1
            continue
        candidates.append(payload)
        index = start + consumed
    return candidates[-1] if candidates else None


def _normalized_key(value: str) -> str:
    value = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", value)
    return re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_")


def _semantic_values(
    value: Any,
    path: tuple[str, ...] = (),
) -> Iterable[tuple[str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = _normalized_key(str(key))
            child_path = (*path, normalized)
            if normalized in SECRET_FIELD_NAMES:
                yield ".".join(child_path), bool(child)
            else:
                yield from _semantic_values(child, child_path)
        return
    if isinstance(value, list):
        for child in value:
            yield from _semantic_values(child, path)
        return
    if path:
        if isinstance(value, str):
            value = sanitize_output(value).strip().casefold()[:256]
        yield ".".join(path), value


def _terminal_key(path: str) -> str:
    return path.rsplit(".", 1)[-1]


def _text_for_classification(result: CommandResult) -> str:
    text = f"{result.stdout}\n{result.stderr}".casefold()
    return re.sub(r"[_-]+", " ", text)


def classify_authorization(
    result: CommandResult,
    *,
    require_verified: bool = True,
) -> tuple[str, str]:
    """Classify a sanitized ``lark-cli auth status`` result."""

    if result.timed_out:
        return "unknown", "authorization_probe_timed_out"
    if result.launch_failed:
        return "unknown", "authorization_probe_failed_to_start"

    combined = f"{result.stdout}\n{result.stderr}"
    payload = extract_json(combined)
    semantics = list(_semantic_values(payload)) if payload is not None else []
    text = _text_for_classification(result)

    # Current lark-cli reports both bot and user diagnostics. Fail closed on
    # schema drift: document publishing is eligible only when every expected
    # user-profile field is present and the server verification was requested.
    if isinstance(payload, dict) and result.returncode == 0:
        identities = payload.get("identities")
        user = identities.get("user") if isinstance(identities, dict) else None
        identity_value = payload.get("identity")
        effective_identity = (
            identity_value.strip().casefold()
            if isinstance(identity_value, str)
            else ""
        )
        if effective_identity in {"bot", "none"}:
            if not isinstance(user, dict) or user.get("available") is not True:
                return (
                    "authorization_required",
                    "verified_user_identity_not_available",
                )
            return "unknown", "inconsistent_effective_identity"
        if effective_identity == "user":
            if not isinstance(user, dict):
                return "unknown", "user_identity_diagnostics_missing"
            if user.get("available") is not True:
                return (
                    "authorization_required",
                    "verified_user_identity_not_available",
                )
            if not require_verified:
                return (
                    "unknown",
                    "authorization_present_not_server_verified",
                )
            if user.get("verified") is not True:
                return (
                    "authorization_required",
                    "user_identity_not_server_verified",
                )
            open_id = user.get("openId")
            if not isinstance(open_id, str) or not open_id.strip():
                return "unknown", "verified_user_open_id_missing"
            app_id = payload.get("appId")
            if not isinstance(app_id, str) or not app_id.strip():
                return "unknown", "verified_app_id_missing"
            brand = payload.get("brand")
            if (
                not isinstance(brand, str)
                or brand.strip().casefold() not in RECOGNIZED_BRANDS
            ):
                return "unknown", "unrecognized_or_missing_brand"
            return "authorization_ready", "user_authorization_verified"

    config_missing = False
    auth_missing = False
    for path, value in semantics:
        key = _terminal_key(path)
        if key in CONFIG_BOOLEAN_KEYS and value is False:
            config_missing = True
        if key in CONFIG_REQUIRED_KEYS and value is True:
            config_missing = True
        if key in {"app_id", "app_secret", "client_id", "client_secret"} and value in {
            None,
            "",
            False,
        }:
            config_missing = True
        if key in AUTH_REQUIRED_KEYS and value is True:
            auth_missing = True
        if key in AUTH_BOOLEAN_KEYS:
            if value is False:
                auth_missing = True
        if key in {"status", "state", "result"} and isinstance(value, str):
            status = value.strip()
            if status in CONFIG_STATUSES:
                config_missing = True
            elif status in AUTH_STATUSES:
                auth_missing = True
    if config_missing or any(marker in text for marker in CONFIG_TEXT_MARKERS):
        return "configuration_required", "lark_cli_configuration_missing"
    if auth_missing or any(marker in text for marker in AUTH_TEXT_MARKERS):
        return "authorization_required", "lark_cli_authorization_missing_or_invalid"
    return "unknown", "unrecognized_authorization_status"


def _scope_list(value: Any) -> list[str] | None:
    if value is None:
        return []
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item for item in value
    ):
        return None
    return value


def classify_scopes(result: CommandResult) -> tuple[str, str]:
    """Classify the exact minimum-scope predicate from ``lark-cli``."""

    if result.timed_out:
        return "unknown", "scope_probe_timed_out"
    if result.launch_failed:
        return "unknown", "scope_probe_failed_to_start"

    payload = extract_json(f"{result.stdout}\n{result.stderr}")
    if not isinstance(payload, dict):
        return "unknown", "unrecognized_scope_status"

    granted = _scope_list(payload.get("granted"))
    missing = _scope_list(payload.get("missing"))
    if granted is None or missing is None:
        return "unknown", "malformed_scope_lists"

    required = set(REQUIRED_SCOPES)
    granted_set = set(granted)
    missing_set = set(missing)
    if not granted_set.issubset(required) or not missing_set.issubset(required):
        return "unknown", "scope_response_contains_unrequested_scope"
    if granted_set & missing_set or granted_set | missing_set != required:
        return "unknown", "scope_response_does_not_cover_requested_scopes"

    if (
        result.returncode == 0
        and payload.get("ok") is True
        and granted_set == required
        and not missing
    ):
        return "authorization_ready", "minimum_document_scopes_verified"
    if (
        result.returncode == 1
        and payload.get("ok") is False
        and bool(missing)
    ):
        return "scope_incomplete", "minimum_document_scopes_missing"
    return "unknown", "inconsistent_scope_status"


def _first_safe_line(result: CommandResult) -> str | None:
    for line in f"{result.stdout}\n{result.stderr}".splitlines():
        line = sanitize_output(line).strip()
        if line:
            return line[:160]
    return None


def _version_check(
    name: str,
    executable: str,
    timeout_seconds: float,
    runner: Runner,
) -> dict[str, Any]:
    result = runner(executable, ["--version"], timeout_seconds)
    if result.timed_out:
        probe = "timed_out"
    elif result.launch_failed:
        probe = "launch_failed"
    elif result.returncode == 0:
        probe = "ok"
    else:
        probe = "failed"
    return {
        "name": name,
        "present": True,
        "probe": probe,
        "version": _first_safe_line(result) if probe == "ok" else None,
    }


def _missing_check(name: str) -> dict[str, Any]:
    return {"name": name, "present": False, "probe": "not_run", "version": None}


def _next_action(state: str) -> str:
    return {
        "absent": "request_consent_then_install_verified_official_lark_cli",
        "cli_review_required": "review_candidate_or_install_verified_official_lark_cli",
        "profile_selection_required": "select_named_profile_and_expected_brand",
        "configuration_required": "request_consent_then_start_guided_profile_setup",
        "authorization_required": "request_consent_then_start_minimum_scope_login",
        "scope_incomplete": "request_consent_then_authorize_missing_document_scopes",
        "identity_confirmation_required": "show_safe_fingerprint_and_confirm_intended_identity",
        "identity_mismatch": "stop_and_resolve_profile_account_or_tenant_mismatch",
        "authorization_ready": "publish_formal_report_then_verify_readback",
        "unknown": "inspect_lark_cli_diagnostics_without_exposing_credentials",
    }[state]


def _report_exit_code(report: dict[str, Any]) -> int:
    return 0 if report.get("state_recognized") is True else 2


def _validated_explicit_executable(value: str | None) -> str | None:
    if value is None:
        return None
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        return None
    try:
        metadata = candidate.lstat()
    except OSError:
        return None
    if candidate.is_symlink() or not stat.S_ISREG(metadata.st_mode):
        return None
    suffix = candidate.suffix.casefold()
    if suffix in {".bat", ".cmd", ".ps1"}:
        return None
    if os.name == "nt" and suffix != ".exe":
        return None
    if os.name != "nt" and not os.access(candidate, os.X_OK):
        return None
    return os.fspath(candidate)


def _sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _valid_profile(value: str | None) -> bool:
    return bool(
        isinstance(value, str)
        and value
        and value == value.strip()
        and len(value) <= 128
        and not any(ord(character) < 32 for character in value)
    )


def _validated_config_dir(value: str | None) -> str | None:
    if value is None:
        return None
    if not value or value != value.strip():
        raise ValueError("config_dir must be a non-empty absolute path")
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        raise ValueError("config_dir must be absolute")
    absolute = Path(os.path.abspath(os.fspath(candidate)))
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


def _config_dir_identity(config_dir: str) -> str | None:
    try:
        normalized = _validated_config_dir(config_dir)
        if normalized is None:
            return None
        metadata = Path(normalized).lstat()
    except (OSError, ValueError):
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


def _identity_fingerprint(
    result: CommandResult,
    *,
    profile: str,
) -> dict[str, str] | None:
    if result.identity_fingerprint is not None:
        return {
            "profile": profile,
            "brand": result.identity_fingerprint.brand,
            "app_id_sha256": result.identity_fingerprint.app_id_sha256,
            "user_open_id_sha256": result.identity_fingerprint.user_open_id_sha256,
        }
    payload = extract_json(f"{result.stdout}\n{result.stderr}")
    if not isinstance(payload, dict):
        return None
    identities = payload.get("identities")
    user = identities.get("user") if isinstance(identities, dict) else None
    app_id = payload.get("appId")
    brand = payload.get("brand")
    open_id = user.get("openId") if isinstance(user, dict) else None
    if not all(
        isinstance(value, str)
        and value.strip()
        and value.strip() != "[REDACTED]"
        for value in (app_id, brand, open_id)
    ):
        return None
    normalized_brand = brand.strip().casefold()
    if normalized_brand not in RECOGNIZED_BRANDS:
        return None
    return {
        "profile": profile,
        "brand": normalized_brand,
        "app_id_sha256": _fingerprint(app_id.strip()),
        "user_open_id_sha256": _fingerprint(open_id.strip()),
    }


def _build_preflight_report(
    state: str,
    reason: str,
    checks: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "ok": state == "authorization_ready",
        "state_recognized": state in ACTIONABLE_STATES,
        "state": state,
        "authorization_ready": state == "authorization_ready",
        "delivery_verified": False,
        "reason": reason,
        "checks": checks,
        "next_action": _next_action(state),
        "safety": {
            "read_only": True,
            "installs_packages": False,
            "starts_login": False,
            "changes_configuration": False,
            "raw_command_output_included": False,
        },
    }


def collect_preflight(
    *,
    timeout_seconds: float,
    verify: bool,
    lark_cli_path: str | None = None,
    approved_executable_sha256: str | None = None,
    profile: str | None = None,
    expected_brand: str | None = None,
    expected_app_id_sha256: str | None = None,
    expected_user_open_id_sha256: str | None = None,
    config_dir: str | None = None,
    data_dir: str | None = None,
    which: Which = shutil.which,
    runner: Runner = run_command,
    hasher: Hasher = _sha256_file,
) -> dict[str, Any]:
    """Collect a deterministic preflight report using injectable host probes."""

    checks: dict[str, Any] = {}
    try:
        normalized_config_dir = _validated_config_dir(config_dir)
        normalized_data_dir = _validated_config_dir(data_dir)
    except ValueError:
        checks["config_dir"] = {
            "present": False,
            "valid": False,
        }
        return _build_preflight_report(
            "configuration_required",
            "dedicated_config_dir_invalid",
            checks,
        )
    if normalized_data_dir is not None and normalized_config_dir is None:
        checks["data_dir"] = {
            "present": True,
            "valid": False,
        }
        return _build_preflight_report(
            "configuration_required",
            "dedicated_data_dir_without_config_dir",
            checks,
        )
    if normalized_config_dir is not None:
        initial_config_identity = _config_dir_identity(normalized_config_dir)
        if initial_config_identity is None:
            return _build_preflight_report(
                "configuration_required",
                "dedicated_config_dir_invalid",
                checks,
            )
        checks["config_dir"] = {
            "present": True,
            "valid": True,
            "path": normalized_config_dir,
            "identity_sha256": initial_config_identity,
        }
    else:
        initial_config_identity = None
    if normalized_data_dir is not None:
        initial_data_identity = _config_dir_identity(normalized_data_dir)
        if initial_data_identity is None:
            return _build_preflight_report(
                "configuration_required",
                "dedicated_data_dir_invalid",
                checks,
            )
        checks["data_dir"] = {
            "present": True,
            "valid": True,
            "path": normalized_data_dir,
            "identity_sha256": initial_data_identity,
        }
    else:
        initial_data_identity = None
    expected_executable_hash: str | None = None

    def invoke(
        executable: str,
        arguments: list[str],
        timeout: float,
    ) -> CommandResult:
        if (
            normalized_config_dir is not None
            and _config_dir_identity(normalized_config_dir)
            != initial_config_identity
        ):
            return CommandResult(returncode=None, launch_failed=True)
        if (
            normalized_data_dir is not None
            and _config_dir_identity(normalized_data_dir)
            != initial_data_identity
        ):
            return CommandResult(returncode=None, launch_failed=True)
        if expected_executable_hash is not None:
            try:
                current_executable_hash = hasher(executable)
            except OSError:
                return CommandResult(returncode=None, launch_failed=True)
            if current_executable_hash != expected_executable_hash:
                return CommandResult(returncode=None, launch_failed=True)
        if runner is run_command:
            return run_command(
                executable,
                arguments,
                timeout,
                config_dir=normalized_config_dir,
                data_dir=normalized_data_dir,
            )
        return runner(executable, arguments, timeout)
    if lark_cli_path is None:
        discovered = which("lark-cli")
        if not discovered:
            checks["lark_cli"] = _missing_check("lark-cli")
            return _build_preflight_report(
                "absent",
                "lark_cli_not_found",
                checks,
            )
        validated_candidate = _validated_explicit_executable(discovered)
        candidate_check: dict[str, Any] = {
            "name": "lark-cli",
            "present": True,
            "probe": "not_run",
            "executed": False,
        }
        if validated_candidate is None:
            candidate_check["candidate_path"] = os.path.abspath(discovered)
            candidate_check["standalone_regular_executable"] = False
            reason = "path_candidate_is_not_an_approved_standalone_executable"
        else:
            candidate_check["candidate_path"] = validated_candidate
            candidate_check["standalone_regular_executable"] = True
            try:
                candidate_check["executable_sha256"] = hasher(validated_candidate)
                reason = "path_candidate_requires_provenance_review"
            except OSError:
                reason = "path_candidate_could_not_be_hashed"
        checks["lark_cli"] = candidate_check
        return _build_preflight_report("cli_review_required", reason, checks)

    lark_executable = _validated_explicit_executable(lark_cli_path)
    if lark_executable is None:
        checks["lark_cli"] = _missing_check("lark-cli")
        return _build_preflight_report(
            "cli_review_required",
            "explicit_lark_cli_is_not_a_standalone_executable",
            checks,
        )
    try:
        executable_sha256 = hasher(lark_executable)
    except OSError:
        return _build_preflight_report(
            "cli_review_required",
            "explicit_lark_cli_could_not_be_hashed",
            checks,
        )
    checks["lark_cli"] = {
        "name": "lark-cli",
        "present": True,
        "probe": "not_run",
        "executed": False,
        "path": lark_executable,
        "executable_sha256": executable_sha256,
    }
    approved_digest = (
        approved_executable_sha256.casefold()
        if isinstance(approved_executable_sha256, str)
        else None
    )
    if (
        approved_digest is None
        or not re.fullmatch(r"[0-9a-f]{64}", approved_digest)
        or approved_digest != executable_sha256
    ):
        return _build_preflight_report(
            "cli_review_required",
            "executable_hash_not_approved_or_mismatched",
            checks,
        )
    expected_executable_hash = executable_sha256
    if not _valid_profile(profile) or expected_brand not in RECOGNIZED_BRANDS:
        return _build_preflight_report(
            "profile_selection_required",
            "explicit_profile_and_brand_are_required",
            checks,
        )

    assert profile is not None
    assert expected_brand is not None
    checks["lark_cli"] = _version_check(
        "lark-cli",
        lark_executable,
        timeout_seconds,
        invoke,
    )
    checks["lark_cli"]["path"] = lark_executable
    checks["lark_cli"]["executable_sha256"] = executable_sha256
    checks["lark_cli"]["executed"] = True
    if checks["lark_cli"]["probe"] != "ok":
        return _build_preflight_report(
            "unknown",
            "lark_cli_unusable",
            checks,
        )

    arguments = ["--profile", profile, "auth", "status", "--json"]
    if verify:
        arguments.append("--verify")
    auth_result = invoke(lark_executable, arguments, timeout_seconds)
    state, reason = classify_authorization(
        auth_result,
        require_verified=verify,
    )
    checks["authorization"] = {
        "probe": (
            "timed_out"
            if auth_result.timed_out
            else "launch_failed"
            if auth_result.launch_failed
            else "completed"
        ),
        "exit_code": auth_result.returncode,
        "verification_requested": verify,
        "classification": state,
        "profile": profile,
        "expected_brand": expected_brand,
    }
    if state != "authorization_ready":
        return _build_preflight_report(state, reason, checks)

    identity = _identity_fingerprint(auth_result, profile=profile)
    if identity is None:
        return _build_preflight_report(
            "unknown",
            "verified_identity_fingerprint_unavailable",
            checks,
        )
    checks["identity"] = {**identity, "confirmed": False}
    if identity["brand"] != expected_brand:
        return _build_preflight_report(
            "identity_mismatch",
            "verified_brand_does_not_match_expected_brand",
            checks,
        )
    expected_app = (
        expected_app_id_sha256.casefold()
        if isinstance(expected_app_id_sha256, str)
        else None
    )
    expected_user = (
        expected_user_open_id_sha256.casefold()
        if isinstance(expected_user_open_id_sha256, str)
        else None
    )
    if expected_app is None or expected_user is None:
        return _build_preflight_report(
            "identity_confirmation_required",
            "confirm_safe_app_and_user_fingerprints",
            checks,
        )
    if (
        identity["app_id_sha256"] != expected_app
        or identity["user_open_id_sha256"] != expected_user
    ):
        return _build_preflight_report(
            "identity_mismatch",
            "verified_app_or_user_fingerprint_mismatch",
            checks,
        )
    checks["identity"]["confirmed"] = True

    scope_arguments = [
        "--profile",
        profile,
        "auth",
        "check",
        "--scope",
        REQUIRED_SCOPE_ARGUMENT,
        "--json",
    ]
    scope_result = invoke(
        lark_executable,
        scope_arguments,
        timeout_seconds,
    )
    state, reason = classify_scopes(scope_result)
    checks["scopes"] = {
        "probe": (
            "timed_out"
            if scope_result.timed_out
            else "launch_failed"
            if scope_result.launch_failed
            else "completed"
        ),
        "exit_code": scope_result.returncode,
        "required": list(REQUIRED_SCOPES),
        "classification": state,
    }
    return _build_preflight_report(state, reason, checks)


def run_self_test() -> None:
    secret = "abcDEF0123456789abcDEF0123456789"
    jwt = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.signature123"
    dirty = (
        f"\x1b[31maccess_token={secret}\x1b[0m "
        f"Bearer {secret} {jwt} https://example.test/?code={secret}"
    )
    cleaned = sanitize_output(dirty)
    assert "\x1b" not in cleaned
    assert secret not in cleaned
    assert jwt not in cleaned
    assert cleaned.count("[REDACTED]") >= 4

    realistic_app_a = "cli_a6b71f3d8c9442f7a71200aabfd92651"
    realistic_user_a = "ou_7dab8a3d3cdcc9da365777c7ad535d62"
    realistic_app_b = "cli_b73998e4e12a475f945ae7a15e61c229"
    realistic_user_b = "ou_0192fd9408b947ac87df20c82cff63d1"

    def raw_identity(app_id: str, open_id: str) -> str:
        return json.dumps(
            {
                "appId": app_id,
                "brand": "feishu",
                "identities": {"user": {"openId": open_id}},
            }
        )

    safe_identity_a = _safe_identity_from_raw(
        raw_identity(realistic_app_a, realistic_user_a)
    )
    safe_identity_b = _safe_identity_from_raw(
        raw_identity(realistic_app_b, realistic_user_b)
    )
    assert safe_identity_a is not None and safe_identity_b is not None
    assert safe_identity_a.app_id_sha256 != safe_identity_b.app_id_sha256
    assert (
        safe_identity_a.user_open_id_sha256
        != safe_identity_b.user_open_id_sha256
    )
    safe_serialized = json.dumps(
        {
            "a": safe_identity_a.__dict__,
            "b": safe_identity_b.__dict__,
        },
        sort_keys=True,
    )
    sanitized_identities = sanitize_output(
        raw_identity(realistic_app_a, realistic_user_a)
        + "\n"
        + raw_identity(realistic_app_b, realistic_user_b)
    )
    for raw_identifier in (
        realistic_app_a,
        realistic_user_a,
        realistic_app_b,
        realistic_user_b,
    ):
        assert raw_identifier not in safe_serialized
        assert raw_identifier not in sanitized_identities

    noisy_json = (
        "status probe\n"
        f'{{"authenticated": true, "access_token": "{secret}", '
        '"verification": {"verified": true}}}\n'
    )
    payload = extract_json(noisy_json)
    assert isinstance(payload, dict)
    assert payload["authenticated"] is True
    assert payload["access_token"] == "[REDACTED]"

    valid_status = json.dumps(
        {
            "appId": "cli_app_123",
            "brand": "feishu",
            "identity": "user",
            "verified": True,
            "identities": {
                "bot": {
                    "available": True,
                    "verified": True,
                    "status": "ready",
                    "openId": "ou_bot_123",
                },
                "user": {
                    "available": True,
                    "verified": True,
                    "status": "valid",
                    "openId": "ou_user_123",
                },
            },
        }
    )
    fixtures = (
        (
            CommandResult(0, '{"configured": false}'),
            "configuration_required",
        ),
        (
            CommandResult(1, '{"appId": null, "appSecret": null}'),
            "configuration_required",
        ),
        (
            CommandResult(1, '{"configured": true, "authenticated": false}'),
            "authorization_required",
        ),
        (
            CommandResult(1, '{"authorizationRequired": true}'),
            "authorization_required",
        ),
        (
            CommandResult(0, '{"authenticated": true, "verified": true}'),
            "unknown",
        ),
        (
            CommandResult(0, '{"isAuthenticated": true, "ok": true}'),
            "unknown",
        ),
        (
            CommandResult(
                0,
                '{"identity":"bot","verified":true,"identities":'
                '{"bot":{"available":true,"verified":true,"status":"valid"},'
                '"user":{"available":false,"verified":null,'
                '"status":"not_logged_in"}}}',
            ),
            "authorization_required",
        ),
        (
            CommandResult(0, valid_status),
            "authorization_ready",
        ),
        (
            CommandResult(
                0,
                valid_status.replace('"identity": "user",', ""),
            ),
            "unknown",
        ),
        (
            CommandResult(
                0,
                valid_status.replace('"openId": "ou_user_123"', '"openId": ""'),
            ),
            "unknown",
        ),
        (
            CommandResult(
                0,
                valid_status.replace('"appId": "cli_app_123"', '"appId": ""'),
            ),
            "unknown",
        ),
        (
            CommandResult(
                0,
                valid_status.replace('"brand": "feishu"', '"brand": "other"'),
            ),
            "unknown",
        ),
        (
            CommandResult(
                0,
                valid_status.replace('"brand": "feishu",', ""),
            ),
            "unknown",
        ),
        (
            CommandResult(
                0,
                valid_status.replace(
                    '"available": true, "verified": true, "status": "valid"',
                    '"available": true, "verified": false, "status": "invalid"',
                ),
            ),
            "authorization_required",
        ),
        (
            CommandResult(1, stderr="token expired"),
            "authorization_required",
        ),
        (
            CommandResult(0, '{"message": "something new"}'),
            "unknown",
        ),
        (
            CommandResult(None, timed_out=True),
            "unknown",
        ),
    )
    for fixture, expected in fixtures:
        actual, _ = classify_authorization(fixture)
        assert actual == expected, (fixture, expected, actual)

    local_only, _ = classify_authorization(
        CommandResult(
            0,
            '{"identity":"user","identities":'
            '{"user":{"available":true,"verified":null,"status":"valid"}}}',
        ),
        require_verified=False,
    )
    assert local_only == "unknown"

    scope_fixtures = (
        (
            CommandResult(
                0,
                json.dumps(
                    {
                        "ok": True,
                        "granted": list(REQUIRED_SCOPES),
                        "missing": None,
                    }
                ),
            ),
            "authorization_ready",
        ),
        (
            CommandResult(
                1,
                json.dumps(
                    {
                        "ok": False,
                        "granted": [REQUIRED_SCOPES[0]],
                        "missing": [REQUIRED_SCOPES[1]],
                    }
                ),
            ),
            "scope_incomplete",
        ),
        (
            CommandResult(
                0,
                json.dumps(
                    {
                        "ok": False,
                        "granted": [REQUIRED_SCOPES[0]],
                        "missing": [REQUIRED_SCOPES[1]],
                    }
                ),
            ),
            "unknown",
        ),
        (
            CommandResult(
                0,
                json.dumps(
                    {
                        "ok": True,
                        "granted": [REQUIRED_SCOPES[0]],
                        "missing": [],
                    }
                ),
            ),
            "unknown",
        ),
        (
            CommandResult(
                0,
                json.dumps(
                    {
                        "ok": True,
                        "granted": [*REQUIRED_SCOPES, "unexpected:scope"],
                        "missing": [],
                    }
                ),
            ),
            "unknown",
        ),
    )
    for fixture, expected in scope_fixtures:
        actual, _ = classify_scopes(fixture)
        assert actual == expected, (fixture, expected, actual)

    def standalone_which(name: str) -> str | None:
        assert name == "lark-cli", "node/npm must not gate a standalone CLI"
        return "/tools/lark-cli"

    def fake_runner(
        executable: str,
        arguments: list[str],
        timeout_seconds: float,
    ) -> CommandResult:
        assert timeout_seconds == 3
        if arguments == ["--version"]:
            return CommandResult(0, "1.2.3")
        if arguments == [
            "--profile",
            "codex-paper-reading",
            "auth",
            "status",
            "--json",
            "--verify",
        ]:
            return CommandResult(0, valid_status)
        assert arguments == [
            "--profile",
            "codex-paper-reading",
            "auth",
            "check",
            "--scope",
            REQUIRED_SCOPE_ARGUMENT,
            "--json",
        ]
        return CommandResult(
            0,
            json.dumps(
                {
                    "ok": True,
                    "granted": list(REQUIRED_SCOPES),
                    "missing": None,
                }
            ),
        )

    path_candidate = collect_preflight(
        timeout_seconds=3,
        verify=True,
        which=standalone_which,
        runner=lambda *_: (_ for _ in ()).throw(
            AssertionError("a PATH candidate must not be executed")
        ),
    )
    assert path_candidate["state"] == "cli_review_required"
    assert path_candidate["checks"]["lark_cli"]["executed"] is False

    def missing_scope_runner(
        executable: str,
        arguments: list[str],
        timeout_seconds: float,
    ) -> CommandResult:
        if arguments == [
            "--profile",
            "codex-paper-reading",
            "auth",
            "check",
            "--scope",
            REQUIRED_SCOPE_ARGUMENT,
            "--json",
        ]:
            return CommandResult(
                1,
                json.dumps(
                    {
                        "ok": False,
                        "granted": [REQUIRED_SCOPES[0]],
                        "missing": [REQUIRED_SCOPES[1]],
                    }
                ),
            )
        return fake_runner(executable, arguments, timeout_seconds)

    absent = collect_preflight(
        timeout_seconds=3,
        verify=True,
        which=lambda name: None,
        runner=fake_runner,
    )
    assert absent["ok"] is False
    assert absent["state_recognized"] is True
    assert absent["state"] == "absent"

    def no_identity_runner(
        executable: str,
        arguments: list[str],
        timeout_seconds: float,
    ) -> CommandResult:
        if arguments == ["--version"]:
            return CommandResult(0, "1.2.3")
        assert arguments == [
            "--profile",
            "codex-paper-reading",
            "auth",
            "status",
            "--json",
            "--verify",
        ]
        return CommandResult(
            0,
            valid_status.replace('"identity": "user",', ""),
        )

    with tempfile.TemporaryDirectory(prefix="feishu-preflight-test-") as directory:
        dedicated_config_dir = Path(directory) / "dedicated-config"
        dedicated_config_dir.mkdir(mode=0o700)
        dedicated_data_dir = dedicated_config_dir / "data"
        dedicated_data_dir.mkdir(mode=0o700)
        original_environment = os.environ.copy()
        try:
            os.environ["LARKSUITE_CLI_APP_SECRET"] = secret
            os.environ["LARKSUITE_CLI_PROXY_ENABLE"] = "true"
            os.environ["LARKSUITE_CLI_PROXY_ADDRESS"] = "https://127.0.0.1:9443"
            os.environ["LARKSUITE_CLI_CA_PATH"] = secret
            os.environ["LARKSUITE_CLI_PROFILE"] = "ambient-profile"
            os.environ["HTTPS_PROXY"] = "https://127.0.0.1:9443"
            os.environ["SSL_CERT_FILE"] = secret
            os.environ["OPENCLAW_HOME"] = "must-not-survive"
            os.environ["OPENCLAW_CLI"] = "must-not-survive"
            os.environ["HERMES_SESSION_KEY"] = secret
            environment_probe = run_command(
                sys.executable,
                [
                    "-c",
                    (
                        "import json, os; "
                        "print(json.dumps({"
                        "'config': bool(os.getenv('LARKSUITE_CLI_CONFIG_DIR')),"
                        "'data': bool(os.getenv('LARKSUITE_CLI_DATA_DIR')),"
                        "'secret': bool(os.getenv('LARKSUITE_CLI_APP_SECRET')),"
                        "'proxy': any(os.getenv(k) for k in ("
                        "'LARKSUITE_CLI_PROXY_ENABLE',"
                        "'LARKSUITE_CLI_PROXY_ADDRESS',"
                        "'LARKSUITE_CLI_CA_PATH',"
                        "'LARKSUITE_CLI_PROFILE')),"
                        "'generic_transport': any(os.getenv(k) for k in ("
                        "'HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','NO_PROXY',"
                        "'SSL_CERT_FILE','SSL_CERT_DIR')),"
                        "'workspace': any(os.getenv(k) for k in ("
                        "'OPENCLAW_HOME','OPENCLAW_CLI',"
                        "'HERMES_SESSION_KEY'))"
                        "}))"
                    ),
                ],
                3,
                config_dir=os.fspath(dedicated_config_dir),
                data_dir=os.fspath(dedicated_data_dir),
            )
        finally:
            os.environ.clear()
            os.environ.update(original_environment)
        assert environment_probe.returncode == 0
        assert json.loads(environment_probe.stdout) == {
            "config": True,
            "data": True,
            "secret": False,
            "proxy": False,
            "generic_transport": False,
            "workspace": False,
        }

        fake_executable = Path(directory) / (
            "lark-cli.exe" if os.name == "nt" else "lark-cli"
        )
        fake_executable.write_bytes(b"verified fake executable")
        with contextlib.suppress(OSError):
            fake_executable.chmod(0o700)
        executable_digest = _sha256_file(os.fspath(fake_executable))
        common = {
            "timeout_seconds": 3,
            "verify": True,
            "lark_cli_path": os.fspath(fake_executable),
            "approved_executable_sha256": executable_digest,
            "profile": "codex-paper-reading",
            "expected_brand": "feishu",
        }
        hash_mismatch = collect_preflight(
            **{**common, "approved_executable_sha256": "0" * 64},
            runner=lambda *_: (_ for _ in ()).throw(
                AssertionError("a hash-mismatched executable must not run")
            ),
        )
        assert hash_mismatch["state"] == "cli_review_required"
        assert hash_mismatch["checks"]["lark_cli"]["executed"] is False

        confirmation = collect_preflight(
            **common,
            runner=fake_runner,
        )
        assert confirmation["state"] == "identity_confirmation_required"
        fingerprint = confirmation["checks"]["identity"]
        assert fingerprint["confirmed"] is False

        identity_mismatch = collect_preflight(
            **common,
            expected_app_id_sha256="0" * 64,
            expected_user_open_id_sha256=fingerprint["user_open_id_sha256"],
            runner=fake_runner,
        )
        assert identity_mismatch["state"] == "identity_mismatch"

        report = collect_preflight(
            **common,
            expected_app_id_sha256=fingerprint["app_id_sha256"],
            expected_user_open_id_sha256=fingerprint["user_open_id_sha256"],
            runner=fake_runner,
        )
        assert report["ok"] is True
        assert report["state_recognized"] is True
        assert report["state"] == "authorization_ready"
        assert report["authorization_ready"] is True
        assert report["delivery_verified"] is False
        assert secret not in json.dumps(report)
        assert _report_exit_code(report) == 0

        scope_incomplete = collect_preflight(
            **common,
            expected_app_id_sha256=fingerprint["app_id_sha256"],
            expected_user_open_id_sha256=fingerprint["user_open_id_sha256"],
            runner=missing_scope_runner,
        )
        assert scope_incomplete["ok"] is False
        assert scope_incomplete["state_recognized"] is True
        assert scope_incomplete["state"] == "scope_incomplete"
        assert scope_incomplete["authorization_ready"] is False

        unknown = collect_preflight(
            **common,
            expected_app_id_sha256=fingerprint["app_id_sha256"],
            expected_user_open_id_sha256=fingerprint["user_open_id_sha256"],
            runner=no_identity_runner,
        )
        assert unknown["ok"] is False
        assert unknown["state_recognized"] is False
        assert unknown["state"] == "unknown"
        assert _report_exit_code(unknown) == 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Read-only Feishu connection preflight. Probe an existing lark-cli "
            "first, then verify its user identity and minimum document scopes. "
            "The script never installs, logs in, or changes configuration."
        )
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=(
            "per-command timeout in seconds "
            f"(default: {DEFAULT_TIMEOUT_SECONDS:g}, max: {MAX_TIMEOUT_SECONDS:g})"
        ),
    )
    parser.add_argument(
        "--lark-cli",
        help=(
            "absolute path to an approved standalone lark-cli executable; "
            "when omitted, PATH is inspected but no candidate is executed"
        ),
    )
    parser.add_argument(
        "--approved-executable-sha256",
        help="exact executable SHA-256 returned by the verified installer",
    )
    parser.add_argument(
        "--profile",
        help="exact named lark-cli profile to inspect",
    )
    parser.add_argument(
        "--config-dir",
        help=(
            "optional absolute dedicated lark-cli configuration directory "
            "created by the guided setup helper"
        ),
    )
    parser.add_argument(
        "--data-dir",
        help=(
            "optional absolute protected-data directory returned by the fresh "
            "setup helper"
        ),
    )
    parser.add_argument(
        "--expected-brand",
        choices=sorted(RECOGNIZED_BRANDS),
        help="expected platform brand for the selected profile",
    )
    parser.add_argument(
        "--expected-app-id-sha256",
        help="previously confirmed safe app-ID fingerprint",
    )
    parser.add_argument(
        "--expected-user-open-id-sha256",
        help="previously confirmed safe user open-ID fingerprint",
    )
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help=(
            "omit --verify from 'lark-cli auth status --json'; useful for a "
            "strictly local status check"
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit JSON output (the default; accepted for explicit invocation)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run deterministic parser, redaction, and classification fixtures",
    )
    args = parser.parse_args()
    if not 0 < args.timeout_seconds <= MAX_TIMEOUT_SECONDS:
        parser.error(
            f"--timeout-seconds must be greater than 0 and at most "
            f"{MAX_TIMEOUT_SECONDS:g}"
        )
    return args


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        print(json.dumps({"self_test": "passed"}, sort_keys=True))
        return 0

    try:
        report = collect_preflight(
            timeout_seconds=args.timeout_seconds,
            verify=not args.no_verify,
            lark_cli_path=args.lark_cli,
            approved_executable_sha256=args.approved_executable_sha256,
            profile=args.profile,
            expected_brand=args.expected_brand,
            expected_app_id_sha256=args.expected_app_id_sha256,
            expected_user_open_id_sha256=args.expected_user_open_id_sha256,
            config_dir=args.config_dir,
            data_dir=args.data_dir,
        )
    except Exception:
        report = {
            "schema_version": SCHEMA_VERSION,
            "ok": False,
            "state_recognized": False,
            "state": "unknown",
            "authorization_ready": False,
            "delivery_verified": False,
            "reason": "unexpected_preflight_failure",
            "checks": {},
            "next_action": _next_action("unknown"),
            "safety": {
                "read_only": True,
                "raw_command_output_included": False,
            },
        }
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return _report_exit_code(report)


if __name__ == "__main__":
    raise SystemExit(main())
