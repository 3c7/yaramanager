import click
from rich.console import Console
import os
from yaramanager.db.base import Rule, String, Meta, Tag
from yaramanager.db.session import get_session
from yaramanager.config import load_config


@click.command(help="Prints stats about the database contents.")
def stats():
    c = Console()
    config = load_config()
    db = config.get_current_db()
    session = get_session()
    rule_count = session.query(Rule).count()
    string_count = session.query(String).count()
    meta_count = session.query(Meta).count()
    tag_count = session.query(Tag).count()
    c.print(f"Number of rules:\t{rule_count}")
    c.print(f"Number of strings:\t{string_count}")
    c.print(f"Number of meta fields:\t{meta_count}")
    c.print(f"Number of tags:\t\t{tag_count}")
    c.print()

    if db["driver"] == "sqlite":
        c.print(f"Database size: \t\t{os.path.getsize(db['path'])/1024/1024:.2}MB")
