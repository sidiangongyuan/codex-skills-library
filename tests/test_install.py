from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "scripts"))

import install  # noqa: E402


def catalog_item(name: str, provenance: str = "original") -> dict[str, object]:
    return {
        "name": name,
        "category": "Testing",
        "description": f"Test skill {name}.",
        "path": f"skills/{name}",
        "example_prompt": f"${name} Run the test.",
        "tags": ["testing"],
        "requirements": [],
        "provenance": provenance,
        "source_url": "",
        "source_revision": "",
        "license_spdx": "MIT",
        "notice_path": "NOTICE.md",
    }


class InstallerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "library"
        self.root.mkdir()
        (self.root / "skills").mkdir()
        items = [catalog_item("alpha", "third-party-adapted"), catalog_item("beta")]
        (self.root / "skills.json").write_text(
            json.dumps({"schema_version": 2, "skills": items}), encoding="utf-8"
        )
        for name in ("alpha", "beta"):
            skill = self.root / "skills" / name
            skill.mkdir()
            (skill / "SKILL.md").write_text(f"# {name}\n", encoding="utf-8")
            (skill / "LICENSE").write_text(f"license for {name}\n", encoding="utf-8")
        self.target = Path(self.temporary.name) / "installed"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_installer(self, *args: str, default_target: Path | None = None):
        stdout = io.StringIO()
        stderr = io.StringIO()
        code = install.main(
            list(args),
            root=self.root,
            default_target=default_target or self.target,
            stdout=stdout,
            stderr=stderr,
        )
        return code, stdout.getvalue(), stderr.getvalue()

    def test_no_arguments_lists_catalog_without_writing(self) -> None:
        code, stdout, stderr = self.run_installer()
        self.assertEqual(code, 0)
        self.assertIn("Available skills (2)", stdout)
        self.assertIn("usage:", stdout)
        self.assertEqual(stderr, "")
        self.assertFalse(self.target.exists())

    def test_list_is_read_only(self) -> None:
        code, stdout, _ = self.run_installer("--list")
        self.assertEqual(code, 0)
        self.assertIn("alpha", stdout)
        self.assertFalse(self.target.exists())

    def test_single_and_repeated_skill_selection(self) -> None:
        code, _, _ = self.run_installer(
            "--skill", "alpha", "--skill", "beta", "--target", str(self.target)
        )
        self.assertEqual(code, 0)
        self.assertTrue((self.target / "alpha" / "SKILL.md").is_file())
        self.assertTrue((self.target / "beta" / "SKILL.md").is_file())
        self.assertEqual(
            (self.target / "alpha" / "LICENSE").read_text(encoding="utf-8"),
            "license for alpha\n",
        )

    def test_all_requires_explicit_flag(self) -> None:
        code, _, _ = self.run_installer("--all", "--target", str(self.target))
        self.assertEqual(code, 0)
        self.assertEqual(
            {path.name for path in self.target.iterdir()}, {"alpha", "beta"}
        )

    def test_unknown_skill_is_nonzero_and_writes_nothing(self) -> None:
        code, _, stderr = self.run_installer(
            "--skill", "missing", "--target", str(self.target)
        )
        self.assertEqual(code, 2)
        self.assertIn("Unknown skill", stderr)
        self.assertFalse(self.target.exists())

    def test_dry_run_does_not_create_target(self) -> None:
        code, stdout, _ = self.run_installer(
            "--all", "--dry-run", "--target", str(self.target)
        )
        self.assertEqual(code, 0)
        self.assertIn("[dry-run] install: alpha", stdout)
        self.assertFalse(self.target.exists())

    def test_existing_directory_skips_then_replaces_safely(self) -> None:
        destination = self.target / "alpha"
        destination.mkdir(parents=True)
        (destination / "old.txt").write_text("old", encoding="utf-8")

        code, stdout, _ = self.run_installer(
            "--skill", "alpha", "--target", str(self.target)
        )
        self.assertEqual(code, 0)
        self.assertIn("[skip] exists", stdout)
        self.assertTrue((destination / "old.txt").is_file())

        code, _, _ = self.run_installer(
            "--skill", "alpha", "--replace", "--target", str(self.target)
        )
        self.assertEqual(code, 0)
        self.assertFalse((destination / "old.txt").exists())
        self.assertTrue((destination / "SKILL.md").is_file())

    def test_replace_unlinks_symlink_without_following_it(self) -> None:
        self.target.mkdir()
        external = Path(self.temporary.name) / "external"
        external.mkdir()
        sentinel = external / "do-not-delete.txt"
        sentinel.write_text("preserve", encoding="utf-8")
        link = self.target / "alpha"
        try:
            link.symlink_to(external, target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"directory symlinks are unavailable: {exc}")

        code, _, stderr = self.run_installer(
            "--skill", "alpha", "--replace", "--target", str(self.target)
        )
        self.assertEqual(code, 0, stderr)
        self.assertTrue(sentinel.is_file())
        self.assertFalse(link.is_symlink())
        self.assertTrue((link / "SKILL.md").is_file())

    def test_deprecated_codex_home_maps_to_skills_subdirectory(self) -> None:
        codex_home = Path(self.temporary.name) / "codex-home"
        code, _, stderr = self.run_installer(
            "--skill", "alpha", "--codex-home", str(codex_home)
        )
        self.assertEqual(code, 0)
        self.assertIn("deprecated", stderr)
        self.assertTrue((codex_home / "skills" / "alpha" / "SKILL.md").is_file())

    def test_all_sources_are_validated_before_any_copy(self) -> None:
        missing = self.root / "skills" / "beta"
        for child in missing.iterdir():
            child.unlink()
        missing.rmdir()
        code, _, stderr = self.run_installer(
            "--skill", "alpha", "--skill", "beta", "--target", str(self.target)
        )
        self.assertEqual(code, 2)
        self.assertIn("Missing skill source", stderr)
        self.assertFalse(self.target.exists())


if __name__ == "__main__":
    unittest.main()
