#!/usr/bin/env python3
"""Audit a static paper-sharing HTML package for common structural failures."""

from __future__ import annotations

import argparse
import os
import re
import struct
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


REQUIRED_DIRECTORIES = (
    "assets/figures",
    "assets/tables/raw",
    "source",
    "qa/archive",
)

META_PHRASES = (
    "一句话版",
    "外行版",
    "文中几处值得展示的表述",
    "值得展示的表述",
    "下面保留原文",
    "下面保留",
    "这页适合",
    "这一页适合",
    "结果解读",
    "表格解读",
    "给你一个",
)

PLACEHOLDER_PATTERNS = (
    re.compile(r"{{\s*[^{}]+\s*}}"),
    re.compile(r"\bTODO\b", re.IGNORECASE),
    re.compile(r"\bTBD\b", re.IGNORECASE),
    re.compile(r"\[\s*INSERT\b", re.IGNORECASE),
)


class ReportParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.images: list[dict[str, str | None]] = []
        self.references: list[tuple[str, str, str]] = []
        self.visible_text: list[str] = []
        self.html_lang: str | None = None
        self.has_viewport = False
        self.slide_count = 0
        self._ignored_tags: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {key.lower(): value for key, value in attrs}
        lowered_tag = tag.lower()
        if lowered_tag in {"script", "style", "noscript", "template"}:
            self._ignored_tags.append(lowered_tag)

        element_id = attr.get("id")
        if element_id:
            self.ids.append(element_id)

        classes = set((attr.get("class") or "").split())
        if "slide" in classes:
            self.slide_count += 1

        if lowered_tag == "html":
            self.html_lang = attr.get("lang")
        elif lowered_tag == "meta" and (attr.get("name") or "").lower() == "viewport":
            self.has_viewport = bool(attr.get("content"))
        elif lowered_tag == "img":
            self.images.append(attr)

        for attribute in ("src", "href", "poster"):
            value = attr.get(attribute)
            if value:
                self.references.append((lowered_tag, attribute, value))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag.lower() in {"script", "style", "noscript", "template"} and self._ignored_tags:
            self._ignored_tags.pop()

    def handle_endtag(self, tag: str) -> None:
        lowered_tag = tag.lower()
        if self._ignored_tags and self._ignored_tags[-1] == lowered_tag:
            self._ignored_tags.pop()

    def handle_data(self, data: str) -> None:
        if not self._ignored_tags and data.strip():
            self.visible_text.append(data)


def png_dimensions(path: Path) -> tuple[int, int] | None:
    try:
        with path.open("rb") as handle:
            header = handle.read(24)
    except OSError:
        return None
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", header[16:24])


def is_remote_or_fragment(reference: str) -> bool:
    stripped = reference.strip()
    if not stripped or stripped.startswith("#") or stripped.startswith("//"):
        return True
    scheme = urlsplit(stripped).scheme.lower()
    return scheme in {"http", "https", "mailto", "tel", "data", "javascript"}


def resolve_local_reference(report_root: Path, reference: str) -> tuple[Path | None, str | None]:
    if is_remote_or_fragment(reference):
        return None, None
    split = urlsplit(reference)
    raw_path = unquote(split.path)
    if not raw_path:
        return None, None
    if split.scheme or os.path.isabs(raw_path) or re.match(r"^[A-Za-z]:[\\/]", raw_path):
        return None, "absolute local path"
    resolved = (report_root / Path(raw_path.replace("/", os.sep))).resolve()
    try:
        resolved.relative_to(report_root.resolve())
    except ValueError:
        return None, "path escapes the paper package"
    return resolved, None


