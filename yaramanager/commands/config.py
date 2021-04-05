import io

import click
from rich.console import Console
from rich.prompt import Confirm
from rich.syntax import Syntax

from yaramanager.config import load_config, config_file, write_initial_config
from yaramanager.utils.utils import open_file

CONFIG = load_config()


@click.group(help="Review and change yaramanager configuration.")
def config():
    pass


@config.command(help="Get single config entry by key.")
@click.argument("key")
def get(key):
    c, ec = Console(), Console(stderr=True, style="bold red")
    if key in CONFIG.keys():
        c.print(CONFIG[key])
    else:
        ec.print("Config key not found")


@config.command(help=f"Edit your config with an external editor. The config file can be found here: {config_file}. "
                     f"If you don't use codium as default editor, you need to change the according key in the config "
                     f"or use the environment variable EDITOR.")
def edit():
    open_file(config_file, status="Config file opened in external editor...")


@config.command(help="Prints the current config to stdout.")
def dump():
    c = Console()
    with io.open(config_file) as fh:
        syntax = Syntax(fh.read(), "toml", background_color="default")
        c.print(syntax)


@config.command(help="Resets the configuration.")
def reset():
    confirm = Confirm.ask("Do you really want to reset the config?")
    if confirm:
        write_initial_config()
