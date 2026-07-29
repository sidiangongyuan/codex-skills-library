#!/usr/bin/env python3
"""Install the official Lark/Feishu CLI release without running package scripts.

This helper performs a network download and a filesystem write. The calling
agent must obtain explicit user consent before invoking it and pass
``--consent-confirmed``. It never requests credentials, edits PATH, or executes
the downloaded binary.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import platform
import re
import shutil
import stat
import sys
import tarfile
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO, Iterator, Mapping, Sequence


SCHEMA_VERSION = 1
REPOSITORY = "larksuite/cli"
API_ROOT = "https://api.github.com/repos/larksuite/cli/releases"
USER_AGENT = "feishu-paper-reading-lark-cli-installer/1"
SEMVER = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$"
)
CHECKSUM_LINE = re.compile(
    r"^([0-9A-Fa-f]{64})[ \t]+[*]?([^\x00-\x1f\x7f]+)$"
)
ALLOWED_ARCHIVE_MEMBERS = frozenset(
    {"README.md", "LICENSE", "CHANGELOG.md"}
)
MAX_RELEASE_JSON_BYTES = 2 * 1024 * 1024
MAX_CHECKSUM_BYTES = 2 * 1024 * 1024
MAX_ARCHIVE_BYTES = 160 * 1024 * 1024
MAX_BINARY_BYTES = 128 * 1024 * 1024
MAX_AUXILIARY_MEMBER_BYTES = 8 * 1024 * 1024
MAX_ARCHIVE_MEMBERS = 8
DEFAULT_TIMEOUT_SECONDS = 30.0
MAX_TIMEOUT_SECONDS = 120.0


class InstallerError(Exception):
    """An expected, user-facing installer failure."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class JsonArgumentParser(argparse.ArgumentParser):
    """Route argument errors through the sanitized JSON error contract."""

    def error(self, message: str) -> None:
        del message
        raise InstallerError(
            "invalid_arguments",
            "Command-line arguments were invalid. Use --help for the accepted options.",
        )


def _json_print(payload: Mapping[str, Any], *, stream: Any = sys.stdout) -> None:
    print(
        json.dumps(payload, ensure_ascii=True, sort_keys=True),
        file=stream,
        flush=True,
    )


def _validate_https_url(url: str) -> urllib.parse.ParseResult:
    try:
        parsed = urllib.parse.urlparse(url)
        port = parsed.port
    except ValueError as exc:
        raise InstallerError("unsafe_url", "A malformed download URL was rejected.") from exc

    host = (parsed.hostname or "").lower().rstrip(".")
    allowed = (
        host == "github.com"
        or host.endswith(".github.com")
        or host == "githubusercontent.com"
        or host.endswith(".githubusercontent.com")
    )
    if (
        parsed.scheme.lower() != "https"
        or not allowed
        or parsed.username is not None
        or parsed.password is not None
        or port not in (None, 443)
        or parsed.fragment
    ):
        raise InstallerError(
            "unsafe_url",
            "Only HTTPS GitHub and GitHubusercontent download URLs are allowed.",
        )
    return parsed


def _validate_release_asset_url(url: str, tag: str, asset_name: str) -> None:
    parsed = _validate_https_url(url)
    expected_path = f"/{REPOSITORY}/releases/download/{tag}/{asset_name}"
    if (
        (parsed.hostname or "").lower().rstrip(".") != "github.com"
        or parsed.path != expected_path
        or parsed.params
        or parsed.query
    ):
        raise InstallerError(
            "unsafe_asset_url",
            f"The release metadata contained an unexpected URL for {asset_name}.",
        )


class _SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: BinaryIO,
        code: int,
        msg: str,
        headers: Mapping[str, str],
        newurl: str,
    ) -> urllib.request.Request | None:
        _validate_https_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _opener() -> urllib.request.OpenerDirector:
    return urllib.request.build_opener(_SafeRedirectHandler())


def _request(url: str) -> urllib.request.Request:
    _validate_https_url(url)
    return urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": USER_AGENT,
        },
        method="GET",
    )


