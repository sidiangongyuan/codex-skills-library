#!/usr/bin/env python3
"""Prepare, audit, and publish clean GitHub release repositories."""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, Sequence


DEFAULT_DENY_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".ipynb_checkpoints",
    "dataset",
    "datasets",
    "data",
    "ckpt",
    "ckpts",
    "checkpoint",
    "checkpoints",
    "log",
    "logs",
    "wandb",
    "runs",
    "output",
    "outputs",
    "result",
    "results",
    "paper",
    "papers",
    "tmp",
    "temp",
}

DEFAULT_DENY_FILE_PATTERNS = [
    "*.pdf",
    "*.pth",
    "*.pt",
    "*.ckpt",
    "*.npy",
    "*.npz",
    "*.pkl",
    "*.pickle",
    "*.joblib",
    "*.h5",
    "*.hdf5",
    "*.onnx",
    "*.engine",
    "*.zip",
    "*.tar",
    "*.tar.gz",
    "*.tgz",
    "*.7z",
    "*.rar",
    "*.mp4",
    "*.avi",
    "*.mov",
    "*.mkv",
]

TEXT_EXTENSIONS = {
    ".bib",
    ".cfg",
    ".cff",
    ".conf",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".rst",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}

RISK_PATTERNS = [
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("openai-token", re.compile(r"\bsk-[A-Za-z0-9][A-Za-z0-9_-]{20,}\b")),
    ("local-path", re.compile(r"(?<![\w.-])/(?:home|mnt|Users|Volumes)/[^\s)`'\"]+")),
    ("camera-ready", re.compile(r"camera[- ]?ready|Camera Ready", re.IGNORECASE)),
    ("private-review", re.compile(r"\b(rebuttal|meta-review|OpenReview-private)\b", re.IGNORECASE)),
    ("internal-note", re.compile(r"给你|你需要|你帮|我会|我自己|请你|注意")),
]

STALE_UPSTREAM_README_PATTERNS = [
    re.compile(r"official implementation of (?:OpenCOOD|HEAL)", re.IGNORECASE),
    re.compile(r"welcome to (?:OpenCOOD|HEAL)", re.IGNORECASE),
    re.compile(r"this repository contains .* upstream", re.IGNORECASE),
]


@dataclass
class CopyStats:
    copied_files: int = 0
    skipped_files: int = 0
    skipped_dirs: int = 0
    skipped: list[str] | None = None


@dataclass
class Risk:
    severity: str
    kind: str
    path: str
    detail: str


def run(
    args: Sequence[str],
    cwd: Path | None = None,
    check: bool = True,
    dry_run: bool = False,
) -> subprocess.CompletedProcess[str]:
    if dry_run:
        print("$ " + " ".join(args))
        return subprocess.CompletedProcess(args, 0, "", "")
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=check)


