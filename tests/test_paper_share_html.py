from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

try:
    from PIL import Image, ImageDraw
except ImportError:  # The public skill keeps Pillow optional.
    Image = None
    ImageDraw = None


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPOSITORY_ROOT / "skills" / "paper-share-html"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


audit_module = load_module(
    "paper_share_audit",
    SKILL_ROOT / "scripts" / "audit_paper_share.py",
)
init_module = load_module(
    "paper_share_init",
    SKILL_ROOT / "scripts" / "init_paper_share.py",
)


class PaperShareAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "paper"
        for relative in (
            "assets/figures",
            "assets/tables/raw",
            "source",
            "qa/archive",
        ):
            (self.root / relative).mkdir(parents=True, exist_ok=True)
        for name in ("paper.pdf", "citation.bib", "links.md"):
            (self.root / "source" / name).write_text("fixture\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_table(
        self,
        *,
        size: tuple[int, int] = (1600, 600),
        content_box: tuple[int, int, int, int] = (40, 45, 1560, 555),
    ) -> None:
        if Image is None or ImageDraw is None:
            self.skipTest("Pillow is not installed")
        image = Image.new("RGB", size, "white")
        draw = ImageDraw.Draw(image)
        draw.rectangle(content_box, outline="black", width=8)
        table = self.root / "assets" / "tables" / "main.png"
        raw = self.root / "assets" / "tables" / "raw" / "main.png"
        image.save(table)
        image.save(raw)
        image.close()

    def write_html(
        self,
        *,
        include_table: bool = True,
        wrapper_classes: str = "table-stage",
        patterns: tuple[str | None, ...] = (None, None, None),
        audience_text: str = "Source-grounded result.",
    ) -> None:
        sections: list[str] = []
        for index, pattern in enumerate(patterns, start=1):
            pattern_attr = f' data-visual-pattern="{pattern}"' if pattern else ""
            table_html = ""
            if include_table and index == 2:
                table_html = (
                    f'<div class="{wrapper_classes}">'
                    '<img src="assets/tables/main.png" alt="Benchmark results" '
                    'class="table-image zoomable" data-zoomable>'
                    "</div>"
                )
            sections.append(
                f'<section class="slide" id="slide-{index}"{pattern_attr}>'
                f"<h2>Slide {index}</h2>{table_html}<p>{audience_text}</p>"
                "</section>"
            )
        html = (
            '<!doctype html><html lang="en"><head>'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            "<style>@media print { .slide { break-after: page; } }</style>"
            "</head><body>"
            + "".join(sections)
            + '<dialog aria-label="Enlarged image"></dialog>'
            '<script>const keys = ["ArrowRight", "ArrowLeft"];</script>'
            "</body></html>"
        )
        (self.root / "index.html").write_text(html, encoding="utf-8")

    def test_tight_high_resolution_table_passes(self) -> None:
        self.write_table()
        self.write_html()
        errors, warnings = audit_module.audit(self.root)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_low_resolution_table_warns(self) -> None:
        self.write_table(
            size=(1200, 600),
            content_box=(20, 40, 1180, 560),
        )
        self.write_html()
        _, warnings = audit_module.audit(self.root)
        self.assertTrue(any("too narrow" in warning for warning in warnings))

    def test_large_empty_margins_warn(self) -> None:
        self.write_table(content_box=(300, 180, 1300, 420))
        self.write_html()
        _, warnings = audit_module.audit(self.root)
        self.assertTrue(any("excess background" in warning for warning in warnings))

    def test_compressed_table_layout_warns(self) -> None:
        self.write_table()
        self.write_html(wrapper_classes="table-stage split")
        _, warnings = audit_module.audit(self.root)
        self.assertTrue(any("compressed layout" in warning for warning in warnings))

    def test_three_horizontal_chains_warn(self) -> None:
        self.write_html(
            include_table=False,
            patterns=("horizontal-chain", "horizontal-chain", "horizontal-chain"),
        )
        _, warnings = audit_module.audit(self.root)
        self.assertTrue(any("repeat data-visual-pattern" in warning for warning in warnings))

    def test_two_horizontal_chains_do_not_warn(self) -> None:
        self.write_html(
            include_table=False,
            patterns=("horizontal-chain", "horizontal-chain", "matrix"),
        )
        _, warnings = audit_module.audit(self.root)
        self.assertFalse(any("repeat data-visual-pattern" in warning for warning in warnings))

    def test_new_meta_narration_is_rejected(self) -> None:
        self.write_html(
            include_table=False,
            audience_text="本页将展示原文完整句子，中文部分只说明它的作用。",
        )
        errors, _ = audit_module.audit(self.root)
        joined = "\n".join(errors)
        self.assertIn("本页将展示", joined)
        self.assertIn("原文完整句子", joined)
        self.assertIn("中文部分只说明", joined)

    def test_template_visual_marker_is_rejected(self) -> None:
        self.write_html(include_table=False)
        index = self.root / "index.html"
        html = index.read_text(encoding="utf-8").replace(
            "<h2>Slide 1</h2>",
            '<h2 data-template-placeholder="replace-me">Slide 1</h2>',
        )
        index.write_text(html, encoding="utf-8")
        errors, _ = audit_module.audit(self.root)
        self.assertTrue(any("data-template-placeholder" in error for error in errors))

    def test_missing_pillow_skips_only_pixel_crop_check(self) -> None:
        self.write_table(content_box=(300, 180, 1300, 420))
        self.write_html()
        with mock.patch.object(audit_module, "PILImage", None), mock.patch.object(
            audit_module,
            "ImageChops",
            None,
        ):
            errors, warnings = audit_module.audit(self.root)
        self.assertEqual(errors, [])
        self.assertFalse(any("excess background" in warning for warning in warnings))


class PaperShareInitializerTests(unittest.TestCase):
    def test_title_with_colon_and_apostrophe_creates_safe_folder(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            destination = init_module.build_package(
                "Researcher's Guide: Strong Assumptions",
                root,
            )
            self.assertEqual(destination.name, "Researcher's Guide")
            html = (destination / "index.html").read_text(encoding="utf-8")
            self.assertIn("Researcher&#x27;s Guide: Strong Assumptions", html)

    def test_existing_destination_is_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            init_module.build_package("Existing: Paper", root)
            with self.assertRaises(FileExistsError):
                init_module.build_package("Existing: Paper", root)


if __name__ == "__main__":
    unittest.main()