def _read_bounded(response: BinaryIO, limit: int) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = response.read(min(64 * 1024, limit + 1 - total))
        if not chunk:
            break
        total += len(chunk)
        if total > limit:
            raise InstallerError("response_too_large", "A GitHub response exceeded its size limit.")
        chunks.append(chunk)
    return b"".join(chunks)


def _open_url(url: str, timeout: float) -> BinaryIO:
    try:
        response = _opener().open(_request(url), timeout=timeout)
        _validate_https_url(response.geturl())
        return response
    except InstallerError:
        raise
    except urllib.error.HTTPError as exc:
        if exc.code == 403:
            message = "GitHub refused the request, possibly because its anonymous API limit was reached."
        elif exc.code == 404:
            message = "The requested official GitHub release was not found."
        else:
            message = f"GitHub returned HTTP {exc.code}."
        raise InstallerError("github_http_error", message) from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise InstallerError(
            "network_error",
            "The official GitHub release could not be reached over HTTPS.",
        ) from exc


def _fetch_release(version: str | None, timeout: float) -> Mapping[str, Any]:
    url = (
        f"{API_ROOT}/latest"
        if version is None
        else f"{API_ROOT}/tags/v{version}"
    )
    with contextlib.closing(_open_url(url, timeout)) as response:
        raw = _read_bounded(response, MAX_RELEASE_JSON_BYTES)
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InstallerError(
            "invalid_release_metadata",
            "GitHub returned invalid release metadata.",
        ) from exc
    if not isinstance(value, Mapping):
        raise InstallerError(
            "invalid_release_metadata",
            "GitHub release metadata was not an object.",
        )
    return value


def _normalize_release(
    release: Mapping[str, Any],
    requested_version: str | None,
) -> tuple[str, str, list[Mapping[str, Any]]]:
    tag = release.get("tag_name")
    if not isinstance(tag, str) or not tag.startswith("v"):
        raise InstallerError(
            "invalid_release_metadata",
            "The official release tag was missing or malformed.",
        )
    version = tag[1:]
    if not SEMVER.fullmatch(version):
        raise InstallerError(
            "invalid_release_tag",
            "The official release tag is not an exact stable semantic version.",
        )
    if requested_version is not None and version != requested_version:
        raise InstallerError(
            "release_version_mismatch",
            "The returned release did not match the requested exact version.",
        )
    if release.get("draft") is not False or release.get("prerelease") is not False:
        raise InstallerError(
            "non_stable_release",
            "Draft and prerelease builds are not eligible for installation.",
        )
    assets = release.get("assets")
    if not isinstance(assets, list) or not all(isinstance(item, Mapping) for item in assets):
        raise InstallerError(
            "invalid_release_metadata",
            "The official release asset list was missing or malformed.",
        )
    return version, tag, assets


def _platform_target(
    system_name: str | None = None,
    machine_name: str | None = None,
) -> tuple[str, str, str]:
    system_value = (system_name or platform.system()).lower()
    machine_value = (machine_name or platform.machine()).lower()
    systems = {"windows": "windows", "darwin": "darwin", "linux": "linux"}
    architectures = {
        "amd64": "amd64",
        "x86_64": "amd64",
        "x64": "amd64",
        "arm64": "arm64",
        "aarch64": "arm64",
    }
    operating_system = systems.get(system_value)
    architecture = architectures.get(machine_value)
    if operating_system is None or architecture is None:
        raise InstallerError(
            "unsupported_platform",
            "Only Windows, macOS, and Linux on amd64 or arm64 are supported.",
        )
    extension = ".zip" if operating_system == "windows" else ".tar.gz"
    return operating_system, architecture, extension


def _asset_name(version: str, operating_system: str, architecture: str, extension: str) -> str:
    return f"lark-cli-{version}-{operating_system}-{architecture}{extension}"


