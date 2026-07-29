from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIRECTORY = (
    REPOSITORY_ROOT / "skills" / "feishu-paper-reading" / "scripts"
)
sys.path.insert(0, str(SCRIPTS_DIRECTORY))
from feishu_process_environment import build_isolated_cli_environment  # noqa: E402


class FeishuProcessEnvironmentTests(unittest.TestCase):
    def test_only_allowlisted_runtime_and_explicit_cli_stores_survive(self) -> None:
        environment = build_isolated_cli_environment(
            config_dir="C:\\approved-config",
            data_dir="C:\\approved-config\\data",
            base_environment={
                "PATH": "approved-runtime",
                "HTTPS_PROXY": "https://ambient-proxy.example",
                "SSL_CERT_FILE": "C:\\ambient-ca.pem",
                "LARKSUITE_CLI_PROFILE": "ambient-profile",
                "LARKSUITE_CLI_PROXY_ENABLE": "true",
                "LARKSUITE_CLI_PROXY_ADDRESS": "https://127.0.0.1:9443",
                "LARKSUITE_CLI_CA_PATH": "C:\\ambient-ca.pem",
                "LARKSUITE_CLI_APP_SECRET": "must-not-survive",
                "OPENCLAW_CLI": "must-not-survive",
                "OPENCLAW_STATE_DIR": "must-not-survive",
                "HERMES_SESSION_KEY": "must-not-survive",
                "LARK_CHANNEL": "must-not-survive",
                "UNRELATED_SECRET": "must-not-survive",
            },
        )
        self.assertEqual(
            environment,
            {
                "PATH": "approved-runtime",
                "LARKSUITE_CLI_CONFIG_DIR": "C:\\approved-config",
                "LARKSUITE_CLI_DATA_DIR": "C:\\approved-config\\data",
            },
        )

    def test_data_store_cannot_be_selected_without_config_store(self) -> None:
        with self.assertRaises(ValueError):
            build_isolated_cli_environment(
                data_dir="C:\\unbound-data",
                base_environment={},
            )


if __name__ == "__main__":
    unittest.main()
