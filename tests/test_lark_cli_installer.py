from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
INSTALLER = (
    REPOSITORY_ROOT
    / "skills"
    / "feishu-paper-reading"
    / "scripts"
    / "install_lark_cli.py"
)


class LarkCliInstallerTests(unittest.TestCase):
    def _run(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(INSTALLER), *arguments],
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )

    def test_self_test_is_local_and_passes(self) -> None:
        completed = self._run("--self-test")
        self.assertEqual(
            completed.returncode,
            0,
            msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
        )
        self.assertEqual(json.loads(completed.stdout), {"self_test": "passed"})
        self.assertEqual(completed.stderr, "")

    def test_install_requires_external_consent_attestation(self) -> None:
        completed = self._run("--version", "1.2.3")
        self.assertEqual(completed.returncode, 2)
        payload = json.loads(completed.stderr)
        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["error"]["code"], "consent_required")
        self.assertEqual(completed.stdout, "")

    def test_invalid_exact_version_fails_before_network(self) -> None:
        completed = self._run(
            "--consent-confirmed",
            "--version",
            "v1.2.3-beta",
        )
        self.assertEqual(completed.returncode, 2)
        payload = json.loads(completed.stderr)
        self.assertEqual(payload["error"]["code"], "invalid_version")
        self.assertEqual(completed.stdout, "")

    def test_consented_install_requires_the_complete_inspected_plan(self) -> None:
        completed = self._run(
            "--consent-confirmed",
            "--version",
            "1.2.3",
        )
        self.assertEqual(completed.returncode, 2)
        payload = json.loads(completed.stderr)
        self.assertEqual(payload["error"]["code"], "unpinned_install_plan")
        self.assertEqual(completed.stdout, "")

    def test_invalid_approved_checksum_fails_before_network(self) -> None:
        completed = self._run(
            "--consent-confirmed",
            "--version",
            "1.2.3",
            "--expected-asset",
            "lark-cli-1.2.3-windows-amd64.zip",
            "--expected-sha256",
            "not-a-sha256",
        )
        self.assertEqual(completed.returncode, 2)
        payload = json.loads(completed.stderr)
        self.assertEqual(payload["error"]["code"], "invalid_expected_sha256")
        self.assertEqual(completed.stdout, "")


if __name__ == "__main__":
    unittest.main()