def _select_asset(
    assets: Sequence[Mapping[str, Any]],
    asset_name: str,
    tag: str,
    *,
    size_limit: int,
) -> Mapping[str, Any]:
    matches = [item for item in assets if item.get("name") == asset_name]
    if len(matches) != 1:
        raise InstallerError(
            "asset_selection_failed",
            f"Expected exactly one official release asset named {asset_name}.",
        )
    asset = matches[0]
    url = asset.get("browser_download_url")
    size = asset.get("size")
    state = asset.get("state")
    if not isinstance(url, str):
        raise InstallerError("invalid_release_metadata", f"{asset_name} has no download URL.")
    _validate_release_asset_url(url, tag, asset_name)
    if not isinstance(size, int) or isinstance(size, bool) or size <= 0 or size > size_limit:
        raise InstallerError(
            "invalid_asset_size",
            f"The declared size of {asset_name} is outside the allowed range.",
        )
    if state not in (None, "uploaded"):
        raise InstallerError("asset_not_ready", f"The official asset {asset_name} is not uploaded.")
    return asset


def _download_to_file(
    url: str,
    destination: Path,
    timeout: float,
    size_limit: int,
    declared_size: int,
) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(destination, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as output:
            descriptor = -1
            total = 0
            with contextlib.closing(_open_url(url, timeout)) as response:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > size_limit:
                        raise InstallerError(
                            "download_too_large",
                            "A downloaded release asset exceeded its size limit.",
                        )
                    output.write(chunk)
            output.flush()
            os.fsync(output.fileno())
        if total != declared_size:
            raise InstallerError(
                "asset_size_mismatch",
                "A downloaded release asset did not match its declared size.",
            )
    except BaseException:
        if descriptor >= 0:
            os.close(descriptor)
        destination.unlink(missing_ok=True)
        raise


def _parse_checksum_file(raw: bytes, asset_name: str) -> str:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InstallerError(
            "invalid_checksums",
            "The official checksum file was not valid UTF-8.",
        ) from exc
    matches: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = CHECKSUM_LINE.fullmatch(line)
        if match is None:
            raise InstallerError(
                "invalid_checksums",
                "The official checksum file contained a malformed line.",
            )
        digest, filename = match.groups()
        if filename == asset_name:
            matches.append(digest.lower())
    if len(matches) != 1:
        raise InstallerError(
            "checksum_selection_failed",
            f"Expected exactly one SHA-256 checksum for {asset_name}.",
        )
    return matches[0]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _verify_sha256(path: Path, expected: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise InstallerError(
            "invalid_checksums",
            "The selected official SHA-256 checksum was malformed.",
        )
    actual = _sha256(path)
    if actual != expected:
        raise InstallerError(
            "checksum_mismatch",
            "The downloaded archive did not match the official SHA-256 checksum.",
        )
    return actual


def _safe_member_name(name: str, allowed_binary: str) -> None:
    path = PurePosixPath(name)
    allowed = ALLOWED_ARCHIVE_MEMBERS | {allowed_binary}
    if (
        not name
        or "\\" in name
        or path.is_absolute()
        or len(path.parts) != 1
        or path.name not in allowed
        or path.name != name
        or any(part in ("", ".", "..") for part in path.parts)
    ):
        raise InstallerError(
            "unsafe_archive",
            "The release archive contained an unsafe or unexpected member.",
        )


def _write_binary(source: BinaryIO, output_path: Path, expected_size: int) -> None:
    if expected_size <= 0 or expected_size > MAX_BINARY_BYTES:
        raise InstallerError(
            "invalid_binary_size",
            "The archived executable size is outside the allowed range.",
        )
    descriptor = os.open(output_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as output:
            descriptor = -1
            remaining = expected_size
            while remaining:
                chunk = source.read(min(1024 * 1024, remaining))
                if not chunk:
                    raise InstallerError(
                        "truncated_binary",
                        "The archived executable ended before its declared size.",
                    )
                output.write(chunk)
                remaining -= len(chunk)
            if source.read(1):
                raise InstallerError(
                    "binary_size_mismatch",
                    "The archived executable exceeded its declared size.",
                )
            output.flush()
            os.fsync(output.fileno())
    except BaseException:
        if descriptor >= 0:
            os.close(descriptor)
        output_path.unlink(missing_ok=True)
        raise


def _validate_member_set(names: Sequence[str], allowed_binary: str) -> None:
    if len(names) > MAX_ARCHIVE_MEMBERS:
        raise InstallerError("unsafe_archive", "The release archive contained too many members.")
    for name in names:
        _safe_member_name(name, allowed_binary)
    if len(set(names)) != len(names) or names.count(allowed_binary) != 1:
        raise InstallerError(
            "unsafe_archive",
            "The release archive contained duplicate or missing executable members.",
        )


def _extract_zip_binary(archive_path: Path, output_path: Path, binary_name: str) -> None:
    try:
        with zipfile.ZipFile(archive_path, "r") as archive:
            members = archive.infolist()
            _validate_member_set([member.filename for member in members], binary_name)
            total_size = 0
            binary_member: zipfile.ZipInfo | None = None
            for member in members:
                mode = (member.external_attr >> 16) & 0xFFFF
                kind = stat.S_IFMT(mode)
                if (
                    member.is_dir()
                    or member.flag_bits & 0x1
                    or kind not in (0, stat.S_IFREG)
                ):
                    raise InstallerError(
                        "unsafe_archive",
                        "The release ZIP contained a directory, encrypted file, link, or special file.",
                    )
                limit = (
                    MAX_BINARY_BYTES
                    if member.filename == binary_name
                    else MAX_AUXILIARY_MEMBER_BYTES
                )
                if member.file_size < 0 or member.file_size > limit:
                    raise InstallerError(
                        "unsafe_archive",
                        "A release ZIP member exceeded its size limit.",
                    )
                total_size += member.file_size
                if total_size > MAX_BINARY_BYTES + 3 * MAX_AUXILIARY_MEMBER_BYTES:
                    raise InstallerError(
                        "unsafe_archive",
                        "The uncompressed release ZIP exceeded its size limit.",
                    )
                if member.filename == binary_name:
                    binary_member = member
            if binary_member is None:
                raise InstallerError("unsafe_archive", "The release ZIP had no executable.")
            with archive.open(binary_member, "r") as source:
                _write_binary(source, output_path, binary_member.file_size)
    except InstallerError:
        raise
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        output_path.unlink(missing_ok=True)
        raise InstallerError("invalid_archive", "The official ZIP archive could not be read.") from exc


def _extract_tar_binary(archive_path: Path, output_path: Path, binary_name: str) -> None:
    try:
        with tarfile.open(archive_path, mode="r:gz") as archive:
            members = archive.getmembers()
            _validate_member_set([member.name for member in members], binary_name)
            total_size = 0
            binary_member: tarfile.TarInfo | None = None
            for member in members:
                if not member.isfile() or member.issym() or member.islnk():
                    raise InstallerError(
                        "unsafe_archive",
                        "The release tarball contained a directory, link, or special file.",
                    )
                limit = (
                    MAX_BINARY_BYTES
                    if member.name == binary_name
                    else MAX_AUXILIARY_MEMBER_BYTES
                )
                if member.size < 0 or member.size > limit:
                    raise InstallerError(
                        "unsafe_archive",
                        "A release tarball member exceeded its size limit.",
                    )
                total_size += member.size
                if total_size > MAX_BINARY_BYTES + 3 * MAX_AUXILIARY_MEMBER_BYTES:
                    raise InstallerError(
                        "unsafe_archive",
                        "The uncompressed release tarball exceeded its size limit.",
                    )
                if member.name == binary_name:
                    binary_member = member
            if binary_member is None:
                raise InstallerError("unsafe_archive", "The release tarball had no executable.")
            source = archive.extractfile(binary_member)
            if source is None:
                raise InstallerError("invalid_archive", "The archived executable could not be opened.")
            with source:
                _write_binary(source, output_path, binary_member.size)
    except InstallerError:
        raise
    except (OSError, tarfile.TarError) as exc:
        output_path.unlink(missing_ok=True)
        raise InstallerError(
            "invalid_archive",
            "The official tarball could not be read.",
        ) from exc


def _extract_binary(
    archive_path: Path,
    output_path: Path,
    extension: str,
    binary_name: str,
) -> None:
    if extension == ".zip":
        _extract_zip_binary(archive_path, output_path, binary_name)
    elif extension == ".tar.gz":
        _extract_tar_binary(archive_path, output_path, binary_name)
    else:
        raise InstallerError("invalid_archive", "The release archive format is unsupported.")


@contextlib.contextmanager
def _private_temp_directory() -> Iterator[Path]:
    directory = Path(tempfile.mkdtemp(prefix="lark-cli-install-"))
    try:
        if os.name != "nt":
            directory.chmod(0o700)
        yield directory
    finally:
        shutil.rmtree(directory, ignore_errors=True)


def _default_install_directory(operating_system: str) -> Path:
    if operating_system == "windows":
        local_app_data = os.environ.get("LOCALAPPDATA")
        root = Path(local_app_data) if local_app_data else Path.home() / "AppData" / "Local"
        return root / "Programs" / "lark-cli" / "bin"
    return Path.home() / ".local" / "bin"


def _prepare_install_directory(path: Path) -> Path:
    expanded = path.expanduser()
    if os.path.lexists(expanded) and expanded.is_symlink():
        raise InstallerError(
            "unsafe_install_path",
            "The install directory may not be a symbolic link.",
        )
    try:
        expanded.mkdir(mode=0o755, parents=True, exist_ok=True)
        resolved = expanded.resolve(strict=True)
    except OSError as exc:
        raise InstallerError(
            "install_directory_error",
            "The selected install directory could not be created or resolved.",
        ) from exc
    if not resolved.is_dir() or resolved.is_symlink():
        raise InstallerError(
            "unsafe_install_path",
            "The selected install path is not a regular directory.",
        )
    return resolved


def _destination_exists(path: Path) -> bool:
    return os.path.lexists(path)


def _install_atomically(source: Path, install_directory: Path, binary_name: str, replace: bool) -> tuple[Path, bool]:
    directory = _prepare_install_directory(install_directory)
    destination = directory / binary_name
    existed = _destination_exists(destination)
    if existed:
        if destination.is_symlink() or not destination.is_file():
            raise InstallerError(
                "unsafe_existing_destination",
                "The existing destination is not a regular file and will not be replaced.",
            )
        if not replace:
            raise InstallerError(
                "destination_exists",
                "The destination already exists; pass --replace only after confirming replacement.",
            )

    descriptor, stage_name = tempfile.mkstemp(prefix=".lark-cli-", dir=directory)
    stage = Path(stage_name)
    try:
        with os.fdopen(descriptor, "wb") as output, source.open("rb") as input_stream:
            shutil.copyfileobj(input_stream, output, length=1024 * 1024)
            output.flush()
            os.fsync(output.fileno())
        stage.chmod(0o755)
        if replace:
            if _destination_exists(destination) and (
                destination.is_symlink() or not destination.is_file()
            ):
                raise InstallerError(
                    "unsafe_existing_destination",
                    "The destination changed to a non-regular file before replacement.",
                )
            os.replace(stage, destination)
        else:
            try:
                os.link(stage, destination)
            except FileExistsError as exc:
                raise InstallerError(
                    "destination_exists",
                    "The destination appeared during installation and was not overwritten.",
                ) from exc
            except OSError as exc:
                raise InstallerError(
                    "atomic_install_unavailable",
                    "This filesystem could not atomically create the new executable.",
                ) from exc
            stage.unlink()
        if os.name != "nt":
            destination.chmod(0o755)
            try:
                directory_fd = os.open(directory, os.O_RDONLY)
                try:
                    os.fsync(directory_fd)
                finally:
                    os.close(directory_fd)
            except OSError:
                pass
        return destination, existed
    finally:
        stage.unlink(missing_ok=True)


def _install(args: argparse.Namespace) -> Mapping[str, Any]:
    if not args.inspect and not args.consent_confirmed:
        raise InstallerError(
            "consent_required",
            "Run --inspect, obtain explicit user consent for that exact plan, "
            "then rerun the pinned version with --consent-confirmed.",
        )
    if args.version is not None and not SEMVER.fullmatch(args.version):
        raise InstallerError(
            "invalid_version",
            "--version must be an exact stable semantic version such as 1.2.3.",
        )
    if args.expected_sha256 is not None and not re.fullmatch(
        r"[0-9A-Fa-f]{64}",
        args.expected_sha256,
    ):
        raise InstallerError(
            "invalid_expected_sha256",
            "--expected-sha256 must be exactly 64 hexadecimal characters.",
        )
    if not args.inspect and (
        args.version is None
        or args.expected_asset is None
        or args.expected_sha256 is None
    ):
        raise InstallerError(
            "unpinned_install_plan",
            "Installation requires --version, --expected-asset, and "
            "--expected-sha256 from the approved --inspect result.",
        )
    timeout = float(args.timeout)
    if timeout <= 0 or timeout > MAX_TIMEOUT_SECONDS:
        raise InstallerError(
            "invalid_timeout",
            f"--timeout must be greater than zero and at most {MAX_TIMEOUT_SECONDS:g} seconds.",
        )

    operating_system, architecture, extension = _platform_target()
    release = _fetch_release(args.version, timeout)
    version, tag, assets = _normalize_release(release, args.version)
    archive_name = _asset_name(version, operating_system, architecture, extension)
    if args.expected_asset is not None and args.expected_asset != archive_name:
        raise InstallerError(
            "approved_asset_mismatch",
            "The platform release asset no longer matches the approved inspect plan.",
        )
    archive_asset = _select_asset(
        assets,
        archive_name,
        tag,
        size_limit=MAX_ARCHIVE_BYTES,
    )
    checksum_asset = _select_asset(
        assets,
        "checksums.txt",
        tag,
        size_limit=MAX_CHECKSUM_BYTES,
    )
    binary_name = "lark-cli.exe" if operating_system == "windows" else "lark-cli"
    install_directory = (
        Path(args.install_dir)
        if args.install_dir is not None
        else _default_install_directory(operating_system)
    )
    planned_destination = (
        install_directory.expanduser().absolute() / binary_name
    )

    with _private_temp_directory() as temp_directory:
        checksum_path = temp_directory / "checksums.txt"
        archive_path = temp_directory / archive_name
        extracted_path = temp_directory / binary_name
        _download_to_file(
            str(checksum_asset["browser_download_url"]),
            checksum_path,
            timeout,
            MAX_CHECKSUM_BYTES,
            int(checksum_asset["size"]),
        )
        expected_checksum = _parse_checksum_file(
            checksum_path.read_bytes(),
            archive_name,
        )
        if (
            args.expected_sha256 is not None
            and expected_checksum != args.expected_sha256.casefold()
        ):
            raise InstallerError(
                "approved_checksum_mismatch",
                "The official checksum no longer matches the approved inspect plan.",
            )
        if args.inspect:
            return {
                "schema_version": SCHEMA_VERSION,
                "status": "planned",
                "repository": REPOSITORY,
                "version": version,
                "asset": archive_name,
                "sha256": expected_checksum,
                "install_directory": str(install_directory.expanduser().absolute()),
                "destination": str(planned_destination),
                "destination_exists": os.path.lexists(planned_destination),
                "replace_requested": bool(args.replace),
                "path_modified": False,
                "downloaded_binary_executed": False,
                "archive_downloaded": False,
                "files_installed": False,
            }
        _download_to_file(
            str(archive_asset["browser_download_url"]),
            archive_path,
            timeout,
            MAX_ARCHIVE_BYTES,
            int(archive_asset["size"]),
        )
        actual_checksum = _verify_sha256(archive_path, expected_checksum)
        _extract_binary(archive_path, extracted_path, extension, binary_name)
        executable_checksum = _sha256(extracted_path)
        destination, replaced = _install_atomically(
            extracted_path,
            install_directory,
            binary_name,
            args.replace,
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "installed",
        "repository": REPOSITORY,
        "version": version,
        "asset": archive_name,
        "sha256": actual_checksum,
        "executable_sha256": executable_checksum,
        "install_directory": str(destination.parent),
        "destination": str(destination),
        "replaced": replaced,
        "path_modified": False,
        "downloaded_binary_executed": False,
    }


def _expect_error(code: str, function: Any, *args: Any) -> None:
    try:
        function(*args)
    except InstallerError as exc:
        if exc.code != code:
            raise AssertionError(f"Expected {code}, got {exc.code}") from exc
    else:
        raise AssertionError(f"Expected {code}")


def _self_test() -> None:
    assert _platform_target("Windows", "AMD64") == ("windows", "amd64", ".zip")
    assert _platform_target("Darwin", "arm64") == ("darwin", "arm64", ".tar.gz")
    assert _platform_target("Linux", "aarch64") == ("linux", "arm64", ".tar.gz")
    _expect_error("unsupported_platform", _platform_target, "Plan9", "amd64")
    _expect_error("unsupported_platform", _platform_target, "Linux", "riscv64")

    payload = b"test-lark-cli-binary"
    checksum = hashlib.sha256(payload).hexdigest()
    assert _parse_checksum_file(
        f"{checksum}  lark-cli-1.2.3-linux-amd64.tar.gz\n".encode(),
        "lark-cli-1.2.3-linux-amd64.tar.gz",
    ) == checksum
    _expect_error(
        "checksum_selection_failed",
        _parse_checksum_file,
        (
            f"{checksum}  lark-cli-1.2.3-linux-amd64.tar.gz\n"
            f"{checksum}  lark-cli-1.2.3-linux-amd64.tar.gz\n"
        ).encode(),
        "lark-cli-1.2.3-linux-amd64.tar.gz",
    )

    with tempfile.TemporaryDirectory(prefix="lark-cli-installer-self-test-") as raw_temp:
        root = Path(raw_temp)
        valid_zip = root / "valid.zip"
        with zipfile.ZipFile(valid_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("lark-cli.exe", payload)
            archive.writestr("LICENSE", b"license")
        zip_output = root / "zip-output.exe"
        _extract_binary(valid_zip, zip_output, ".zip", "lark-cli.exe")
        assert zip_output.read_bytes() == payload
        archive_checksum = _sha256(valid_zip)
        assert _verify_sha256(valid_zip, archive_checksum) == archive_checksum
        _expect_error("checksum_mismatch", _verify_sha256, valid_zip, "0" * 64)

        unsafe_zip = root / "unsafe.zip"
        with zipfile.ZipFile(unsafe_zip, "w") as archive:
            archive.writestr("../lark-cli.exe", payload)
        _expect_error(
            "unsafe_archive",
            _extract_binary,
            unsafe_zip,
            root / "unsafe-output.exe",
            ".zip",
            "lark-cli.exe",
        )

        unexpected_zip = root / "unexpected.zip"
        with zipfile.ZipFile(unexpected_zip, "w") as archive:
            archive.writestr("lark-cli.exe", payload)
            archive.writestr("install.ps1", b"not allowed")
        _expect_error(
            "unsafe_archive",
            _extract_binary,
            unexpected_zip,
            root / "unexpected-output.exe",
            ".zip",
            "lark-cli.exe",
        )

        symlink_zip = root / "symlink.zip"
        link_info = zipfile.ZipInfo("lark-cli.exe")
        link_info.create_system = 3
        link_info.external_attr = (stat.S_IFLNK | 0o777) << 16
        with zipfile.ZipFile(symlink_zip, "w") as archive:
            archive.writestr(link_info, b"target")
        _expect_error(
            "unsafe_archive",
            _extract_binary,
            symlink_zip,
            root / "symlink-output.exe",
            ".zip",
            "lark-cli.exe",
        )

        valid_tar = root / "valid.tar.gz"
        with tarfile.open(valid_tar, "w:gz") as archive:
            info = tarfile.TarInfo("lark-cli")
            info.size = len(payload)
            archive.addfile(info, _BytesReader(payload))
            license_info = tarfile.TarInfo("LICENSE")
            license_info.size = 7
            archive.addfile(license_info, _BytesReader(b"license"))
        tar_output = root / "tar-output"
        _extract_binary(valid_tar, tar_output, ".tar.gz", "lark-cli")
        assert tar_output.read_bytes() == payload

        unsafe_tar = root / "unsafe.tar.gz"
        with tarfile.open(unsafe_tar, "w:gz") as archive:
            info = tarfile.TarInfo("../../lark-cli")
            info.size = len(payload)
            archive.addfile(info, _BytesReader(payload))
        _expect_error(
            "unsafe_archive",
            _extract_binary,
            unsafe_tar,
            root / "unsafe-tar-output",
            ".tar.gz",
            "lark-cli",
        )

        source = root / "source"
        source.write_bytes(payload)
        install_directory = root / "bin"
        destination, replaced = _install_atomically(
            source,
            install_directory,
            "lark-cli",
            False,
        )
        assert destination.read_bytes() == payload and replaced is False
        _expect_error(
            "destination_exists",
            _install_atomically,
            source,
            install_directory,
            "lark-cli",
            False,
        )
        replacement = root / "replacement"
        replacement.write_bytes(b"replacement")
        destination, replaced = _install_atomically(
            replacement,
            install_directory,
            "lark-cli",
            True,
        )
        assert destination.read_bytes() == b"replacement" and replaced is True


class _BytesReader:
    """Minimal file object used by deterministic tar self-tests."""

    def __init__(self, value: bytes) -> None:
        self._value = value
        self._offset = 0

    def read(self, size: int = -1) -> bytes:
        if size < 0:
            size = len(self._value) - self._offset
        start = self._offset
        end = min(len(self._value), start + size)
        self._offset = end
        return self._value[start:end]


def _build_parser() -> argparse.ArgumentParser:
    parser = JsonArgumentParser(
        description=(
            "Install a checksum-verified official larksuite/cli release binary. "
            "This command does not edit PATH or run the downloaded executable."
        ),
        epilog=(
            "Consent boundary: a person must explicitly approve the GitHub download "
            "and selected install directory before the caller passes "
            "--consent-confirmed. The flag is an attestation, not a prompt."
        ),
    )
    parser.add_argument(
        "--inspect",
        action="store_true",
        help=(
            "Resolve the exact stable release, checksum, and destination "
            "without downloading the binary or installing files."
        ),
    )
    parser.add_argument(
        "--version",
        help="Exact stable version such as 1.2.3. Omit to resolve the latest stable release.",
    )
    parser.add_argument(
        "--expected-asset",
        help="Exact asset name returned by the approved --inspect result.",
    )
    parser.add_argument(
        "--expected-sha256",
        help="Exact archive SHA-256 returned by the approved --inspect result.",
    )
    parser.add_argument(
        "--install-dir",
        help="Explicit destination directory. Defaults to a user-scoped bin directory.",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Atomically replace an existing regular lark-cli executable.",
    )
    parser.add_argument(
        "--consent-confirmed",
        action="store_true",
        help="Attest that explicit external user consent was obtained.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"Per-request timeout in seconds, up to {MAX_TIMEOUT_SECONDS:g}.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run deterministic local tests. No network or install outside a temporary directory.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = _build_parser().parse_args(argv)
        if args.self_test:
            _self_test()
            _json_print({"self_test": "passed"})
            return 0
        _json_print(_install(args))
        return 0
    except InstallerError as exc:
        _json_print(
            {
                "schema_version": SCHEMA_VERSION,
                "status": "error",
                "error": {"code": exc.code, "message": exc.message},
            },
            stream=sys.stderr,
        )
        return 2
    except KeyboardInterrupt:
        _json_print(
            {
                "schema_version": SCHEMA_VERSION,
                "status": "error",
                "error": {"code": "interrupted", "message": "Installation was interrupted."},
            },
            stream=sys.stderr,
        )
        return 130
    except Exception:
        _json_print(
            {
                "schema_version": SCHEMA_VERSION,
                "status": "error",
                "error": {
                    "code": "internal_error",
                    "message": "The installer stopped on an unexpected local error.",
                },
            },
            stream=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
