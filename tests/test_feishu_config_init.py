from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIRECTORY = (
    REPOSITORY_ROOT / "skills" / "feishu-paper-reading" / "scripts"
)
sys.path.insert(0, str(SCRIPTS_DIRECTORY))
import run_feishu_config_init as config_init  # noqa: E402


CONFIG_INIT_HELPER = (
    SCRIPTS_DIRECTORY / "run_feishu_config_init.py"
)


class FeishuConfigInitTests(unittest.TestCase):
    def test_self_test_covers_isolation_and_secret_suppression(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(CONFIG_INIT_HELPER), "--self-test"],
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

    def test_fresh_setup_requires_explicit_consent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / "state.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(CONFIG_INIT_HELPER),
                    "--state-file",
                    str(state),
                    "--config-parent",
                    str(root),
                    "--brand",
                    "feishu",
                    "--lark-cli",
                    str(root / "lark-cli.exe"),
                    "--approved-executable-sha256",
                    "0" * 64,
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
            self.assertEqual(completed.returncode, 2)
            self.assertFalse(state.exists())

    def test_relative_config_parent_is_rejected_before_directory_creation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            state = root / "state.json"
            executable = root / ("lark-cli.exe" if os.name == "nt" else "lark-cli")
            executable.touch(mode=0o700)
            executable.chmod(0o700)
            digest = hashlib.sha256(executable.read_bytes()).hexdigest()
            completed = subprocess.run(
                [
                    sys.executable,
                    str(CONFIG_INIT_HELPER),
                    "--state-file",
                    str(state),
                    "--config-parent",
                    "relative-profile-parent",
                    "--brand",
                    "feishu",
                    "--lark-cli",
                    str(executable),
                    "--approved-executable-sha256",
                    digest,
                    "--consent-confirmed",
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
            self.assertEqual(completed.returncode, 3)
            self.assertEqual(
                json.loads(completed.stdout)["reason"],
                "config_parent_invalid",
            )
            self.assertFalse(state.exists())
            self.assertFalse(
                (REPOSITORY_ROOT / "relative-profile-parent").exists()
            )

    def test_status_requires_and_checks_the_complete_binding(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            profile = "codex-paper-reading-" + "0" * 32
            config_dir = root / profile
            config_dir.mkdir(mode=0o700)
            data_dir = config_dir / "data"
            data_dir.mkdir(mode=0o700)
            state = root / "missing-state.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(CONFIG_INIT_HELPER),
                    "--status",
                    "--state-file",
                    str(state),
                    "--brand",
                    "feishu",
                    "--profile",
                    profile,
                    "--config-dir",
                    str(config_dir),
                    "--data-dir",
                    str(data_dir),
                    "--approved-executable-sha256",
                    "0" * 64,
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
            self.assertEqual(completed.returncode, 1)
            report = json.loads(completed.stdout)
            self.assertEqual(report["state"], "absent")
            self.assertEqual(report["reason"], "no_state_file")
            self.assertEqual(set(report), {"state", "reason", "updated_at"})

    def test_expired_live_process_stays_active_and_cleanup_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            profile = "codex-paper-reading-" + "1" * 32
            config_dir = root / profile
            config_dir.mkdir(mode=0o700)
            data_dir = config_dir / "data"
            data_dir.mkdir(mode=0o700)
            state_path = root / "state.json"
            config_identity = config_init._directory_identity(config_dir)
            data_identity = config_init._directory_identity(data_dir)
            self.assertIsNotNone(config_identity)
            self.assertIsNotNone(data_identity)
            now = time.time()
            binding = {
                "brand": "feishu",
                "profile": profile,
                "config_dir": os.fspath(config_dir),
                "config_dir_identity_sha256": (
                    config_init._directory_identity_sha256(config_identity)
                ),
                "data_dir": os.fspath(data_dir),
                "data_dir_identity_sha256": (
                    config_init._directory_identity_sha256(data_identity)
                ),
                "executable_sha256": "2" * 64,
            }
            active = {
                "state": "pending",
                "reason": "awaiting_user_verification",
                "pid": os.getpid(),
                "browser_opened": True,
                "started_at": config_init._utc_timestamp(now - 120),
                "updated_at": config_init._utc_timestamp(now - 60),
                "expires_at": config_init._utc_timestamp(now - 30),
                **binding,
            }
            config_init._write_initial_state(state_path, active)

            status_events: list[dict[str, object]] = []
            result = config_init.status(
                state_path,
                brand="feishu",
                profile=profile,
                config_dir=config_dir,
                data_dir=data_dir,
                approved_executable_sha256="2" * 64,
                emit=status_events.append,
            )
            self.assertEqual(result, 0)
            self.assertEqual(status_events[-1]["state"], "pending")
            self.assertEqual(
                json.loads(state_path.read_text(encoding="utf-8"))["state"],
                "pending",
            )

            terminal_with_live_pid = {
                "state": "expired",
                "reason": "configuration_expired",
                "pid": os.getpid(),
                "started_at": config_init._utc_timestamp(now - 120),
                "updated_at": config_init._utc_timestamp(now),
                "finished_at": config_init._utc_timestamp(now),
                **binding,
            }
            config_init._replace_state(state_path, terminal_with_live_pid)
            cleanup_events: list[dict[str, object]] = []
            result = config_init.cleanup(
                state_path,
                brand="feishu",
                profile=profile,
                config_dir=config_dir,
                data_dir=data_dir,
                approved_executable_sha256="2" * 64,
                emit=cleanup_events.append,
            )
            self.assertEqual(result, 2)
            self.assertEqual(
                cleanup_events[-1]["reason"],
                "cleanup_refused_active_configuration",
            )
            self.assertTrue(state_path.exists())
            self.assertTrue(config_dir.is_dir())
            self.assertTrue(data_dir.is_dir())


if __name__ == "__main__":
    unittest.main()
