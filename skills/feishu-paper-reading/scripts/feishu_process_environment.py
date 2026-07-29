#!/usr/bin/env python3
"""Build a minimal environment for pinned Feishu/Lark CLI child processes."""

from __future__ import annotations

import os
from collections.abc import Mapping


SAFE_BASE_ENVIRONMENT_VARIABLES = frozenset(
    {
        "APPDATA",
        "COMSPEC",
        "DBUS_SESSION_BUS_ADDRESS",
        "DISPLAY",
        "GNOME_KEYRING_CONTROL",
        "HOME",
        "HOMEDRIVE",
        "HOMEPATH",
        "LANG",
        "LC_ALL",
        "LOCALAPPDATA",
        "PATH",
        "PATHEXT",
        "SYSTEMROOT",
        "TEMP",
        "TMP",
        "TMPDIR",
        "USERPROFILE",
        "WAYLAND_DISPLAY",
        "WINDIR",
        "XDG_RUNTIME_DIR",
    }
)


def build_isolated_cli_environment(
    *,
    config_dir: str | None = None,
    data_dir: str | None = None,
    base_environment: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Retain only OS/runtime essentials and explicitly selected CLI stores."""

    source = os.environ if base_environment is None else base_environment
    environment = {
        key: value
        for key, value in source.items()
        if isinstance(key, str)
        and isinstance(value, str)
        and key.upper() in SAFE_BASE_ENVIRONMENT_VARIABLES
    }
    if config_dir is not None:
        environment["LARKSUITE_CLI_CONFIG_DIR"] = config_dir
    if data_dir is not None:
        if config_dir is None:
            raise ValueError("data_dir requires config_dir")
        environment["LARKSUITE_CLI_DATA_DIR"] = data_dir
    return environment
