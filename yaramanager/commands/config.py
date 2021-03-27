import io
import click
from rich.console import Console
from rich.syntax import Syntax
from rich.prompt import Confirm

from yaramanager.config import load_config, config_file, init_config, write_config
from yaramanager.utils import open_file

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


@config.command(help="Edit your config with an external editor.")
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
        write_config(init_config)
