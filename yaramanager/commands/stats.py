import click
from rich.console import Console

from yaramanager.db.base import Rule, String, Meta, Tag
from yaramanager.db.session import get_session


@click.command()
def stats():
    c = Console()
    session = get_session()
    rule_count = session.query(Rule).count()
    string_count = session.query(String).count()
    meta_count = session.query(Meta).count()
    tag_count = session.query(Tag).count()
    c.print(f"Number of rules:\t{rule_count}")
    c.print(f"Number of strings:\t{string_count}")
    c.print(f"Number of meta fields:\t{meta_count}")
    c.print(f"Number of tags:\t\t{tag_count}")
