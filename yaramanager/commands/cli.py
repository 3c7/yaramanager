import click
from .add import add
from .delete import delete
from .edit import edit
from .init import init
from .list import list
from .parse import parse

@click.group()
def cli():
    pass

cli.add_command(add)
cli.add_command(delete)
cli.add_command(edit)
cli.add_command(init)
cli.add_command(list)
cli.add_command(parse)
