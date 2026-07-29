from __future__ import annotations

import json
import os
import re
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = (
    REPOSITORY_ROOT
    / "skills"
    / "feishu-paper-reading"
    / "scripts"
    / "validate_digest.py"
)
CONNECTION_PREFLIGHT = (
    REPOSITORY_ROOT
    / "skills"
    / "feishu-paper-reading"
    / "scripts"
    / "check_feishu_connection.py"
)
AUTH_HELPER = (
    REPOSITORY_ROOT
    / "skills"
    / "feishu-paper-reading"
    / "scripts"
    / "run_feishu_auth.py"
)
PUBLICATION_CHECKPOINT = (
    REPOSITORY_ROOT
    / "skills"
    / "feishu-paper-reading"
    / "scripts"
    / "publication_checkpoint.py"
)
ONBOARDING_REFERENCE = (
    REPOSITORY_ROOT
    / "skills"
    / "feishu-paper-reading"
    / "references"
    / "feishu-onboarding.md"
)
PUBLISHING_REFERENCE = (
    REPOSITORY_ROOT
    / "skills"
    / "feishu-paper-reading"
    / "references"
    / "feishu-publishing.md"
)
SHOWCASE_EN = REPOSITORY_ROOT / "docs" / "FEISHU_PAPER_READING.md"
SHOWCASE_ZH = REPOSITORY_ROOT / "docs" / "FEISHU_PAPER_READING.zh-CN.md"
WORKFLOW_MMD = (
    REPOSITORY_ROOT / "figures" / "feishu-paper-reading-workflow.mmd"
)
WORKFLOW_WRAPPER = (
    REPOSITORY_ROOT / "figures" / "feishu-paper-reading-workflow.md"
)
WORKFLOW_PNG = (
    REPOSITORY_ROOT / "figures" / "feishu-paper-reading-workflow.png"
)
SHOWCASE_SCREENSHOTS = (
    REPOSITORY_ROOT
    / "assets"
    / "feishu-paper-reading"
    / "actual-summary.png",
    REPOSITORY_ROOT
    / "assets"
    / "feishu-paper-reading"
    / "actual-insight.png",
)


def png_dimensions(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:24]
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError(f"Not a PNG file: {path}")
    return struct.unpack(">II", header[16:24])


