import click
from rich.console import Console
from rich.table import Table

from yaramanager.db.base import Tag
from yaramanager.db.session import get_session


@click.command(help="Show tags and the number of tagged rules")
@click.option("-r", "--reverse", is_flag=True, help="Reverse the order.")
@click.option("-l", "--limit", type=int, help="Limit amount of rows.")
def tags(reverse, limit):
    c, ec = Console(), Console(stderr=True, style="bold red")
    session = get_session()
    tags = session.query(Tag).all()
    if len(tags) == 0:
        ec.print("No tags available.")
        exit(-1)

    sorted_tags = []
    for tag in tags:
        sorted_tags.append((tag.name, len(tag.rules)))

    sorted_tags.sort(key=lambda x: x[1], reverse=(not reverse))
    table = Table()
    table.add_column("Tag")
    table.add_column("Rule count")
    for tag in sorted_tags[:limit]:
        table.add_row(tag[0], str(tag[1]))
    c.print(table)
