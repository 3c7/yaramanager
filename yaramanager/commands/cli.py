from typing import List

import click
from rich.console import Console

from .add import add
from .config import config
from .db import db
from .delete import delete
from .edit import edit
from .export import export
from .get import get
from .list import list
from .new import new
from .parse import parse
from .read import read
from .ruleset import ruleset
from .scan import scan
from .search import search
from .stats import stats
from .tags import tags
from .version import version


@click.group(
    help="ym - yaramanager. Use the commands shown below to manage your yara ruleset. By default, the manager "
         "uses codium as editor. You can change that in the config file or using EDITOR environment variable. "
         "When using editors in the console, you might want to disable the status display using DISABLE_STATUS. You can "
         "overwrite the general ym path with YM_PATH and the config path with YM_CONFIG."
)
def cli():
    pass


cli.add_command(add)
cli.add_command(config)
cli.add_command(db)
cli.add_command(delete)
cli.add_command(edit)
cli.add_command(export)
cli.add_command(get)
cli.add_command(list)
cli.add_command(new)
cli.add_command(parse)
cli.add_command(read)
cli.add_command(ruleset)
cli.add_command(scan)
cli.add_command(search)
cli.add_command(stats)
cli.add_command(tags)
cli.add_command(version)


@cli.command(help="Displays help about commands")
@click.argument("cmds", nargs=-1)
def help(cmds: List[str]):
    c, ec = Console(), Console(stderr=True, style="bold red")
    ctx = click.get_current_context()
    if not cmds or len(cmds) == 0:
        print(cli.get_help(ctx))
    command = cli
    for cmd in cmds:
        if not isinstance(command, click.Group):
            ec.print("Command not found.")
            exit(-1)
        command = command.commands.get(cmd, None)
        if not command:
            ec.print("Command not found.")
            exit(-1)
    with click.Context(command) as ctx:
        c.print(ctx.get_help())
