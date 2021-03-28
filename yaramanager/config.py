import io
import os
from collections import OrderedDict
from typing import Dict

import toml
from rich.console import Console

init_config = {
    "yaramanager": {
        "databases": [
            {
                "driver": "sqlite",
                "path": os.path.join(os.getenv("HOME"), ".config", "yaramanager", "data.db")
            },
            {
                "driver": "sqlite",
                "path": os.path.join(os.getenv("HOME"), ".config", "yaramanager", "data_alt.db")
            }
        ],
        "editor": ["codium", "-w"],
        "db": 0,
        "meta": {
            "Author": "author",
            "TLP": "tlp",
            "Created": "created",
            "Modified": "modified"
        }
    }
}
config_dir = os.path.join(os.getenv("HOME"), ".config", "yaramanager")
config_file = os.path.join(config_dir, "config.toml")


class Config(OrderedDict):
    instance = None

    @staticmethod
    def get_instance():
        if not Config.instance:
            Config.instance = Config()
        return Config.instance

    def get_current_db(self) -> Dict:
        return self["databases"][self["db"]]

    def __init__(self):
        ec = Console(stderr=True, style="bold yellow")
        if not os.path.exists(config_dir):
            os.mkdir(config_dir)

        if not os.path.isdir(config_dir):
            ec.print(f"Error: File found as config directory path.")

        if not os.path.exists(config_file):
            ec.print(f"Creating initial config file.")
            with io.open(config_file, "w") as fh:
                fh.write(toml.dumps(init_config))

        if os.path.getsize(config_file) == 0:
            ec.print(f"Config file ({config_file}) is empty. Applying initial config.")
            with io.open(config_file, "w") as fh:
                fh.write(toml.dumps(init_config))

        with io.open(config_file, "r") as fh:
            config_data = toml.loads(fh.read())["yaramanager"]
        super().__init__(self, **config_data)


def load_config() -> Config:
    return Config.get_instance()


def write_config(config: dict):
    if "yaramanager" not in config.keys():
        config = {"yaramanager": config}
    with io.open(config_file, "w") as fh:
        fh.write(toml.dumps(config))
