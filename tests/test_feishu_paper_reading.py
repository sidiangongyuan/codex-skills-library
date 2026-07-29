from __future__ import annotations

import subprocess
import sys
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


if __name__ == "__main__":
    unittest.main()
