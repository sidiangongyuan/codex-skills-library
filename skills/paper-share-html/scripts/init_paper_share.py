#!/usr/bin/env python3
"""Create a non-destructive paper-share HTML package from the bundled template."""

from __future__ import annotations

import argparse
import html
import re
import shutil
import sys
from pathlib import Path


INVALID_WINDOWS_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
RESERVED_WINDOWS_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def safe_folder_name(title: str, override: str | None = None) -> str:
    """Return a readable, Windows-safe main-title folder name."""
    candidate = (override or re.split(r"[:：]", title, maxsplit=1)[0]).strip()
    candidate = INVALID_WINDOWS_CHARS.sub(" - ", candidate)
    candidate = re.sub(r"\s+", " ", candidate)
    candidate = re.sub(r"(?:\s+-\s+)+", " - ", candidate)
    candidate = candidate.rstrip(" .")
    if not candidate:
        raise ValueError("The title does not contain a usable folder name.")
    if candidate.upper() in RESERVED_WINDOWS_NAMES:
        candidate = f"_{candidate}"
    if len(candidate) > 120:
        candidate = candidate[:120].rstrip(" .-")
    return candidate


def build_package(title: str, root: Path, folder_name: str | None = None) -> Path:
    skill_root = Path(__file__).resolve().parents[1]
    template = skill_root / "assets" / "template" / "index.html"
    if not template.is_file():
        raise FileNotFoundError(f"Bundled template not found: {template}")

    destination = root.expanduser().resolve() / safe_folder_name(title, folder_name)
    if destination.exists():
        raise FileExistsError(f"Destination already exists; refusing to overwrite: {destination}")

    destination.mkdir(parents=True)
    for relative in (
        "assets/figures",
        "assets/tables/raw",
        "source",
        "qa/archive",
    ):
        (destination / relative).mkdir(parents=True)

    rendered = template.read_text(encoding="utf-8")
    escaped_title = html.escape(title, quote=True)
    rendered = rendered.replace("{{DOCUMENT_TITLE}}", escaped_title)
    rendered = rendered.replace("{{PAPER_TITLE}}", escaped_title)
    (destination / "index.html").write_text(rendered, encoding="utf-8", newline="\n")
    return destination


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a static paper-sharing HTML package without overwriting existing work."
    )
    parser.add_argument("--title", required=True, help="Full paper title.")
    parser.add_argument("--root", required=True, type=Path, help="Parent output directory.")
    parser.add_argument(
        "--folder-name",
        help="Optional folder name override; defaults to the title before the first colon.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        destination = build_package(args.title, args.root, args.folder_name)
    except (FileExistsError, FileNotFoundError, ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
