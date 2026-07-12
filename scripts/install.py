#!/usr/bin/env python3
"""Install selected skills from Codex Skills Library.

This installer intentionally uses only the Python standard library. It copies
skill directories and never executes code from an installed skill.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence, TextIO


ROOT = Path(__file__).resolve().parents[1]
CATALOG_NAME = "skills.json"


class InstallError(ValueError):
    """A user-facing catalog or installation error."""


@dataclass(frozen=True)
class Operation:
    name: str
    source: Path
    destination: Path
    exists: bool


def _lexists(path: Path) -> bool:
    """Return True for normal paths and broken symbolic links."""

    return os.path.lexists(path)


def load_catalog(root: Path = ROOT) -> list[dict[str, object]]:
    catalog_path = root / CATALOG_NAME
    try:
        document = json.loads(catalog_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise InstallError(f"Catalog not found: {catalog_path}") from exc
    except json.JSONDecodeError as exc:
        raise InstallError(
            f"Invalid JSON in {catalog_path}: line {exc.lineno}, column {exc.colno}"
        ) from exc

    if not isinstance(document, dict) or document.get("schema_version") != 2:
        raise InstallError(f"{catalog_path} must use catalog schema_version 2")
    skills = document.get("skills")
    if not isinstance(skills, list):
        raise InstallError(f"{catalog_path} must contain a skills array")

    seen: set[str] = set()
    normalized: list[dict[str, object]] = []
    for index, item in enumerate(skills):
        if not isinstance(item, dict):
            raise InstallError(f"skills[{index}] must be an object")
        name = item.get("name")
        path = item.get("path")
        if not isinstance(name, str) or not name:
            raise InstallError(f"skills[{index}].name must be a non-empty string")
        if name in seen:
            raise InstallError(f"Duplicate skill name in catalog: {name}")
        if not isinstance(path, str) or path != f"skills/{name}":
            raise InstallError(
                f"Catalog path for {name!r} must be exactly 'skills/{name}'"
            )
        seen.add(name)
        normalized.append(item)
    return normalized


def print_catalog(skills: Sequence[dict[str, object]], stream: TextIO) -> None:
    print(f"Available skills ({len(skills)}):", file=stream)
    for item in skills:
        print(
            f"  {item['name']:<36} {item.get('category', '')} "
            f"[{item.get('provenance', '')}]",
            file=stream,
        )


def select_skills(
    skills: Sequence[dict[str, object]], names: Sequence[str] | None, install_all: bool
) -> list[dict[str, object]]:
    by_name = {str(item["name"]): item for item in skills}
    if install_all:
        return list(skills)

    selected: list[dict[str, object]] = []
    missing: list[str] = []
    seen: set[str] = set()
    for name in names or ():
        if name in seen:
            continue
        seen.add(name)
        item = by_name.get(name)
        if item is None:
            missing.append(name)
        else:
            selected.append(item)
    if missing:
        raise InstallError(f"Unknown skill(s): {', '.join(missing)}")
    return selected


def _validate_target_root(target: Path) -> Path:
    target = target.expanduser().resolve(strict=False)
    if _lexists(target) and not target.is_dir():
        raise InstallError(f"Installation target is not a directory: {target}")

    ancestor = target
    while not _lexists(ancestor) and ancestor != ancestor.parent:
        ancestor = ancestor.parent
    if _lexists(ancestor) and not ancestor.is_dir():
        raise InstallError(f"Target parent is not a directory: {ancestor}")
    return target


def plan_operations(
    root: Path,
    selected: Sequence[dict[str, object]],
    target: Path,
) -> tuple[Path, list[Operation]]:
    """Validate every source and destination before any filesystem mutation."""

    root = root.resolve(strict=True)
    skills_root = (root / "skills").resolve(strict=True)
    target = _validate_target_root(target)
    operations: list[Operation] = []

    for item in selected:
        name = str(item["name"])
        relative_source = Path(str(item["path"]))
        if relative_source.is_absolute() or relative_source.parts != ("skills", name):
            raise InstallError(f"Unsafe catalog path for {name}: {relative_source}")
        try:
            source = (root / relative_source).resolve(strict=True)
        except FileNotFoundError as exc:
            raise InstallError(f"Missing skill source: {root / relative_source}") from exc
        try:
            source.relative_to(skills_root)
        except ValueError as exc:
            raise InstallError(f"Skill source escapes the skills directory: {source}") from exc
        if not source.is_dir():
            raise InstallError(f"Skill source is not a directory: {source}")

        destination = target / name
        if destination.parent != target or destination.name != name:
            raise InstallError(f"Unsafe destination for {name}: {destination}")
        operations.append(
            Operation(
                name=name,
                source=source,
                destination=destination,
                exists=_lexists(destination),
            )
        )
    return target, operations


def _safe_remove(destination: Path, target: Path) -> None:
    """Remove one exact target child without following links or junctions."""

    if destination.parent != target or destination.name in {"", ".", ".."}:
        raise InstallError(f"Refusing to remove unsafe destination: {destination}")

    is_junction = getattr(destination, "is_junction", lambda: False)()
    if destination.is_symlink():
        destination.unlink()
    elif is_junction:
        os.rmdir(destination)
    elif destination.is_dir():
        shutil.rmtree(destination)
    else:
        destination.unlink()


def apply_operations(
    operations: Sequence[Operation],
    target: Path,
    *,
    dry_run: bool,
    replace: bool,
    stream: TextIO,
) -> None:
    if not dry_run:
        target.mkdir(parents=True, exist_ok=True)

    for operation in operations:
        if operation.exists and not replace:
            prefix = "dry-run" if dry_run else "skip"
            print(
                f"[{prefix}] exists: {operation.name} -> {operation.destination} "
                "(use --replace to overwrite)",
                file=stream,
            )
            continue

        action = "replace" if operation.exists else "install"
        if dry_run:
            print(
                f"[dry-run] {action}: {operation.name} -> {operation.destination}",
                file=stream,
            )
            continue

        if operation.exists:
            _safe_remove(operation.destination, target)
        shutil.copytree(operation.source, operation.destination, symlinks=True)
        print(f"[ok] installed: {operation.name} -> {operation.destination}", file=stream)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Install selected skills from Codex Skills Library."
    )
    parser.add_argument("--list", action="store_true", help="List available skills and exit.")
    parser.add_argument(
        "--skill", action="append", metavar="NAME", help="Install one skill. Repeatable."
    )
    parser.add_argument("--all", action="store_true", help="Install every cataloged skill.")
    parser.add_argument(
        "--target",
        metavar="DIR",
        help="Destination skills directory. Defaults to ~/.agents/skills.",
    )
    parser.add_argument(
        "--codex-home",
        metavar="DIR",
        help="Deprecated compatibility option; installs into DIR/skills.",
    )
    parser.add_argument(
        "--replace", action="store_true", help="Replace matching installed skill directories."
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Validate and show actions without writing."
    )
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    root: Path = ROOT,
    default_target: Path | None = None,
    stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr,
) -> int:
    argv_list = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()
    args = parser.parse_args(argv_list)

    try:
        skills = load_catalog(root)
        if args.list:
            if args.skill or args.all:
                raise InstallError("--list cannot be combined with --skill or --all")
            print_catalog(skills, stdout)
            return 0

        if args.skill and args.all:
            raise InstallError("Choose either repeated --skill options or --all, not both")

        has_selection = bool(args.skill or args.all)
        if not has_selection:
            if not argv_list:
                print_catalog(skills, stdout)
                print(file=stdout)
                parser.print_help(stdout)
                return 0
            raise InstallError("Nothing selected; use --skill NAME, --all, or --list")

        if args.target and args.codex_home:
            raise InstallError("--target and deprecated --codex-home cannot be combined")

        if args.codex_home:
            print(
                "warning: --codex-home is deprecated; use --target DIR instead",
                file=stderr,
            )
            target = Path(args.codex_home).expanduser() / "skills"
        elif args.target:
            target = Path(args.target)
        else:
            target = default_target or (Path.home() / ".agents" / "skills")

        selected = select_skills(skills, args.skill, args.all)
        target, operations = plan_operations(root, selected, target)

        print(f"Library: {root.resolve()}", file=stdout)
        print(f"Target: {target}", file=stdout)
        if args.dry_run:
            print("Mode: dry-run", file=stdout)
        apply_operations(
            operations,
            target,
            dry_run=args.dry_run,
            replace=args.replace,
            stream=stdout,
        )
        return 0
    except (InstallError, OSError) as exc:
        print(f"error: {exc}", file=stderr)
        return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
