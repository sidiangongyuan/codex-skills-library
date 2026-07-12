from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "scripts"))

import validate  # noqa: E402


@unittest.skipIf(validate.yaml is None, "PyYAML is not installed")
class ValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        skill = self.root / "skills" / "demo-skill"
        (skill / "agents").mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            "---\n"
            "name: demo-skill\n"
            "description: Use when validating a minimal public skill fixture.\n"
            "license: MIT\n"
            "---\n\n"
            "# Demo Skill\n",
            encoding="utf-8",
        )
        (skill / "LICENSE").write_text("MIT License\n", encoding="utf-8")
        (skill / "agents" / "openai.yaml").write_text(
            "interface:\n"
            "  display_name: Demo Skill\n"
            "  short_description: Validate a demo skill\n"
            '  default_prompt: "Use $demo-skill to validate this fixture."\n'
            "policy:\n"
            "  allow_implicit_invocation: true\n",
            encoding="utf-8",
        )
        (self.root / "NOTICE.md").write_text(
            "# Notices\n\nOriginal project work.\n", encoding="utf-8"
        )
        (self.root / "README.md").write_text(
            "# Demo\n\n[Skill](skills/demo-skill/SKILL.md)\n", encoding="utf-8"
        )
        item = {
            "name": "demo-skill",
            "category": "Demo",
            "description": "Validate a minimal public skill fixture.",
            "path": "skills/demo-skill",
            "example_prompt": "$demo-skill Validate the fixture.",
            "tags": ["demo", "validation"],
            "requirements": [],
            "provenance": "original",
            "source_url": "",
            "source_revision": "",
            "license_spdx": "MIT",
            "notice_path": "NOTICE.md",
        }
        (self.root / "skills.json").write_text(
            json.dumps(
                {
                    "schema_version": 2,
                    "repository": "sidiangongyuan/codex-skills-library",
                    "skills": [item],
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_valid_repository_fixture(self) -> None:
        self.assertEqual(validate.validate_repository(self.root), [])

    def test_missing_license_and_broken_link_are_reported(self) -> None:
        (self.root / "skills" / "demo-skill" / "LICENSE").unlink()
        with (self.root / "README.md").open("a", encoding="utf-8") as stream:
            stream.write("[Missing](docs/not-there.md)\n")
        errors = validate.validate_repository(self.root)
        joined = "\n".join(errors)
        self.assertIn("missing standalone LICENSE", joined)
        self.assertIn("broken relative link", joined)

    def test_removed_install_default_field_is_rejected(self) -> None:
        document = json.loads((self.root / "skills.json").read_text(encoding="utf-8"))
        document["skills"][0]["install_default"] = True
        (self.root / "skills.json").write_text(json.dumps(document), encoding="utf-8")
        errors = validate.validate_repository(self.root)
        self.assertTrue(any("install_default" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