def print_result(title: str, payload: object, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(title)
    if isinstance(payload, dict):
        for key, value in payload.items():
            print(f"  {key}: {value}")
    else:
        print(payload)


def sanitize_repo_name(name: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9._-]+", "-", name.strip()).strip(".-_")
    return sanitized or "project-release"


def default_release_dir(source: Path) -> Path:
    return source.parent / f"{sanitize_repo_name(source.name)}-github"


def get_active_github_user() -> str | None:
    try:
        result = run(["gh", "api", "user", "--jq", ".login"], check=True)
        return result.stdout.strip() or None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def repo_parts(repo: str | None, owner: str | None, name: str | None, release_dir: Path) -> tuple[str, str]:
    if repo:
        if "/" not in repo:
            raise SystemExit("--repo must be in OWNER/NAME form")
        repo_owner, repo_name = repo.split("/", 1)
        return repo_owner, sanitize_repo_name(repo_name)
    repo_owner = owner or get_active_github_user()
    if not repo_owner:
        raise SystemExit("Cannot infer GitHub owner. Run `gh auth login` or pass --owner.")
    return repo_owner, sanitize_repo_name(name or release_dir.name)


def auth_check(args: argparse.Namespace) -> int:
    gh = shutil.which("gh")
    git = shutil.which("git")
    payload: dict[str, object] = {
        "gh": gh or "missing",
        "git": git or "missing",
        "active_user": None,
        "repo_scope_seen": False,
        "git_user_name": None,
        "git_user_email": None,
    }
    ok = bool(gh and git)

    if gh:
        status = run(["gh", "auth", "status"], check=False)
        combined = status.stdout + status.stderr
        payload["gh_auth_status"] = "ok" if status.returncode == 0 else "failed"
        payload["repo_scope_seen"] = "'repo'" in combined or " repo" in combined
        payload["active_user"] = get_active_github_user()
        ok = ok and status.returncode == 0 and bool(payload["active_user"])
    else:
        payload["gh_auth_status"] = "missing-gh"

    if git:
        name = run(["git", "config", "--get", "user.name"], check=False)
        email = run(["git", "config", "--get", "user.email"], check=False)
        payload["git_user_name"] = name.stdout.strip() if name.returncode == 0 else ""
        payload["git_user_email"] = email.stdout.strip() if email.returncode == 0 else ""
        ok = ok and bool(payload["git_user_name"]) and bool(payload["git_user_email"])

    payload["ready"] = ok
    print_result("Authentication check", payload, args.json)
    return 0 if ok else 2


def normalize_patterns(patterns: Iterable[str]) -> list[str]:
    return [p.replace("\\", "/") for p in patterns if p]


def rel_match(rel_path: str, patterns: Sequence[str]) -> bool:
    rel_path = rel_path.replace("\\", "/")
    name = Path(rel_path).name
    return any(fnmatch.fnmatch(rel_path, p) or fnmatch.fnmatch(name, p) for p in patterns)


def should_skip_file(
    rel_path: str,
    deny_patterns: Sequence[str],
    allow_patterns: Sequence[str],
) -> str | None:
    if rel_match(rel_path, allow_patterns):
        return None
    if rel_match(rel_path, deny_patterns):
        return "deny-pattern"
    return None


def iter_source_files(
    source: Path,
    dest: Path | None,
    deny_dirs: set[str],
    deny_patterns: Sequence[str],
    allow_patterns: Sequence[str],
) -> tuple[list[Path], list[tuple[Path, str]], int]:
    files: list[Path] = []
    skipped: list[tuple[Path, str]] = []
    skipped_dirs = 0
    dest_resolved = dest.resolve() if dest else None

    for root, dirs, filenames in os.walk(source):
        root_path = Path(root)
        kept_dirs = []
        for dirname in dirs:
            child = root_path / dirname
            rel = child.relative_to(source).as_posix()
            if dest_resolved and child.resolve() == dest_resolved:
                skipped.append((child, "destination-inside-source"))
                skipped_dirs += 1
                continue
            if dirname in deny_dirs and not rel_match(rel, allow_patterns):
                skipped.append((child, "deny-dir"))
                skipped_dirs += 1
                continue
            kept_dirs.append(dirname)
        dirs[:] = kept_dirs

        for filename in filenames:
            path = root_path / filename
            rel = path.relative_to(source).as_posix()
            reason = should_skip_file(rel, deny_patterns, allow_patterns)
            if reason:
                skipped.append((path, reason))
            else:
                files.append(path)
    return files, skipped, skipped_dirs


def prepare(args: argparse.Namespace) -> int:
    source = Path(args.source).expanduser().resolve()
    dest = Path(args.dest).expanduser().resolve() if args.dest else default_release_dir(source)
    if not source.exists() or not source.is_dir():
        raise SystemExit(f"Source directory does not exist: {source}")
    if source == dest:
        raise SystemExit("Destination must differ from source.")

    deny_dirs = set(DEFAULT_DENY_DIRS) | set(args.ignore_dir)
    deny_patterns = normalize_patterns([*DEFAULT_DENY_FILE_PATTERNS, *args.ignore_pattern])
    allow_patterns = normalize_patterns(args.allow_pattern)
    files, skipped, skipped_dirs = iter_source_files(
        source, dest, deny_dirs, deny_patterns, allow_patterns
    )
    stats = CopyStats(
        copied_files=len(files),
        skipped_files=len([item for item in skipped if item[0].is_file()]),
        skipped_dirs=skipped_dirs,
        skipped=[f"{path.relative_to(source).as_posix()} ({reason})" for path, reason in skipped[:50]],
    )

    if args.dry_run:
        print_result(
            "Prepare dry run",
            {
                "source": str(source),
                "dest": str(dest),
                **asdict(stats),
                "note": "No files copied.",
            },
            args.json,
        )
        return 0

    if dest.exists():
        if not args.force:
            raise SystemExit(f"Destination exists: {dest}. Pass --force to replace it.")
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)

    for path in files:
        rel = path.relative_to(source)
        out = dest / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, out)

    print_result(
        "Prepared release copy",
        {"source": str(source), "dest": str(dest), **asdict(stats)},
        args.json,
    )
    return 0


