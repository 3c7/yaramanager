import os
from sys import platform

from rich.console import Console


def is_linux() -> bool:
    return platform == "linux"


def is_win() -> bool:
    return platform == "win32"


def is_darwin() -> bool:
    return platform == "darwin"


def get_user_path() -> str:
    """Returns yaramanager path in user dir."""
    u_path = None
    u_env = os.getenv("YM_PATH", None)
    if u_env:
        return u_env
    if is_linux() or is_darwin():
        u_path = os.path.abspath(os.path.join(os.getenv("HOME"), ".config", "yaramanager"))
    elif is_win():
        u_path = os.path.abspath(os.path.join(os.getenv("APPDATA"), "yaramanager"))
    else:
        c = Console(stderr=True, style="bold red")
        c.print(f"Unknown platform: {platform}.")
        exit(-1)

    if not os.path.exists(u_path):
        os.mkdir(u_path)

    return u_path


def get_config_path() -> str:
    """Return path to config.toml"""
    c_env = os.getenv("YM_CONFIG", None)
    if c_env:
        return c_env
    c_path = os.path.join(get_user_path(), "config.toml")
    return c_path
