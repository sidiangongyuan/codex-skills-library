from __future__ import annotations

import json
import os
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


if __name__ == "__main__":
    unittest.main()
