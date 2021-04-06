import io
import os
import re
import sys
from collections import OrderedDict
from typing import Dict

import toml
from rich.console import Console

from yaramanager.utils.platform import get_user_path, get_config_path

config_dir = get_user_path()
config_file = get_config_path()


class Config(OrderedDict):
    instance = None

    @staticmethod
    def get_instance():
        if not Config.instance:
            Config.instance = Config()
        return Config.instance

    def get_current_db(self) -> Dict:
        return self["db"]["databases"][self["db"]["selected"]]

    def __init__(self):
        ec = Console(stderr=True, style="bold yellow")
        if not os.path.exists(config_dir):
            os.mkdir(config_dir)

        if not os.path.isdir(config_dir):
            ec.print(f"Error: File found as config directory path.")

        if not os.path.exists(config_file):
            ec.print(f"Creating initial config file.")
            write_initial_config()

        if os.path.getsize(config_file) == 0:
            ec.print(f"Config file ({config_file}) is empty. Applying initial config.")
            write_initial_config()

        with io.open(config_file, "r") as fh:
            config_data = toml.loads(fh.read())["yaramanager"]
        super().__init__(self, **config_data)


def load_config() -> Config:
    return Config.get_instance()


def create_initial_config() -> str:
    """Reads initial config from resources directory."""
    config_toml = ""
    db_path = os.path.join(config_dir, 'data.db')
    if sys.platform == "win32":
        db_path = db_path.replace("\\", "\\\\")
    with io.open(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "resources", "config.toml"))) as fh:
        for line in fh.readlines():
            config_toml += line.replace("# {init_database}", (
                f"[[yaramanager.db.databases]]\ndriver = \"sqlite\"\n"
                f"path = \"{db_path}\""
            ))
    return config_toml


def write_initial_config() -> None:
    """Writes fresh config to config file"""
    config_toml = create_initial_config()
    with io.open(config_file, "w") as fh:
        fh.write(config_toml)


def change_db(db_num: int) -> None:
    """Changes selected db through regex replace."""
    with io.open(config_file) as fh:
        data = fh.read()
    data = re.sub(r"selected = [0-9]+", f"selected = {db_num}", data)
    with io.open(config_file, "w") as fh:
        fh.write(data)
