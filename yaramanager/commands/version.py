import click
from rich.console import Console

from yaramanager import version as ver


@click.command()
def version():
    c = Console()
    c.print(f"YaraManager v.{ver}", highlight=False)
    c.print(f"https://github.com/3c7/yaramanager/releases/tag/{ver}")