def is_text_file(path: Path) -> bool:
    if path.suffix in TEXT_EXTENSIONS:
        return True
    if path.name.lower() in {"readme", "license", "notice", "citation"}:
        return True
    return False


def scan_text(path: Path, root: Path, max_bytes: int) -> list[Risk]:
    risks: list[Risk] = []
    if path.stat().st_size > max_bytes or not is_text_file(path):
        return risks
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return risks

    rel = path.relative_to(root).as_posix()
    for kind, pattern in RISK_PATTERNS:
        for match in pattern.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            snippet = match.group(0)
            if len(snippet) > 100:
                snippet = snippet[:97] + "..."
            risks.append(Risk("high", kind, rel, f"line {line}: {snippet}"))

    if path.name.lower().startswith("readme"):
        for pattern in STALE_UPSTREAM_README_PATTERNS:
            if pattern.search(text):
                risks.append(Risk("medium", "stale-upstream-readme", rel, pattern.pattern))
    return risks


def audit_path(
    root: Path,
    max_size_mb: int = 50,
    max_text_mb: int = 2,
    allow_patterns: Sequence[str] | None = None,
) -> list[Risk]:
    allow = normalize_patterns(allow_patterns or [])
    deny_patterns = normalize_patterns(DEFAULT_DENY_FILE_PATTERNS)
    risks: list[Risk] = []
    max_size = max_size_mb * 1024 * 1024
    max_text = max_text_mb * 1024 * 1024

    for path in root.rglob("*"):
        if ".git" in path.parts:
            continue
        rel = path.relative_to(root).as_posix()
        if path.is_dir():
            if path.name in DEFAULT_DENY_DIRS and not rel_match(rel, allow):
                risks.append(Risk("high", "blocked-dir", rel, f"directory name `{path.name}`"))
            continue
        if rel_match(rel, allow):
            continue
        if rel_match(rel, deny_patterns):
            risks.append(Risk("high", "blocked-file-pattern", rel, "default release denylist"))
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size > max_size:
            risks.append(Risk("high", "large-file", rel, f"{size / (1024 * 1024):.1f} MB"))
        risks.extend(scan_text(path, root, max_text))
    return risks


def audit(args: argparse.Namespace) -> int:
    root = Path(args.path).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Audit path does not exist: {root}")
    risks = audit_path(root, args.max_size_mb, args.max_text_mb, args.allow_pattern)
    payload = {"path": str(root), "risk_count": len(risks), "risks": [asdict(r) for r in risks]}
    print_result("Audit result", payload, args.json)
    return 2 if risks else 0


def ensure_git_repo(path: Path, branch: str, dry_run: bool) -> None:
    if not (path / ".git").exists():
        run(["git", "init", "-b", branch], cwd=path, dry_run=dry_run)
    else:
        current = run(["git", "branch", "--show-current"], cwd=path, check=False, dry_run=dry_run)
        if not dry_run and current.stdout.strip() != branch:
            run(["git", "checkout", "-B", branch], cwd=path)


