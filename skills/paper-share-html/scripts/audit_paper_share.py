#!/usr/bin/env python3
"""Audit a static paper-sharing HTML package for common structural failures."""

from __future__ import annotations

import argparse
import os
import re
import struct
import sys
from collections import Counter
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

try:
    from PIL import Image as PILImage
    from PIL import ImageChops
except ImportError:  # Pillow improves crop checks but is not required at runtime.
    PILImage = None
    ImageChops = None


REQUIRED_DIRECTORIES = (
    "assets/figures",
    "assets/tables/raw",
    "source",
    "qa/archive",
)

META_PHRASES = (
    "一句话版",
    "外行版",
    "值得展示的表述",
    "下面保留",
    "这页适合",
    "这一页适合",
    "原文完整句子",
    "中文部分只说明",
    "引文位于",
    "本页将展示",
    "本页用于",
    "这一页将展示",
    "这一页用于",
    "这页用于",
    "结果解读",
    "表格解读",
    "给你一个",
    "向你解释",
    "核心 takeaway",
)

VOID_ELEMENTS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}
IGNORED_TEXT_ELEMENTS = {"script", "style", "noscript", "template"}
COMPRESSING_TABLE_CLASSES = {
    "card-grid",
    "cards",
    "columns",
    "comparison-grid",
    "split",
    "split-wide-visual",
    "takeaways",
    "three-column",
    "two-column",
}
MIN_TABLE_WIDTH = 1400
MIN_CONTENT_WIDTH_RATIO = 0.90
MIN_CONTENT_HEIGHT_RATIO = 0.82

PLACEHOLDER_PATTERNS = (
    re.compile(r"{{\s*[^{}]+\s*}}"),
    re.compile(r"\bTODO\b", re.IGNORECASE),
    re.compile(r"\bTBD\b", re.IGNORECASE),
    re.compile(r"\[\s*INSERT\b", re.IGNORECASE),
    re.compile(r"\bdata-template-placeholder\s*=", re.IGNORECASE),
)


@dataclass(frozen=True)
class ElementFrame:
    tag: str
    classes: frozenset[str]


@dataclass(frozen=True)
class ImageRecord:
    attrs: dict[str, str | None]
    ancestor_classes: frozenset[str]


class ReportParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.images: list[ImageRecord] = []
        self.references: list[tuple[str, str, str]] = []
        self.visible_text: list[str] = []
        self.visual_patterns: list[str | None] = []
        self.html_lang: str | None = None
        self.has_viewport = False
        self.slide_count = 0
        self._elements: list[ElementFrame] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._handle_starttag(tag, attrs, push=True)

    def _handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
        *,
        push: bool,
    ) -> None:
        attr = {key.lower(): value for key, value in attrs}
        lowered_tag = tag.lower()

        element_id = attr.get("id")
        if element_id:
            self.ids.append(element_id)

        classes = set((attr.get("class") or "").split())
        if "slide" in classes:
            self.slide_count += 1
            raw_pattern = (attr.get("data-visual-pattern") or "").strip()
            pattern = raw_pattern.casefold().replace("_", "-") or None
            self.visual_patterns.append(pattern)

        if lowered_tag == "html":
            self.html_lang = attr.get("lang")
        elif lowered_tag == "meta" and (attr.get("name") or "").lower() == "viewport":
            self.has_viewport = bool(attr.get("content"))
        elif lowered_tag == "img":
            ancestor_classes = frozenset(
                class_name
                for element in self._elements
                for class_name in element.classes
            )
            self.images.append(ImageRecord(attr, ancestor_classes))

        for attribute in ("src", "href", "poster"):
            value = attr.get(attribute)
            if value:
                self.references.append((lowered_tag, attribute, value))

        if push and lowered_tag not in VOID_ELEMENTS:
            self._elements.append(ElementFrame(lowered_tag, frozenset(classes)))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._handle_starttag(tag, attrs, push=False)

    def handle_endtag(self, tag: str) -> None:
        lowered_tag = tag.lower()
        for index in range(len(self._elements) - 1, -1, -1):
            if self._elements[index].tag == lowered_tag:
                del self._elements[index:]
                break

    def handle_data(self, data: str) -> None:
        ignored = any(element.tag in IGNORED_TEXT_ELEMENTS for element in self._elements)
        if not ignored and data.strip():
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


