import click

from .add import add
from .config import config
from .delete import delete
from .edit import edit
from .init import init
from .list import list
from .parse import parse
from .stats import stats

@click.group()
def cli():
    pass


cli.add_command(add)
cli.add_command(config)
cli.add_command(delete)
cli.add_command(edit)
cli.add_command(init)
cli.add_command(list)
cli.add_command(parse)
cli.add_command(stats)