def commit_release(path: Path, message: str, dry_run: bool) -> str:
    run(["git", "add", "-A"], cwd=path, dry_run=dry_run)
    status = run(["git", "status", "--porcelain"], cwd=path, dry_run=dry_run)
    if dry_run:
        return "DRY-RUN"
    if status.stdout.strip():
        run(["git", "commit", "-m", message], cwd=path)
    rev = run(["git", "rev-parse", "HEAD"], cwd=path)
    return rev.stdout.strip()


def repo_exists(owner: str, name: str) -> tuple[bool, dict[str, object] | None]:
    result = run(
        ["gh", "repo", "view", f"{owner}/{name}", "--json", "nameWithOwner,isPrivate,url"],
        check=False,
    )
    if result.returncode != 0:
        return False, None
    return True, json.loads(result.stdout)


def set_remote(path: Path, remote: str, url: str, dry_run: bool) -> None:
    existing = run(["git", "remote", "get-url", remote], cwd=path, check=False, dry_run=dry_run)
    if dry_run:
        return
    if existing.returncode == 0:
        if existing.stdout.strip() != url:
            run(["git", "remote", "set-url", remote, url], cwd=path)
    else:
        run(["git", "remote", "add", remote, url], cwd=path)


def remote_branch_exists(path: Path, remote: str, branch: str) -> bool:
    result = run(["git", "ls-remote", "--heads", remote, branch], cwd=path, check=False)
    return bool(result.stdout.strip())


def safe_push(path: Path, remote: str, branch: str, dry_run: bool) -> None:
    if dry_run:
        run(["git", "push", "-u", remote, branch], cwd=path, dry_run=True)
        return
    run(["git", "fetch", remote], cwd=path, check=False)
    if remote_branch_exists(path, remote, branch):
        base = run(["git", "merge-base", "--is-ancestor", f"{remote}/{branch}", "HEAD"], cwd=path, check=False)
        if base.returncode != 0:
            raise SystemExit(
                f"Refusing to push: {remote}/{branch} is not an ancestor of local HEAD. "
                "This skill does not rewrite remote history by default."
            )
    run(["git", "push", "-u", remote, branch], cwd=path)


def publish(args: argparse.Namespace) -> int:
    release_dir = Path(args.release_dir).expanduser().resolve()
    if not release_dir.exists() or not release_dir.is_dir():
        raise SystemExit(f"Release directory does not exist: {release_dir}")

    owner, name = repo_parts(args.repo, args.owner, args.name, release_dir)
    visibility = "public" if args.public else "private"
    remote_url = f"https://github.com/{owner}/{name}.git"

    risks = [] if args.skip_audit else audit_path(release_dir, args.max_size_mb, args.max_text_mb, args.allow_pattern)
    if risks and not args.dry_run:
        payload = {"risk_count": len(risks), "risks": [asdict(r) for r in risks[:20]]}
        print_result("Publish blocked by audit", payload, args.json)
        return 2

    exists, info = (False, None) if args.dry_run else repo_exists(owner, name)
    ensure_git_repo(release_dir, args.branch, args.dry_run)
    sha = commit_release(release_dir, args.message, args.dry_run)

    if args.dry_run:
        print_result(
            "Publish dry run",
            {
                "release_dir": str(release_dir),
                "repo": f"{owner}/{name}",
                "visibility": visibility,
                "branch": args.branch,
                "commit": sha,
                "audit_risks": len(risks),
                "would_create_repo_if_missing": True,
                "would_push_without_force": True,
            },
            args.json,
        )
        return 0

    if not exists:
        create_cmd = ["gh", "repo", "create", f"{owner}/{name}", f"--{visibility}"]
        if args.description:
            create_cmd.extend(["--description", args.description])
        run(create_cmd)
    elif args.public and info and info.get("isPrivate"):
        raise SystemExit("Refusing to change an existing private repo to public by default.")

    set_remote(release_dir, args.remote, remote_url, args.dry_run)
    safe_push(release_dir, args.remote, args.branch, args.dry_run)
    final_info = repo_exists(owner, name)[1] or {}
    print_result(
        "Published release repo",
        {
            "repo": f"{owner}/{name}",
            "url": final_info.get("url", f"https://github.com/{owner}/{name}"),
            "visibility": "private" if final_info.get("isPrivate", True) else "public",
            "branch": args.branch,
            "commit": sha,
            "audit_risks": len(risks),
        },
        args.json,
    )
    return 0