def audit(report_root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    root = report_root.expanduser().resolve()
    index = root / "index.html"

    if not root.is_dir():
        return [f"paper package does not exist: {root}"], warnings
    if not index.is_file():
        return [f"missing required file: {index}"], warnings
    for relative in REQUIRED_DIRECTORIES:
        if not (root / relative).is_dir():
            errors.append(f"missing required directory: {relative}")

    try:
        raw_html = index.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [f"cannot read index.html as UTF-8: {exc}"], warnings

    parser = ReportParser()
    try:
        parser.feed(raw_html)
    except Exception as exc:  # HTMLParser errors are rare; preserve a useful audit result.
        errors.append(f"HTML parsing failed: {exc}")

    if not parser.html_lang:
        errors.append("the html element is missing a lang attribute")
    if not parser.has_viewport:
        errors.append("missing viewport meta tag")
    if "@media print" not in raw_html:
        errors.append("missing print stylesheet")
    if parser.slide_count < 2:
        warnings.append(f"only {parser.slide_count} slide section(s) detected")
    if "ArrowRight" not in raw_html or "ArrowLeft" not in raw_html:
        warnings.append("keyboard previous/next navigation was not detected")

    duplicate_ids = sorted(identifier for identifier, count in Counter(parser.ids).items() if count > 1)
    for identifier in duplicate_ids:
        errors.append(f"duplicate id: {identifier}")

    visible_text = re.sub(r"\s+", " ", " ".join(parser.visible_text))
    for phrase in META_PHRASES:
        if phrase in visible_text:
            errors.append(f"audience-facing copy contains meta phrase: {phrase}")

    for pattern in PLACEHOLDER_PATTERNS:
        match = pattern.search(raw_html)
        if match:
            errors.append(f"unresolved placeholder: {match.group(0)}")

    for tag, attribute, reference in parser.references:
        target, problem = resolve_local_reference(root, reference)
        if problem:
            errors.append(f"{tag}[{attribute}] uses {problem}: {reference}")
        elif target is not None and not target.exists():
            errors.append(f"broken local reference in {tag}[{attribute}]: {reference}")

    table_images: list[tuple[dict[str, str | None], Path, str]] = []
    for image in parser.images:
        src = image.get("src") or ""
        alt = image.get("alt")
        if "data-decorative" not in image and not (alt and alt.strip()):
            errors.append(f"image is missing descriptive alt text: {src or '<missing src>'}")
        normalized = src.replace("\\", "/").lstrip("./")
        if normalized.startswith("assets/tables/") and "/raw/" not in normalized:
            target, problem = resolve_local_reference(root, src)
            if target is not None and not problem:
                table_images.append((image, target, src))

    raw_table_dir = root / "assets" / "tables" / "raw"
    for image, target, src in table_images:
        classes = set((image.get("class") or "").split())
        if "data-zoomable" not in image and "zoomable" not in classes:
            errors.append(f"table image is not click-to-zoom: {src}")
        dimensions = png_dimensions(target) if target.exists() else None
        if dimensions and dimensions[0] < 1400:
            warnings.append(
                f"table image may be too narrow for a full slide: {src} ({dimensions[0]}x{dimensions[1]})"
            )
        if target.exists():
            raw_candidates = (
                raw_table_dir / f"{target.stem}_raw{target.suffix}",
                raw_table_dir / target.name,
            )
            if not any(candidate.exists() for candidate in raw_candidates):
                warnings.append(f"no raw capture found for table image: {src}")

    lowered_html = raw_html.lower()
    has_dialog = "<dialog" in lowered_html or re.search(
        r"role\s*=\s*['\"]dialog['\"]", lowered_html
    )
    if table_images and not has_dialog:
        warnings.append("table images exist but an accessible dialog lightbox was not detected")

    for expected_source in ("paper.pdf", "citation.bib", "links.md"):
        if not (root / "source" / expected_source).is_file():
            warnings.append(f"source archive is missing: source/{expected_source}")

    return errors, warnings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit a static paper-sharing HTML package.")
    parser.add_argument("paper_folder", type=Path, help="Folder containing index.html.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return a failure status when warnings remain.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors, warnings = audit(args.paper_folder)
    for message in errors:
        print(f"ERROR: {message}")
    for message in warnings:
        print(f"WARN: {message}")
    if errors:
        print(f"Audit failed: {len(errors)} error(s), {len(warnings)} warning(s).")
        return 1
    if args.strict and warnings:
        print(f"Audit failed in strict mode: {len(warnings)} warning(s).")
        return 1
    print(f"Audit passed: {len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