def raster_dimensions(path: Path) -> tuple[int, int] | None:
    dimensions = png_dimensions(path)
    if dimensions is not None or PILImage is None:
        return dimensions
    try:
        with PILImage.open(path) as image:
            return image.size
    except (OSError, ValueError):
        return None


def table_content_occupancy(path: Path) -> tuple[float, float] | None:
    """Estimate non-background width and height ratios for a raster table crop."""
    if PILImage is None or ImageChops is None:
        return None
    try:
        with PILImage.open(path) as source:
            rgba = source.convert("RGBA")
    except (OSError, ValueError):
        return None

    white = PILImage.new("RGBA", rgba.size, (255, 255, 255, 255))
    rgb = PILImage.alpha_composite(white, rgba).convert("RGB")
    width, height = rgb.size
    if width == 0 or height == 0:
        return None

    corners = (
        rgb.getpixel((0, 0)),
        rgb.getpixel((width - 1, 0)),
        rgb.getpixel((0, height - 1)),
        rgb.getpixel((width - 1, height - 1)),
    )
    background = tuple(
        sorted(pixel[channel] for pixel in corners)[len(corners) // 2]
        for channel in range(3)
    )
    difference = ImageChops.difference(
        rgb,
        PILImage.new("RGB", rgb.size, background),
    ).convert("L")
    mask = difference.point(lambda value: 255 if value > 18 else 0)
    bounds = mask.getbbox()
    if bounds is None:
        return 0.0, 0.0
    left, top, right, bottom = bounds
    return (right - left) / width, (bottom - top) / height


def repeated_visual_pattern_warnings(patterns: list[str | None]) -> list[str]:
    warnings: list[str] = []
    index = 0
    while index < len(patterns):
        if patterns[index] != "horizontal-chain":
            index += 1
            continue
        end = index + 1
        while end < len(patterns) and patterns[end] == "horizontal-chain":
            end += 1
        if end - index >= 3:
            warnings.append(
                "slides "
                f"{index + 1}-{end} repeat data-visual-pattern=horizontal-chain; "
                "choose a relationship-specific composition unless all are truly sequential"
            )
        index = end
    return warnings


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

    visible_text = re.sub(r"\s+", " ", " ".join(parser.visible_text)).casefold()
    for phrase in META_PHRASES:
        if phrase.casefold() in visible_text:
            errors.append(f"audience-facing copy contains meta phrase: {phrase}")

    warnings.extend(repeated_visual_pattern_warnings(parser.visual_patterns))

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

    table_images: list[tuple[ImageRecord, Path, str]] = []
    for image_record in parser.images:
        image = image_record.attrs
        src = image.get("src") or ""
        alt = image.get("alt")
        if "data-decorative" not in image and not (alt and alt.strip()):
            errors.append(f"image is missing descriptive alt text: {src or '<missing src>'}")
        normalized = src.replace("\\", "/").lstrip("./")
        if normalized.startswith("assets/tables/") and "/raw/" not in normalized:
            target, problem = resolve_local_reference(root, src)
            if target is not None and not problem:
                table_images.append((image_record, target, src))

    raw_table_dir = root / "assets" / "tables" / "raw"
    for image_record, target, src in table_images:
        image = image_record.attrs
        classes = set((image.get("class") or "").split())
        if "data-zoomable" not in image and "zoomable" not in classes:
            errors.append(f"table image is not click-to-zoom: {src}")
        compressed_by = sorted(
            image_record.ancestor_classes.intersection(COMPRESSING_TABLE_CLASSES)
        )
        if compressed_by:
            warnings.append(
                f"table image is inside a potentially compressed layout: {src} "
                f"({', '.join(compressed_by)})"
            )
        dimensions = raster_dimensions(target) if target.exists() else None
        if dimensions and dimensions[0] < MIN_TABLE_WIDTH:
            warnings.append(
                f"table image may be too narrow for a full slide: {src} ({dimensions[0]}x{dimensions[1]})"
            )
        occupancy = table_content_occupancy(target) if target.exists() else None
        if occupancy is not None:
            content_width, content_height = occupancy
            if (
                content_width < MIN_CONTENT_WIDTH_RATIO
                or content_height < MIN_CONTENT_HEIGHT_RATIO
            ):
                warnings.append(
                    f"table crop may include excess background: {src} "
                    f"(content occupies {content_width:.1%} width and "
                    f"{content_height:.1%} height; expected at least "
                    f"{MIN_CONTENT_WIDTH_RATIO:.0%} and "
                    f"{MIN_CONTENT_HEIGHT_RATIO:.0%})"
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