def dry_run(args: argparse.Namespace) -> int:
    source = Path(args.source).expanduser().resolve()
    dest = Path(args.dest).expanduser().resolve() if args.dest else default_release_dir(source)
    owner, name = repo_parts(args.repo, args.owner, args.name, dest)
    files, skipped, skipped_dirs = iter_source_files(
        source,
        dest,
        set(DEFAULT_DENY_DIRS),
        normalize_patterns(DEFAULT_DENY_FILE_PATTERNS),
        normalize_patterns(args.allow_pattern),
    )
    risks = audit_path(source, args.max_size_mb, args.max_text_mb, args.allow_pattern)
    print_result(
        "End-to-end dry run",
        {
            "source": str(source),
            "release_dir": str(dest),
            "repo": f"{owner}/{name}",
            "visibility": "private",
            "would_copy_files": len(files),
            "would_skip_items": len(skipped),
            "would_skip_dirs": skipped_dirs,
            "source_audit_risks": len(risks),
            "note": "No files copied, no git repo created, no GitHub repo created.",
        },
        args.json,
    )
    return 0


def add_common_audit_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--max-size-mb", type=int, default=50)
    parser.add_argument("--max-text-mb", type=int, default=2)
    parser.add_argument("--allow-pattern", action="append", default=[])
    parser.add_argument("--json", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_auth = sub.add_parser("auth-check", help="Check gh/git credentials.")
    p_auth.add_argument("--json", action="store_true")
    p_auth.set_defaults(func=auth_check)

    p_prepare = sub.add_parser("prepare", help="Create a clean release copy.")
    p_prepare.add_argument("--source", default=".")
    p_prepare.add_argument("--dest")
    p_prepare.add_argument("--force", action="store_true")
    p_prepare.add_argument("--dry-run", action="store_true")
    p_prepare.add_argument("--ignore-dir", action="append", default=[])
    p_prepare.add_argument("--ignore-pattern", action="append", default=[])
    p_prepare.add_argument("--allow-pattern", action="append", default=[])
    p_prepare.add_argument("--json", action="store_true")
    p_prepare.set_defaults(func=prepare)

    p_audit = sub.add_parser("audit", help="Audit a release directory for risky files/content.")
    p_audit.add_argument("--path", default=".")
    add_common_audit_args(p_audit)
    p_audit.set_defaults(func=audit)

    p_publish = sub.add_parser("publish", help="Create or safely update a GitHub repo.")
    p_publish.add_argument("--release-dir", default=".")
    p_publish.add_argument("--repo")
    p_publish.add_argument("--owner")
    p_publish.add_argument("--name")
    p_publish.add_argument("--public", action="store_true")
    p_publish.add_argument("--remote", default="origin")
    p_publish.add_argument("--branch", default="main")
    p_publish.add_argument("--message", default="Initial clean release")
    p_publish.add_argument("--description")
    p_publish.add_argument("--skip-audit", action="store_true")
    p_publish.add_argument("--dry-run", action="store_true")
    add_common_audit_args(p_publish)
    p_publish.set_defaults(func=publish)

    p_dry = sub.add_parser("dry-run", help="Show prepare/audit/publish plan without mutation.")
    p_dry.add_argument("--source", default=".")
    p_dry.add_argument("--dest")
    p_dry.add_argument("--repo")
    p_dry.add_argument("--owner")
    p_dry.add_argument("--name")
    add_common_audit_args(p_dry)
    p_dry.set_defaults(func=dry_run)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except FileNotFoundError as exc:
        print(f"Missing command: {exc}", file=sys.stderr)
        return 127
    except subprocess.CalledProcessError as exc:
        if exc.stdout:
            print(exc.stdout, file=sys.stdout)
        if exc.stderr:
            print(exc.stderr, file=sys.stderr)
        return exc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