def png_chunk_types(path: Path) -> tuple[bytes, ...]:
    content = path.read_bytes()
    if content[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError(f"Not a PNG file: {path}")
    offset = 8
    chunks: list[bytes] = []
    while offset + 12 <= len(content):
        length = struct.unpack(">I", content[offset : offset + 4])[0]
        end = offset + 12 + length
        if end > len(content):
            raise AssertionError(f"Truncated PNG chunk: {path}")
        chunk_type = content[offset + 4 : offset + 8]
        chunks.append(chunk_type)
        offset = end
        if chunk_type == b"IEND":
            break
    if not chunks or chunks[-1] != b"IEND":
        raise AssertionError(f"Missing PNG IEND chunk: {path}")
    return tuple(chunks)


class FeishuPaperReadingTests(unittest.TestCase):
    def test_digest_validator_self_test(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR), "--self-test"],
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        self.assertEqual(
            completed.returncode,
            0,
            msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
        )
        self.assertIn("Self-test passed.", completed.stdout)

    def test_connection_preflight_self_test(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(CONNECTION_PREFLIGHT), "--self-test"],
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        self.assertEqual(
            completed.returncode,
            0,
            msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
        )
        self.assertEqual(json.loads(completed.stdout), {"self_test": "passed"})

    def test_connection_preflight_actionable_state_exits_zero(self) -> None:
        environment = os.environ.copy()
        environment["PATH"] = ""
        completed = subprocess.run(
            [sys.executable, str(CONNECTION_PREFLIGHT), "--json"],
            cwd=REPOSITORY_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        self.assertEqual(
            completed.returncode,
            0,
            msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
        )
        report = json.loads(completed.stdout)
        self.assertFalse(report["ok"])
        self.assertTrue(report["state_recognized"])
        self.assertEqual(report["state"], "absent")
        self.assertFalse(report["authorization_ready"])
        self.assertFalse(report["delivery_verified"])

    def test_connection_preflight_never_executes_a_path_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            marker = root / "executed.txt"
            if os.name == "nt":
                candidate = root / "lark-cli.cmd"
                candidate.write_text(
                    "@echo executed>\"%MALICIOUS_MARKER%\"\n",
                    encoding="utf-8",
                )
            else:
                candidate = root / "lark-cli"
                candidate.write_text(
                    "#!/bin/sh\nprintf executed > \"$MALICIOUS_MARKER\"\n",
                    encoding="utf-8",
                )
                candidate.chmod(0o700)
            environment = os.environ.copy()
            environment["PATH"] = directory
            environment["MALICIOUS_MARKER"] = os.fspath(marker)
            completed = subprocess.run(
                [sys.executable, str(CONNECTION_PREFLIGHT), "--json"],
                cwd=REPOSITORY_ROOT,
                env=environment,
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
            self.assertEqual(completed.returncode, 0)
            report = json.loads(completed.stdout)
            self.assertEqual(report["state"], "cli_review_required")
            self.assertFalse(marker.exists())

    def test_auth_helper_self_test(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(AUTH_HELPER), "--self-test"],
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        self.assertEqual(
            completed.returncode,
            0,
            msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
        )
        self.assertEqual(json.loads(completed.stdout), {"self_test": "passed"})
        self.assertEqual(completed.stderr, "")

    def test_auth_helper_requires_an_explicit_binary_binding(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "auth.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(AUTH_HELPER),
                    "--state-file",
                    str(state),
                    "--brand",
                    "feishu",
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
            self.assertEqual(completed.returncode, 2)
            self.assertFalse(state.exists())

    def test_publication_checkpoint_self_test(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(PUBLICATION_CHECKPOINT), "--self-test"],
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        self.assertEqual(
            completed.returncode,
            0,
            msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
        )
        self.assertEqual(
            json.loads(completed.stdout),
            {"ok": True, "self_test": "passed"},
        )
        self.assertEqual(completed.stderr, "")

    def test_documented_checkpoint_commands_include_required_bindings(self) -> None:
        onboarding = ONBOARDING_REFERENCE.read_text(encoding="utf-8")
        publishing = PUBLISHING_REFERENCE.read_text(encoding="utf-8")
        self.assertGreaterEqual(
            onboarding.count('--delivery-route "lark-cli"'),
            2,
        )
        for required_flag in (
            "--lark-cli",
            "--approved-executable-sha256",
            "--profile",
            "--config-dir",
            "--data-dir",
            "--brand",
            "--app-id-sha256",
            "--user-open-id-sha256",
        ):
            self.assertGreaterEqual(onboarding.count(required_flag), 2)
        self.assertGreaterEqual(
            publishing.count('--delivery-route "connector"'),
            2,
        )
        self.assertGreaterEqual(publishing.count("--connector-id"), 2)
        self.assertGreaterEqual(
            publishing.count("--connector-identity-sha256"),
            2,
        )
        self.assertIn("run_feishu_config_init.py", onboarding)
        self.assertIn("feishu_process_environment.py", onboarding)
        self.assertIn("LARKSUITE_CLI_*", onboarding)
        self.assertNotIn(
            '"<absolute-lark-cli-path>" config init',
            onboarding,
        )

    def test_showcase_pages_and_assets_are_publishable(self) -> None:
        english = SHOWCASE_EN.read_text(encoding="utf-8")
        chinese = SHOWCASE_ZH.read_text(encoding="utf-8")
        root_readme = (REPOSITORY_ROOT / "README.md").read_text(
            encoding="utf-8"
        )
        chinese_readme = (REPOSITORY_ROOT / "README.zh-CN.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("FEISHU_PAPER_READING.zh-CN.md", english)
        self.assertIn("FEISHU_PAPER_READING.md", chinese)
        self.assertIn("FEISHU_PAPER_READING.md", root_readme)
        self.assertIn("FEISHU_PAPER_READING.zh-CN.md", chinese_readme)

        for screenshot in SHOWCASE_SCREENSHOTS:
            self.assertTrue(screenshot.is_file(), screenshot)
            width, height = png_dimensions(screenshot)
            self.assertGreaterEqual(width, 1500)
            self.assertGreaterEqual(height, 500)
            reference = f"../assets/feishu-paper-reading/{screenshot.name}"
            self.assertIn(reference, english)
            self.assertIn(reference, chinese)

        self.assertTrue(WORKFLOW_PNG.is_file(), WORKFLOW_PNG)
        workflow_width, workflow_height = png_dimensions(WORKFLOW_PNG)
        self.assertGreaterEqual(workflow_width, 1500)
        self.assertGreaterEqual(workflow_height, 1000)
        self.assertIn(
            "../figures/feishu-paper-reading-workflow.png",
            english,
        )
        self.assertIn(
            "../figures/feishu-paper-reading-workflow.png",
            chinese,
        )
        for image in (*SHOWCASE_SCREENSHOTS, WORKFLOW_PNG):
            chunks = set(png_chunk_types(image))
            self.assertTrue(
                chunks.isdisjoint({b"tEXt", b"iTXt", b"zTXt", b"eXIf"}),
                msg=f"Unexpected textual or EXIF metadata in {image}: {chunks}",
            )

        source = WORKFLOW_MMD.read_text(encoding="utf-8").strip()
        wrapper = WORKFLOW_WRAPPER.read_text(encoding="utf-8")
        fenced = wrapper.split("```mermaid\n", 1)[1].rsplit("\n```", 1)[0]
        self.assertEqual(source, fenced.strip())

        public_files = (
            REPOSITORY_ROOT / "README.md",
            REPOSITORY_ROOT / "README.zh-CN.md",
            REPOSITORY_ROOT / "docs" / "USAGE.md",
            SHOWCASE_EN,
            SHOWCASE_ZH,
            WORKFLOW_MMD,
            WORKFLOW_WRAPPER,
        )
        public_copy = "\n".join(
            path.read_text(encoding="utf-8") for path in public_files
        )
        self.assertNotIn("feishu.cn/docx/", public_copy)
        self.assertIsNone(
            re.search(
                r"(?i)\b[a-z]:\\(?:users|documents|appdata)\\",
                public_copy,
            )
        )
        self.assertIsNone(
            re.search(
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
                public_copy,
            )
        )
        self.assertIsNone(
            re.search(
                r"\b(?=[A-Za-z0-9]{20,32}\b)"
                r"(?=[A-Za-z0-9]*[A-Z])"
                r"(?=[A-Za-z0-9]*[a-z])"
                r"(?=[A-Za-z0-9]*\d)"
                r"[A-Za-z0-9]+\b",
                public_copy,
            )
        )


if __name__ == "__main__":
    unittest.main()
