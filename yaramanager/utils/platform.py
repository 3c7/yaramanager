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
    if is_linux():
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
    c_path = os.path.join(get_user_path(), "config.toml")
    return c_path
