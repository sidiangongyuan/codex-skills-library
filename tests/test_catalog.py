from __future__ import annotations

import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "scripts"))

import catalog  # noqa: E402


class CatalogGeneratorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / "docs").mkdir()
        (self.root / "README.md").write_text(
            "# Demo\n\n"
            f"{catalog.README_START}\nold\n{catalog.README_END}\n",
            encoding="utf-8",
        )
        item = {
            "name": "demo-skill",
            "category": "Demo",
            "description": "Demonstrate generated documentation.",
            "path": "skills/demo-skill",
            "example_prompt": "$demo-skill Show the catalog.",
            "tags": ["demo"],
            "requirements": ["A test runner"],
            "provenance": "original",
            "source_url": "",
            "source_revision": "",
            "license_spdx": "MIT",
            "notice_path": "NOTICE.md",
        }
        (self.root / "skills.json").write_text(
            json.dumps({"schema_version": 2, "skills": [item]}), encoding="utf-8"
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_write_then_check_is_deterministic(self) -> None:
        with redirect_stdout(StringIO()):
            self.assertEqual(catalog.generate(self.root, check=False), 0)
        readme = (self.root / "README.md").read_text(encoding="utf-8")
        detail = (self.root / "docs" / "SKILL_CATALOG.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("[`demo-skill`](skills/demo-skill)", readme)
        self.assertIn("$demo-skill Show the catalog.", detail)
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            self.assertEqual(catalog.generate(self.root, check=True), 0)

    def test_check_detects_stale_generated_document(self) -> None:
        with redirect_stdout(StringIO()):
            catalog.generate(self.root, check=False)
        (self.root / "docs" / "SKILL_CATALOG.md").write_text(
            "stale\n", encoding="utf-8"
        )
        stderr = StringIO()
        with redirect_stderr(stderr):
            self.assertEqual(catalog.generate(self.root, check=True), 1)
        self.assertIn("docs/SKILL_CATALOG.md", stderr.getvalue().replace("\\", "/"))

    def test_missing_markers_are_rejected(self) -> None:
        (self.root / "README.md").write_text("# No markers\n", encoding="utf-8")
        with self.assertRaises(catalog.CatalogError):
            catalog.generate(self.root, check=False)


if __name__ == "__main__":
    unittest.main()
