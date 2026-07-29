#!/usr/bin/env python3
"""Create one isolated Feishu/Lark CLI profile without exposing setup secrets.

This helper never runs ``config init`` against the shared ``~/.lark-cli``
directory. It creates a dedicated, private directory under an explicit parent,
contains the child process, discards all raw child output, and opens only a
strictly validated official verification URL in the user's browser.
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
import stat
import subprocess
import sys
import tempfile
import threading
import time
import uuid
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO, Callable, Mapping
from urllib.parse import parse_qsl, urlsplit

from feishu_process_environment import build_isolated_cli_environment
from run_feishu_auth import (
    _pid_is_alive,
    _start_contained_process,
    _terminate_owned_child,
    _validated_executable,
)


DEFAULT_TIMEOUT_SECONDS = 660.0
MAX_TIMEOUT_SECONDS = 900.0
STALE_ACTIVE_GRACE_SECONDS = 5.0
MAX_STATE_BYTES = 16 * 1024
MAX_CONFIG_BYTES = 64 * 1024
MAX_STREAM_WINDOW = 8 * 1024
PROFILE_PREFIX = "codex-paper-reading-"
URL_PATTERN = re.compile(
    rb"https://(?:open\.feishu\.cn|open\.larksuite\.com)"
    rb"/page/cli\?[^\s<>\"']{1,2048}"
)
PROFILE_PATTERN = re.compile(r"codex-paper-reading-[0-9a-f]{32}")
APP_ID_PATTERN = re.compile(r"cli_[A-Za-z0-9]{1,252}")
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")

ACTIVE_STATES = frozenset({"starting", "pending"})
TERMINAL_STATES = frozenset(
    {"succeeded", "failed", "timed_out", "cancelled", "expired"}
)
VALID_STATES = frozenset({*ACTIVE_STATES, *TERMINAL_STATES, "cleaned", "absent"})
VALID_REASONS = frozenset(
    {
        "config_process_starting",
        "awaiting_user_verification",
        "configuration_initialized",
        "lark_cli_path_invalid",
        "lark_cli_hash_mismatch",
        "config_parent_invalid",
        "state_path_invalid",
        "state_file_conflict",
        "config_directory_creation_failed",
        "config_directory_identity_changed",
        "config_launch_failed",
        "browser_open_failed",
        "verification_url_missing",
        "config_process_failed",
        "config_verification_failed",
        "configuration_timed_out",
        "configuration_cancelled",
        "unexpected_configuration_failure",
        "configuration_expired",
        "configuration_process_not_running",
        "state_file_invalid",
        "no_state_file",
        "cleanup_refused_active_configuration",
        "cleanup_refused_successful_configuration",
        "cleanup_refused_config_present",
        "state_and_empty_config_removed",
    }
)
STATE_FIELDS = frozenset(
    {
        "state",
        "reason",
        "brand",
        "profile",
        "config_dir",
        "config_dir_identity_sha256",
        "data_dir",
        "data_dir_identity_sha256",
        "executable_sha256",
        "pid",
        "started_at",
        "updated_at",
        "finished_at",
        "expires_at",
        "browser_opened",
    }
)
OFFICIAL_OPEN_HOST = {
    "feishu": "open.feishu.cn",
    "lark": "open.larksuite.com",
}
UNBOUND_FAILURE_REASONS = frozenset(
    {
        "lark_cli_path_invalid",
        "lark_cli_hash_mismatch",
        "config_parent_invalid",
        "state_path_invalid",
        "state_file_conflict",
        "config_directory_creation_failed",
        "state_file_invalid",
        "unexpected_configuration_failure",
    }
)
Emitter = Callable[[dict[str, Any]], None]
BrowserOpener = Callable[[str], bool]
ProcessFactory = Callable[..., Any]
CancelCheck = Callable[[], bool]


@dataclass(frozen=True)
class DirectoryIdentity:
    path: Path
    device: int
    inode: int
    attributes: int


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


def _sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validated_bound_executable(value: str | None) -> str | None:
    executable = _validated_executable(value)
    if executable is None:
        return None
    try:
        metadata = Path(executable).lstat()
    except OSError:
        return None
    if _is_reparse_point(metadata):
        return None
    return executable


def _same_path(left: Path, right: Path) -> bool:
    left_text = os.path.normcase(os.path.abspath(os.fspath(left)))
    right_text = os.path.normcase(os.path.abspath(os.fspath(right)))
    return left_text == right_text


def _is_reparse_point(metadata: os.stat_result) -> bool:
    attributes = int(getattr(metadata, "st_file_attributes", 0))
    reparse_flag = int(getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))
    return bool(attributes & reparse_flag)


def _directory_identity(value: Path) -> DirectoryIdentity | None:
    try:
        metadata = value.lstat()
        resolved = value.resolve(strict=True)
        if (
            value.is_symlink()
            or _is_reparse_point(metadata)
            or not stat.S_ISDIR(metadata.st_mode)
            or not _same_path(value, resolved)
        ):
            return None
    except OSError:
        return None
    return DirectoryIdentity(
        path=resolved,
        device=int(metadata.st_dev),
        inode=int(metadata.st_ino),
        attributes=int(getattr(metadata, "st_file_attributes", 0)),
    )


def _same_directory_identity(expected: DirectoryIdentity) -> bool:
    current = _directory_identity(expected.path)
    return current == expected


def _directory_identity_sha256(identity: DirectoryIdentity) -> str:
    canonical = os.path.normcase(os.path.abspath(os.fspath(identity.path)))
    encoded = json.dumps(
        {
            "domain": "feishu-paper-reading/config-dir-identity/v1",
            "path": canonical,
            "device": identity.device,
            "inode": identity.inode,
            "attributes": identity.attributes,
        },
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _validated_existing_directory(value: str | Path | None) -> Path | None:
    if value is None:
        return None
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        return None
    identity = _directory_identity(candidate)
    if identity is None:
        return None
    return identity.path


def _validated_state_path(value: str | Path | None) -> Path | None:
    if value is None:
        return None
    candidate = Path(value).expanduser()
    if not candidate.is_absolute() or candidate.name in {"", ".", ".."}:
        return None
    parent = _validated_existing_directory(candidate.parent)
    if parent is None:
        return None
    final = parent / candidate.name
    if final.exists() or final.is_symlink():
        try:
            metadata = final.lstat()
        except OSError:
            return None
        if (
            final.is_symlink()
            or _is_reparse_point(metadata)
            or not stat.S_ISREG(metadata.st_mode)
        ):
            return None
    return final


def _validated_config_dir(value: str | Path | None) -> Path | None:
    candidate = _validated_existing_directory(value)
    if candidate is None or not PROFILE_PATTERN.fullmatch(candidate.name):
        return None
    return candidate


def _make_directory_owner_private(path: Path) -> bool:
    if os.name != "nt":
        try:
            os.chmod(path, 0o700)
            metadata = path.lstat()
        except OSError:
            return False
        return not path.is_symlink() and not metadata.st_mode & 0o077

    try:
        import ctypes
        from ctypes import wintypes

        class SID_AND_ATTRIBUTES(ctypes.Structure):
            _fields_ = [
                ("Sid", ctypes.c_void_p),
                ("Attributes", wintypes.DWORD),
            ]

        class TOKEN_USER(ctypes.Structure):
            _fields_ = [("User", SID_AND_ATTRIBUTES)]

        advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        advapi32.OpenProcessToken.argtypes = [
            wintypes.HANDLE,
            wintypes.DWORD,
            ctypes.POINTER(wintypes.HANDLE),
        ]
        advapi32.OpenProcessToken.restype = wintypes.BOOL
        advapi32.GetTokenInformation.argtypes = [
            wintypes.HANDLE,
            ctypes.c_int,
            ctypes.c_void_p,
            wintypes.DWORD,
            ctypes.POINTER(wintypes.DWORD),
        ]
        advapi32.GetTokenInformation.restype = wintypes.BOOL
        advapi32.ConvertSidToStringSidW.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_void_p),
        ]
        advapi32.ConvertSidToStringSidW.restype = wintypes.BOOL
        advapi32.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes = [
            wintypes.LPCWSTR,
            wintypes.DWORD,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.POINTER(wintypes.DWORD),
        ]
        advapi32.ConvertStringSecurityDescriptorToSecurityDescriptorW.restype = (
            wintypes.BOOL
        )
        advapi32.SetFileSecurityW.argtypes = [
            wintypes.LPCWSTR,
            wintypes.DWORD,
            ctypes.c_void_p,
        ]
        advapi32.SetFileSecurityW.restype = wintypes.BOOL
        kernel32.GetCurrentProcess.restype = wintypes.HANDLE
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel32.CloseHandle.restype = wintypes.BOOL
        kernel32.LocalFree.argtypes = [ctypes.c_void_p]
        kernel32.LocalFree.restype = ctypes.c_void_p

        token = wintypes.HANDLE()
        if not advapi32.OpenProcessToken(
            kernel32.GetCurrentProcess(),
            0x0008,
            ctypes.byref(token),
        ):
            return False
        sid_text_pointer = ctypes.c_void_p()
        descriptor = ctypes.c_void_p()
        try:
            required = wintypes.DWORD()
            advapi32.GetTokenInformation(
                token,
                1,
                None,
                0,
                ctypes.byref(required),
            )
            if not required.value:
                return False
            buffer = ctypes.create_string_buffer(required.value)
            if not advapi32.GetTokenInformation(
                token,
                1,
                buffer,
                required.value,
                ctypes.byref(required),
            ):
                return False
            token_user = ctypes.cast(
                buffer,
                ctypes.POINTER(TOKEN_USER),
            ).contents
            if not advapi32.ConvertSidToStringSidW(
                token_user.User.Sid,
                ctypes.byref(sid_text_pointer),
            ):
                return False
            sid_text = ctypes.cast(
                sid_text_pointer,
                ctypes.c_wchar_p,
            ).value
            if not sid_text:
                return False
            sddl = f"D:P(A;OICI;FA;;;{sid_text})"
            if not advapi32.ConvertStringSecurityDescriptorToSecurityDescriptorW(
                sddl,
                1,
                ctypes.byref(descriptor),
                None,
            ):
                return False
            return bool(
                advapi32.SetFileSecurityW(
                    os.fspath(path),
                    0x00000004 | 0x80000000,
                    descriptor,
                )
            )
        finally:
            if descriptor.value:
                kernel32.LocalFree(descriptor)
            if sid_text_pointer.value:
                kernel32.LocalFree(sid_text_pointer)
            kernel32.CloseHandle(token)
    except Exception:
        return False


def _sanitize_state(
    payload: Any,
    *,
    brand: str | None = None,
    profile: str | None = None,
    config_dir: Path | None = None,
    data_dir: Path | None = None,
    approved_executable_sha256: str | None = None,
) -> dict[str, Any] | None:
    if not isinstance(payload, dict) or not set(payload).issubset(STATE_FIELDS):
        return None
    state = payload.get("state")
    reason = payload.get("reason")
    if state not in VALID_STATES or reason not in VALID_REASONS:
        return None
    result: dict[str, Any] = {"state": state, "reason": reason}

    binding_values = (
        payload.get("brand"),
        payload.get("profile"),
        payload.get("config_dir"),
        payload.get("config_dir_identity_sha256"),
        payload.get("data_dir"),
        payload.get("data_dir_identity_sha256"),
        payload.get("executable_sha256"),
    )
    binding_present = all(value is not None for value in binding_values)
    if any(value is not None for value in binding_values) and not binding_present:
        return None
    binding_required = (
        state in ACTIVE_STATES
        or state in {"succeeded", "timed_out", "cancelled", "expired"}
        or (
            state == "failed"
            and reason not in UNBOUND_FAILURE_REASONS
        )
    )
    if binding_required:
        if not binding_present:
            return None
    if binding_present:
        (
            state_brand,
            state_profile,
            state_config_dir,
            state_config_identity_sha256,
            state_data_dir,
            state_data_identity_sha256,
            state_sha256,
        ) = binding_values
        if state_brand not in OFFICIAL_OPEN_HOST:
            return None
        if brand is not None and state_brand != brand:
            return None
        if not isinstance(state_profile, str) or not PROFILE_PATTERN.fullmatch(
            state_profile
        ):
            return None
        if profile is not None and state_profile != profile:
            return None
        if not isinstance(state_config_dir, str):
            return None
        state_directory = Path(state_config_dir)
        if not state_directory.is_absolute() or state_directory.name != state_profile:
            return None
        if config_dir is not None and not _same_path(state_directory, config_dir):
            return None
        if not isinstance(state_data_dir, str):
            return None
        state_data_directory = Path(state_data_dir)
        if (
            not state_data_directory.is_absolute()
            or state_data_directory.name != "data"
            or not _same_path(state_data_directory.parent, state_directory)
        ):
            return None
        if data_dir is not None and not _same_path(state_data_directory, data_dir):
            return None
        if (
            not isinstance(state_config_identity_sha256, str)
            or not SHA256_PATTERN.fullmatch(state_config_identity_sha256)
        ):
            return None
        if config_dir is not None:
            current_identity = _directory_identity(config_dir)
            if (
                current_identity is None
                or _directory_identity_sha256(current_identity)
                != state_config_identity_sha256
            ):
                return None
        if (
            not isinstance(state_data_identity_sha256, str)
            or not SHA256_PATTERN.fullmatch(state_data_identity_sha256)
        ):
            return None
        if data_dir is not None:
            current_data_identity = _directory_identity(data_dir)
            if (
                current_data_identity is None
                or _directory_identity_sha256(current_data_identity)
                != state_data_identity_sha256
            ):
                return None
        if not isinstance(state_sha256, str) or not SHA256_PATTERN.fullmatch(
            state_sha256
        ):
            return None
        if (
            approved_executable_sha256 is not None
            and state_sha256 != approved_executable_sha256.casefold()
        ):
            return None
        result.update(
            {
                "brand": state_brand,
                "profile": state_profile,
                "config_dir": os.fspath(state_directory),
                "config_dir_identity_sha256": state_config_identity_sha256,
                "data_dir": os.fspath(state_data_directory),
                "data_dir_identity_sha256": state_data_identity_sha256,
                "executable_sha256": state_sha256,
            }
        )

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
    if "browser_opened" in payload:
        if payload["browser_opened"] is not True or state != "pending":
            return None
        result["browser_opened"] = True
    return result


def _state_bytes(payload: dict[str, Any]) -> bytes:
    sanitized = _sanitize_state(payload)
    if sanitized is None:
        raise ValueError("invalid safe configuration state")
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
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
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
    brand: str | None = None,
    profile: str | None = None,
    config_dir: Path | None = None,
    data_dir: Path | None = None,
    approved_executable_sha256: str | None = None,
) -> dict[str, Any] | None:
    try:
        metadata = path.lstat()
        if (
            path.is_symlink()
            or _is_reparse_point(metadata)
            or not stat.S_ISREG(metadata.st_mode)
        ):
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
        config_dir=config_dir,
        data_dir=data_dir,
        approved_executable_sha256=approved_executable_sha256,
    )


def _emit_json(payload: dict[str, Any]) -> None:
    safe = _sanitize_state(payload)
    if safe is None:
        safe = {
            "state": "failed",
            "reason": "unexpected_configuration_failure",
            "updated_at": _utc_timestamp(),
        }
    print(json.dumps(safe, ensure_ascii=True, sort_keys=True), flush=True)


def _binding(
    *,
    brand: str,
    profile: str,
    config_dir: Path,
    config_identity: DirectoryIdentity,
    data_dir: Path,
    data_identity: DirectoryIdentity,
    executable_sha256: str,
) -> dict[str, str]:
    return {
        "brand": brand,
        "profile": profile,
        "config_dir": os.fspath(config_dir),
        "config_dir_identity_sha256": _directory_identity_sha256(
            config_identity
        ),
        "data_dir": os.fspath(data_dir),
        "data_dir_identity_sha256": _directory_identity_sha256(data_identity),
        "executable_sha256": executable_sha256,
    }


def _terminal_state(
    *,
    state: str,
    reason: str,
    started_at: str,
    binding: Mapping[str, str],
    pid: int | None,
) -> dict[str, Any]:
    now = _utc_timestamp()
    result: dict[str, Any] = {
        "state": state,
        "reason": reason,
        "started_at": started_at,
        "updated_at": now,
        "finished_at": now,
        **binding,
    }
    if pid is not None:
        result["pid"] = pid
    return result


def _create_isolated_directory(parent: Path) -> tuple[str, Path]:
    for _ in range(32):
        profile = PROFILE_PREFIX + uuid.uuid4().hex
        candidate = parent / profile
        try:
            os.mkdir(candidate, 0o700)
        except FileExistsError:
            continue
        if not _make_directory_owner_private(candidate):
            with contextlib.suppress(OSError):
                os.rmdir(candidate)
            raise PermissionError("could not make configuration directory private")
        data_dir = candidate / "data"
        try:
            os.mkdir(data_dir, 0o700)
            if not _make_directory_owner_private(data_dir):
                raise PermissionError("could not make data directory private")
        except Exception:
            with contextlib.suppress(OSError):
                os.rmdir(candidate)
            raise
        identity = _directory_identity(candidate)
        data_identity = _directory_identity(data_dir)
        if identity is None or data_identity is None:
            with contextlib.suppress(OSError):
                os.rmdir(data_dir)
                os.rmdir(candidate)
            continue
        return profile, identity.path
    raise FileExistsError("could not reserve a unique configuration directory")


def _build_environment(
    config_dir: Path,
    base_environment: Mapping[str, str] | None = None,
) -> dict[str, str]:
    return build_isolated_cli_environment(
        config_dir=os.fspath(config_dir),
        data_dir=os.fspath(config_dir / "data"),
        base_environment=base_environment,
    )


def _command_for(executable: str, profile: str, brand: str) -> list[str]:
    return [
        executable,
        "config",
        "init",
        "--new",
        "--name",
        profile,
        "--brand",
        brand,
    ]


def _validated_verification_url(value: str, brand: str) -> str | None:
    if not isinstance(value, str) or not 1 <= len(value) <= 2048:
        return None
    if any(ord(character) < 32 for character in value):
        return None
    try:
        parsed = urlsplit(value)
        port = parsed.port
        pairs = parse_qsl(
            parsed.query,
            keep_blank_values=True,
            strict_parsing=True,
            max_num_fields=8,
        )
    except (ValueError, UnicodeError):
        return None
    if (
        parsed.scheme.casefold() != "https"
        or (parsed.hostname or "").casefold().rstrip(".")
        != OFFICIAL_OPEN_HOST.get(brand)
        or parsed.username is not None
        or parsed.password is not None
        or port not in {None, 443}
        or parsed.path != "/page/cli"
        or parsed.fragment
        or "\\" in parsed.path
    ):
        return None
    keys = [key for key, _ in pairs]
    if (
        set(keys) != {"user_code", "lpv", "ocv", "from"}
        or len(keys) != len(set(keys))
    ):
        return None
    query = dict(pairs)
    user_code = query.get("user_code", "")
    if not re.fullmatch(r"[A-Za-z0-9_-]{4,128}", user_code):
        return None
    for key in ("lpv", "ocv"):
        if not re.fullmatch(r"[A-Za-z0-9._+-]{1,64}", query[key]):
            return None
    if query["from"] != "cli":
        return None
    return value


def _scan_stream(
    stream: BinaryIO,
    events: queue.Queue[tuple[str, str | None]],
    *,
    brand: str,
) -> None:
    window = b""
    seen: set[bytes] = set()
    try:
        while True:
            chunk = stream.read(4096)
            if not chunk:
                break
            window = (window + chunk)[-MAX_STREAM_WINDOW:]
            for match in URL_PATTERN.finditer(window):
                raw_url = match.group(0).rstrip(b".,);]")
                if raw_url in seen:
                    continue
                seen.add(raw_url)
                try:
                    candidate = raw_url.decode("ascii")
                except UnicodeDecodeError:
                    continue
                validated = _validated_verification_url(candidate, brand)
                if validated is not None:
                    events.put(("url", validated))
    except Exception:
        pass
    finally:
        events.put(("done", None))


def _verify_isolated_config(config_dir: Path, profile: str, brand: str) -> bool:
    if _validated_config_dir(config_dir) is None:
        return False
    config_path = config_dir / "config.json"
    try:
        metadata = config_path.lstat()
        if (
            config_path.is_symlink()
            or _is_reparse_point(metadata)
            or not stat.S_ISREG(metadata.st_mode)
            or not 0 < metadata.st_size <= MAX_CONFIG_BYTES
        ):
            return False
        if os.name != "nt" and metadata.st_mode & 0o077:
            return False
        with config_path.open("rb") as handle:
            data = handle.read(MAX_CONFIG_BYTES + 1)
        payload = json.loads(data.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return False
    if not isinstance(payload, dict) or not set(payload).issubset(
        {
            "strictMode",
            "riskControl",
            "currentApp",
            "previousApp",
            "apps",
        }
    ):
        return False
    apps = payload.get("apps")
    if not isinstance(apps, list) or len(apps) != 1:
        return False
    app = apps[0]
    if not isinstance(app, dict) or not set(app).issubset(
        {
            "name",
            "appId",
            "appSecret",
            "brand",
            "lang",
            "defaultAs",
            "strictMode",
            "users",
        }
    ):
        return False
    if app.get("name") != profile or app.get("brand") != brand:
        return False
    app_id = app.get("appId")
    if not isinstance(app_id, str) or not APP_ID_PATTERN.fullmatch(app_id):
        return False
    secret_ref = app.get("appSecret")
    if (
        not isinstance(secret_ref, dict)
        or not set(secret_ref).issubset({"source", "provider", "id"})
        or secret_ref.get("source") != "keychain"
        or secret_ref.get("id") != f"appsecret:{app_id}"
        or secret_ref.get("provider") not in {None, ""}
    ):
        return False
    users = app.get("users")
    if not isinstance(users, list) or users:
        return False
    current_app = payload.get("currentApp")
    if current_app not in {None, "", profile, app_id}:
        return False
    return True


def _default_browser_opener(url: str) -> bool:
    return bool(webbrowser.open_new_tab(url))


def run_config_init(
    *,
    state_path: Path,
    config_parent: Path,
    brand: str,
    timeout_seconds: float,
    lark_cli_path: str,
    approved_executable_sha256: str,
    consent_confirmed: bool,
    process_factory: ProcessFactory = subprocess.Popen,
    browser_opener: BrowserOpener = _default_browser_opener,
    cancel_requested: CancelCheck | None = None,
    base_environment: Mapping[str, str] | None = None,
    emit: Emitter = _emit_json,
) -> int:
    """Run one isolated, credential-silent app registration."""

    validated_state_path = _validated_state_path(state_path)
    if (
        validated_state_path is None
        or not _same_path(validated_state_path, state_path)
    ):
        emit(
            {
                "state": "failed",
                "reason": "state_path_invalid",
                "updated_at": _utc_timestamp(),
            }
        )
        return 3
    state_path = validated_state_path
    if not consent_confirmed:
        emit(
            {
                "state": "failed",
                "reason": "unexpected_configuration_failure",
                "updated_at": _utc_timestamp(),
            }
        )
        return 3
    executable = _validated_bound_executable(lark_cli_path)
    expected_sha256 = approved_executable_sha256.casefold()
    if (
        brand not in OFFICIAL_OPEN_HOST
        or executable is None
        or not SHA256_PATTERN.fullmatch(expected_sha256)
    ):
        emit(
            {
                "state": "failed",
                "reason": "lark_cli_path_invalid",
                "updated_at": _utc_timestamp(),
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
            }
        )
        return 3
    validated_parent = _validated_existing_directory(config_parent)
    parent_identity = (
        None if validated_parent is None else _directory_identity(validated_parent)
    )
    if validated_parent is None or parent_identity is None:
        emit(
            {
                "state": "failed",
                "reason": "config_parent_invalid",
                "updated_at": _utc_timestamp(),
            }
        )
        return 3

    try:
        profile, config_dir = _create_isolated_directory(validated_parent)
    except OSError:
        emit(
            {
                "state": "failed",
                "reason": "config_directory_creation_failed",
                "updated_at": _utc_timestamp(),
            }
        )
        return 4
    config_identity = _directory_identity(config_dir)
    data_identity = _directory_identity(config_dir / "data")
    if config_identity is None or data_identity is None:
        with contextlib.suppress(OSError):
            os.rmdir(config_dir / "data")
            os.rmdir(config_dir)
        emit(
            {
                "state": "failed",
                "reason": "config_directory_creation_failed",
                "updated_at": _utc_timestamp(),
            }
        )
        return 4
    binding = _binding(
        brand=brand,
        profile=profile,
        config_dir=config_dir,
        config_identity=config_identity,
        data_dir=config_dir / "data",
        data_identity=data_identity,
        executable_sha256=actual_sha256,
    )
    started_epoch = time.time()
    deadline = started_epoch + timeout_seconds
    started_at = _utc_timestamp(started_epoch)
    starting = {
        "state": "starting",
        "reason": "config_process_starting",
        "started_at": started_at,
        "updated_at": started_at,
        "expires_at": _utc_timestamp(deadline),
        **binding,
    }
    try:
        _write_initial_state(state_path, starting)
    except FileExistsError:
        with contextlib.suppress(OSError):
            os.rmdir(config_dir / "data")
            os.rmdir(config_dir)
        emit(
            {
                "state": "failed",
                "reason": "state_file_conflict",
                "updated_at": _utc_timestamp(),
            }
        )
        return 4
    except OSError:
        with contextlib.suppress(OSError):
            os.rmdir(config_dir / "data")
            os.rmdir(config_dir)
        emit(
            {
                "state": "failed",
                "reason": "state_path_invalid",
                "updated_at": _utc_timestamp(),
            }
        )
        return 4
    emit(starting)

    command = _command_for(executable, profile, brand)
    environment = _build_environment(config_dir, base_environment)
    directories_unchanged = all(
        _same_directory_identity(identity)
        for identity in (parent_identity, config_identity, data_identity)
    )
    try:
        launch_sha256 = _sha256_file(executable)
    except OSError:
        launch_sha256 = ""
    if not directories_unchanged or launch_sha256 != expected_sha256:
        terminal = _terminal_state(
            state="failed",
            reason=(
                "config_directory_identity_changed"
                if not directories_unchanged
                else "lark_cli_hash_mismatch"
            ),
            started_at=started_at,
            binding=binding,
            pid=None,
        )
        _replace_state(state_path, terminal)
        emit(terminal)
        return 3
    containment: Any | None = None
    try:
        process, containment = _start_contained_process(
            command,
            process_factory=process_factory,
            process_kwargs={
                "stdin": subprocess.DEVNULL,
                "stdout": subprocess.PIPE,
                "stderr": subprocess.PIPE,
                "bufsize": 0,
                "env": environment,
            },
        )
    except Exception:
        terminal = _terminal_state(
            state="failed",
            reason="config_launch_failed",
            started_at=started_at,
            binding=binding,
            pid=None,
        )
        _replace_state(state_path, terminal)
        emit(terminal)
        return 3

    pid = int(process.pid)
    running = {
        **starting,
        "pid": pid,
        "updated_at": _utc_timestamp(),
    }
    _replace_state(state_path, running)
    events: queue.Queue[tuple[str, str | None]] = queue.Queue()
    threads = [
        threading.Thread(
            target=_scan_stream,
            args=(process.stdout, events),
            kwargs={"brand": brand},
            daemon=True,
        ),
        threading.Thread(
            target=_scan_stream,
            args=(process.stderr, events),
            kwargs={"brand": brand},
            daemon=True,
        ),
    ]
    for thread in threads:
        thread.start()

    done_streams = 0
    browser_opened = False
    terminal_state: dict[str, Any] | None = None
    returncode: int | None = None
    try:
        while terminal_state is None:
            if cancel_requested is not None and cancel_requested():
                _terminate_owned_child(process)
                terminal_state = _terminal_state(
                    state="cancelled",
                    reason="configuration_cancelled",
                    started_at=started_at,
                    binding=binding,
                    pid=pid,
                )
                break
            remaining = deadline - time.time()
            if remaining <= 0:
                _terminate_owned_child(process)
                terminal_state = _terminal_state(
                    state="timed_out",
                    reason="configuration_timed_out",
                    started_at=started_at,
                    binding=binding,
                    pid=pid,
                )
                break
            try:
                event_type, event_value = events.get(
                    timeout=min(0.2, remaining)
                )
            except queue.Empty:
                event_type, event_value = "", None
            if event_type == "done":
                done_streams += 1
            elif event_type == "url" and event_value is not None:
                if not browser_opened:
                    try:
                        browser_opened = bool(browser_opener(event_value))
                    except Exception:
                        browser_opened = False
                    if not browser_opened:
                        _terminate_owned_child(process)
                        terminal_state = _terminal_state(
                            state="failed",
                            reason="browser_open_failed",
                            started_at=started_at,
                            binding=binding,
                            pid=pid,
                        )
                        break
                    pending = {
                        "state": "pending",
                        "reason": "awaiting_user_verification",
                        "browser_opened": True,
                        "pid": pid,
                        "started_at": started_at,
                        "updated_at": _utc_timestamp(),
                        "expires_at": _utc_timestamp(deadline),
                        **binding,
                    }
                    _replace_state(state_path, pending)
                    emit(pending)
                event_value = None
            returncode = process.poll()
            if returncode is not None and done_streams >= 2:
                directories_unchanged = all(
                    _same_directory_identity(identity)
                    for identity in (
                        parent_identity,
                        config_identity,
                        data_identity,
                    )
                )
                if returncode != 0:
                    reason = "config_process_failed"
                elif not browser_opened:
                    reason = "verification_url_missing"
                elif not directories_unchanged:
                    reason = "config_directory_identity_changed"
                elif not _verify_isolated_config(config_dir, profile, brand):
                    reason = "config_verification_failed"
                else:
                    reason = "configuration_initialized"
                terminal_state = _terminal_state(
                    state="succeeded" if reason == "configuration_initialized" else "failed",
                    reason=reason,
                    started_at=started_at,
                    binding=binding,
                    pid=pid,
                )
    except KeyboardInterrupt:
        _terminate_owned_child(process)
        terminal_state = _terminal_state(
            state="cancelled",
            reason="configuration_cancelled",
            started_at=started_at,
            binding=binding,
            pid=pid,
        )
    except Exception:
        _terminate_owned_child(process)
        terminal_state = _terminal_state(
            state="failed",
            reason="unexpected_configuration_failure",
            started_at=started_at,
            binding=binding,
            pid=pid,
        )
    finally:
        for thread in threads:
            thread.join(timeout=1.0)
        if containment is not None:
            containment.close()

    assert terminal_state is not None
    _replace_state(state_path, terminal_state)
    emit(terminal_state)
    return 0 if terminal_state["state"] == "succeeded" else 2


def status(
    state_path: Path,
    *,
    brand: str,
    profile: str,
    config_dir: Path,
    data_dir: Path,
    approved_executable_sha256: str,
    emit: Emitter = _emit_json,
) -> int:
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
        config_dir=config_dir,
        data_dir=data_dir,
        approved_executable_sha256=approved_executable_sha256,
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
    now = time.time()
    pid = current.get("pid")
    updated_at = _parse_timestamp(current.get("updated_at"))
    recently_updated = (
        updated_at is not None
        and now - updated_at < STALE_ACTIVE_GRACE_SECONDS
    )
    recorded_process_alive = isinstance(pid, int) and _pid_is_alive(pid)
    active_process_may_still_run = recorded_process_alive or (
        pid is None and recently_updated
    )
    expires_at = _parse_timestamp(current.get("expires_at"))
    if (
        current["state"] in ACTIVE_STATES
        and expires_at is not None
        and expires_at <= now
        and not active_process_may_still_run
    ):
        expired = {
            "state": "expired",
            "reason": "configuration_expired",
            "updated_at": _utc_timestamp(),
            "finished_at": _utc_timestamp(),
            **{
                key: current[key]
                for key in (
                    "brand",
                    "profile",
                    "config_dir",
                    "config_dir_identity_sha256",
                    "data_dir",
                    "data_dir_identity_sha256",
                    "executable_sha256",
                    "pid",
                    "started_at",
                )
                if key in current
            },
        }
        _replace_state(state_path, expired)
        emit(expired)
        return 2
    stale = (
        updated_at is not None
        and now - updated_at >= STALE_ACTIVE_GRACE_SECONDS
    )
    if (
        current["state"] in ACTIVE_STATES
        and isinstance(pid, int)
        and stale
        and not recorded_process_alive
    ):
        stopped = {
            "state": "failed",
            "reason": "configuration_process_not_running",
            "updated_at": _utc_timestamp(),
            "finished_at": _utc_timestamp(),
            **{
                key: current[key]
                for key in (
                    "brand",
                    "profile",
                    "config_dir",
                    "config_dir_identity_sha256",
                    "data_dir",
                    "data_dir_identity_sha256",
                    "executable_sha256",
                    "pid",
                    "started_at",
                )
                if key in current
            },
        }
        _replace_state(state_path, stopped)
        emit(stopped)
        return 2
    emit(current)
    return 0


def _directory_has_material_config(config_dir: Path) -> bool:
    try:
        for child in config_dir.iterdir():
            metadata = child.lstat()
            if _is_reparse_point(metadata):
                return True
            if child.name == "data" and child.is_dir() and not child.is_symlink():
                if next(child.iterdir(), None) is None:
                    continue
            return True
    except OSError:
        return True
    return False


def cleanup(
    state_path: Path,
    *,
    brand: str,
    profile: str,
    config_dir: Path,
    data_dir: Path,
    approved_executable_sha256: str,
    emit: Emitter = _emit_json,
) -> int:
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
        config_dir=config_dir,
        data_dir=data_dir,
        approved_executable_sha256=approved_executable_sha256,
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
    binding = {
        key: current[key]
        for key in (
            "brand",
            "profile",
            "config_dir",
            "config_dir_identity_sha256",
            "data_dir",
            "data_dir_identity_sha256",
            "executable_sha256",
        )
    }
    if current["state"] == "succeeded":
        response = {
            "state": "failed",
            "reason": "cleanup_refused_successful_configuration",
            "updated_at": _utc_timestamp(),
            "finished_at": _utc_timestamp(),
            **binding,
        }
        emit(response)
        return 2
    pid = current.get("pid")
    active = current["state"] in ACTIVE_STATES
    updated_at = _parse_timestamp(current.get("updated_at"))
    recently_updated = (
        updated_at is not None
        and time.time() - updated_at < STALE_ACTIVE_GRACE_SECONDS
    )
    recorded_process_alive = isinstance(pid, int) and _pid_is_alive(pid)
    if (
        recorded_process_alive
        or active
        or (pid is None and recently_updated)
    ):
        response = {
            "state": "failed",
            "reason": "cleanup_refused_active_configuration",
            "updated_at": _utc_timestamp(),
            "finished_at": _utc_timestamp(),
            **binding,
        }
        emit(response)
        return 2
    if _directory_has_material_config(config_dir):
        response = {
            "state": "failed",
            "reason": "cleanup_refused_config_present",
            "updated_at": _utc_timestamp(),
            "finished_at": _utc_timestamp(),
            **binding,
        }
        emit(response)
        return 2
    try:
        data_dir = config_dir / "data"
        if data_dir.exists():
            os.rmdir(data_dir)
        os.rmdir(config_dir)
        state_path.unlink()
    except OSError:
        emit(
            {
                "state": "failed",
                "reason": "unexpected_configuration_failure",
                "updated_at": _utc_timestamp(),
                "finished_at": _utc_timestamp(),
                **binding,
            }
        )
        return 2
    emit(
        {
            "state": "cleaned",
            "reason": "state_and_empty_config_removed",
            "updated_at": _utc_timestamp(),
            **binding,
        }
    )
    return 0


class _FakeProcess:
    def __init__(self, stdout: bytes, stderr: bytes, returncode: int = 0) -> None:
        self.stdout = io.BytesIO(stdout)
        self.stderr = io.BytesIO(stderr)
        self.pid = 424242
        self._returncode = returncode

    def poll(self) -> int:
        return self._returncode

    def wait(self, timeout: float | None = None) -> int:
        del timeout
        return self._returncode

    def terminate(self) -> None:
        self._returncode = -15

    def kill(self) -> None:
        self._returncode = -9


def run_self_test() -> None:
    user_code = "USER-CODE-2468"
    app_id = "cli_TestApp1234"
    app_secret = "APP_SECRET_MUST_NEVER_ESCAPE_8675309"
    device_code = "DEVICE_CODE_MUST_NEVER_ESCAPE_13579"
    verification_url = (
        "https://open.feishu.cn/page/cli"
        f"?user_code={user_code}&lpv=v1.0.79&ocv=v1.0.79&from=cli"
    )
    raw_stdout = json.dumps(
        {
            "appId": app_id,
            "appSecret": "****",
            "device_code": device_code,
        }
    ).encode("utf-8")
    raw_stderr = (
        f"secret={app_secret}\nOpen: {verification_url}\n"
        f"device_code={device_code}\n"
    ).encode("utf-8")

    with tempfile.TemporaryDirectory() as temporary_directory:
        root = Path(temporary_directory).resolve()
        config_parent = root / "profiles"
        config_parent.mkdir(mode=0o700)
        shared_config = config_parent / "config.json"
        shared_sentinel = '{"shared":"must remain unchanged"}\n'
        shared_config.write_text(shared_sentinel, encoding="utf-8")
        state_path = root / "setup-state.json"
        fake_lark_cli = root / (
            "lark-cli.exe" if os.name == "nt" else "lark-cli"
        )
        fake_lark_cli.touch(mode=0o700)
        with contextlib.suppress(OSError):
            fake_lark_cli.chmod(0o700)
        fake_digest = _sha256_file(os.fspath(fake_lark_cli))
        captured_commands: list[list[str]] = []
        captured_environments: list[dict[str, str]] = []
        browser_urls: list[str] = []
        emitted: list[dict[str, Any]] = []

        def fake_factory(command: list[str], **kwargs: Any) -> _FakeProcess:
            captured_commands.append(list(command))
            environment = dict(kwargs["env"])
            captured_environments.append(environment)
            isolated = Path(environment["LARKSUITE_CLI_CONFIG_DIR"])
            profile = command[command.index("--name") + 1]
            config_payload = {
                "apps": [
                    {
                        "name": profile,
                        "appId": app_id,
                        "appSecret": {
                            "source": "keychain",
                            "id": f"appsecret:{app_id}",
                        },
                        "brand": "feishu",
                        "users": [],
                    }
                ]
            }
            config_path = isolated / "config.json"
            config_path.write_text(
                json.dumps(config_payload),
                encoding="utf-8",
            )
            with contextlib.suppress(OSError):
                config_path.chmod(0o600)
            return _FakeProcess(raw_stdout, raw_stderr)

        base_environment = {
            "PATH": os.environ.get("PATH", ""),
            "OPENCLAW_HOME": app_secret,
            "HERMES_HOME": app_secret,
            "LARK_CHANNEL": "1",
            "LARKSUITE_CLI_APP_SECRET": app_secret,
            "LARKSUITE_CLI_USER_ACCESS_TOKEN": device_code,
            "LARKSUITE_CLI_PROFILE": "shared-profile",
            "LARKSUITE_CLI_PROXY_ENABLE": "true",
            "LARKSUITE_CLI_PROXY_ADDRESS": "https://127.0.0.1:9443",
            "LARKSUITE_CLI_CA_PATH": app_secret,
            "HTTPS_PROXY": "https://127.0.0.1:9443",
            "SSL_CERT_FILE": app_secret,
        }
        returncode = run_config_init(
            state_path=state_path,
            config_parent=config_parent,
            brand="feishu",
            timeout_seconds=5,
            lark_cli_path=os.fspath(fake_lark_cli),
            approved_executable_sha256=fake_digest,
            consent_confirmed=True,
            process_factory=fake_factory,
            browser_opener=lambda url: browser_urls.append(url) is None,
            base_environment=base_environment,
            emit=lambda payload: emitted.append(dict(payload)),
        )
        assert returncode == 0
        assert shared_config.read_text(encoding="utf-8") == shared_sentinel
        assert len(browser_urls) == 1 and browser_urls[0] == verification_url
        terminal = _read_state(state_path)
        assert terminal is not None and terminal["state"] == "succeeded"
        profile = terminal["profile"]
        config_dir = Path(terminal["config_dir"])
        data_dir = Path(terminal["data_dir"])
        assert config_dir.parent == config_parent
        assert config_dir.name == profile
        assert data_dir == config_dir / "data"
        assert captured_commands == [
            _command_for(os.fspath(fake_lark_cli), profile, "feishu")
        ]
        assert captured_environments[0]["LARKSUITE_CLI_CONFIG_DIR"] == os.fspath(
            config_dir
        )
        assert captured_environments[0]["LARKSUITE_CLI_DATA_DIR"] == os.fspath(
            config_dir / "data"
        )
        assert not any(
            key.startswith(("OPENCLAW_", "HERMES_"))
            or (
                key.startswith("LARK")
                and key
                not in {
                    "LARKSUITE_CLI_CONFIG_DIR",
                    "LARKSUITE_CLI_DATA_DIR",
                }
            )
            for key in captured_environments[0]
        )
        assert not any(
            key in {
                "HTTP_PROXY",
                "HTTPS_PROXY",
                "ALL_PROXY",
                "NO_PROXY",
                "SSL_CERT_FILE",
                "SSL_CERT_DIR",
            }
            for key in captured_environments[0]
        )
        flattened_safe_output = "\n".join(
            (
                state_path.read_text(encoding="utf-8"),
                json.dumps(emitted, sort_keys=True),
                json.dumps(captured_commands),
            )
        )
        for forbidden in (
            user_code,
            app_id,
            app_secret,
            device_code,
            verification_url,
            "user_code",
            "device_code",
        ):
            assert forbidden not in flattened_safe_output

        assert (
            status(
                state_path,
                brand="feishu",
                profile=profile,
                config_dir=config_dir,
                data_dir=data_dir,
                approved_executable_sha256=fake_digest,
                emit=lambda _: None,
            )
            == 0
        )
        original_config_dir = config_dir.with_name(config_dir.name + ".original")
        os.replace(config_dir, original_config_dir)
        config_dir.mkdir(mode=0o700)
        try:
            assert (
                status(
                    state_path,
                    brand="feishu",
                    profile=profile,
                    config_dir=config_dir,
                    data_dir=data_dir,
                    approved_executable_sha256=fake_digest,
                    emit=lambda _: None,
                )
                != 0
            )
        finally:
            os.rmdir(config_dir)
            os.replace(original_config_dir, config_dir)
        assert (
            status(
                state_path,
                brand="feishu",
                profile=PROFILE_PREFIX + "0" * 32,
                config_dir=config_dir,
                data_dir=data_dir,
                approved_executable_sha256=fake_digest,
                emit=lambda _: None,
            )
            != 0
        )
        cleanup_events: list[dict[str, Any]] = []
        assert (
            cleanup(
                state_path,
                brand="feishu",
                profile=profile,
                config_dir=config_dir,
                data_dir=data_dir,
                approved_executable_sha256=fake_digest,
                emit=lambda payload: cleanup_events.append(dict(payload)),
            )
            != 0
        )
        assert cleanup_events[-1]["reason"] == (
            "cleanup_refused_successful_configuration"
        )
        assert state_path.exists() and config_dir.exists()

        cancelled_state = root / "cancelled-state.json"
        cancelled_events: list[dict[str, Any]] = []

        def never_started_factory(
            command: list[str],
            **kwargs: Any,
        ) -> _FakeProcess:
            del command, kwargs
            return _FakeProcess(b"", b"", returncode=0)

        cancelled_code = run_config_init(
            state_path=cancelled_state,
            config_parent=config_parent,
            brand="feishu",
            timeout_seconds=5,
            lark_cli_path=os.fspath(fake_lark_cli),
            approved_executable_sha256=fake_digest,
            consent_confirmed=True,
            process_factory=never_started_factory,
            browser_opener=lambda _: True,
            cancel_requested=lambda: True,
            emit=lambda payload: cancelled_events.append(dict(payload)),
        )
        assert cancelled_code != 0
        cancelled_terminal = _read_state(cancelled_state)
        assert cancelled_terminal is not None
        assert cancelled_terminal["state"] == "cancelled"
        cancelled_config = Path(cancelled_terminal["config_dir"])
        cancelled_data = Path(cancelled_terminal["data_dir"])
        assert (
            cleanup(
                cancelled_state,
                brand="feishu",
                profile=cancelled_terminal["profile"],
                config_dir=cancelled_config,
                data_dir=cancelled_data,
                approved_executable_sha256=fake_digest,
                emit=lambda _: None,
            )
            == 0
        )
        assert not cancelled_state.exists() and not cancelled_config.exists()

    assert _validated_verification_url(verification_url, "feishu") == verification_url
    assert (
        _validated_verification_url(
            verification_url.replace("open.feishu.cn", "evil.example"),
            "feishu",
        )
        is None
    )
    assert (
        _validated_verification_url(
            verification_url.replace("/page/cli", "/page/cli/extra"),
            "feishu",
        )
        is None
    )
    assert (
        _validated_verification_url(
            verification_url.replace("&lpv=v1.0.79", ""),
            "feishu",
        )
        is None
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or inspect one isolated Feishu/Lark CLI profile."
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--status", action="store_true")
    mode.add_argument("--cleanup", action="store_true")
    mode.add_argument("--self-test", action="store_true")
    parser.add_argument("--state-file")
    parser.add_argument("--config-parent")
    parser.add_argument("--config-dir")
    parser.add_argument("--data-dir")
    parser.add_argument("--brand", choices=("feishu", "lark"))
    parser.add_argument("--profile")
    parser.add_argument("--lark-cli")
    parser.add_argument("--approved-executable-sha256")
    parser.add_argument("--consent-confirmed", action="store_true")
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
    )
    args = parser.parse_args(argv)
    if args.self_test:
        return args
    if not args.state_file:
        parser.error("--state-file is required")
    if not args.brand or not args.approved_executable_sha256:
        parser.error("--brand and --approved-executable-sha256 are required")
    if args.status or args.cleanup:
        if not args.profile or not args.config_dir or not args.data_dir:
            parser.error("--profile, --config-dir, and --data-dir are required")
    else:
        if not args.config_parent or not args.lark_cli:
            parser.error("--config-parent and --lark-cli are required")
        if not args.consent_confirmed:
            parser.error("fresh setup requires --consent-confirmed")
    if not 1 <= args.timeout_seconds <= MAX_TIMEOUT_SECONDS:
        parser.error(
            f"--timeout-seconds must be between 1 and {MAX_TIMEOUT_SECONDS:g}"
        )
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.self_test:
        run_self_test()
        print(json.dumps({"self_test": "passed"}, sort_keys=True))
        return 0

    state_path = _validated_state_path(args.state_file)
    if state_path is None:
        _emit_json(
            {
                "state": "failed",
                "reason": "state_path_invalid",
                "updated_at": _utc_timestamp(),
            }
        )
        return 3
    expected_sha256 = args.approved_executable_sha256.casefold()
    if args.status or args.cleanup:
        config_dir = _validated_config_dir(args.config_dir)
        data_dir = _validated_existing_directory(args.data_dir)
        if (
            config_dir is None
            or data_dir is None
            or not _same_path(data_dir, config_dir / "data")
            or not PROFILE_PATTERN.fullmatch(args.profile)
            or not SHA256_PATTERN.fullmatch(expected_sha256)
        ):
            _emit_json(
                {
                    "state": "failed",
                    "reason": "state_file_invalid",
                    "updated_at": _utc_timestamp(),
                }
            )
            return 3
        operation = cleanup if args.cleanup else status
        return operation(
            state_path,
            brand=args.brand,
            profile=args.profile,
            config_dir=config_dir,
            data_dir=data_dir,
            approved_executable_sha256=expected_sha256,
        )

    config_parent = _validated_existing_directory(args.config_parent)
    if config_parent is None:
        _emit_json(
            {
                "state": "failed",
                "reason": "config_parent_invalid",
                "updated_at": _utc_timestamp(),
            }
        )
        return 3
    try:
        return run_config_init(
            state_path=state_path,
            config_parent=config_parent,
            brand=args.brand,
            timeout_seconds=args.timeout_seconds,
            lark_cli_path=args.lark_cli,
            approved_executable_sha256=expected_sha256,
            consent_confirmed=args.consent_confirmed,
        )
    except Exception:
        _emit_json(
            {
                "state": "failed",
                "reason": "unexpected_configuration_failure",
                "updated_at": _utc_timestamp(),
            }
        )
        return 5


if __name__ == "__main__":
    raise SystemExit(main())
