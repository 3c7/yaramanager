import click
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table
from yarabuilder import YaraBuilder

from yaramanager.db.base import Rule, Tag
from yaramanager.db.session import get_session


@click.command(help="Lists rules available in DB. Default output is in a table, but raw output can be enabled.")
@click.option("--tag", "-t", help="Only display rules with given tag.")
@click.option("--raw", "-r", is_flag=True, help="Print rules to stdout.")
@click.option("--name", "-n", help="Only display rules containing [NAME].")
def list(tag: str, raw: bool, name: str):
    c = Console()
    session = get_session()
    rules = session.query(Rule)
    if tag and len(tag) > 0:
        rules = rules.select_from(Tag).join(Rule.tags).filter(Tag.name == tag)
    if name and len(name) > 0:
        rules = rules.filter(Rule.name.like(f"%{name}%"))
    count = rules.count()

    if count == 0:
        c.print(f"Query returned empty list of rules.")
    else:
        c.print(f"Loading {count} rules...")
        rules = rules.all()

        if raw:
            yb = YaraBuilder()
            for rule in rules:
                rule.add_to_yarabuilder(yb)
            syntax = Syntax(yb.build_rules(), "python", background_color="default")
            c.print(syntax)
        else:
            t = Table()
            t.add_column("ID")
            t.add_column("Name")
            t.add_column("Tags")
            t.add_column("Author")
            t.add_column("TLP")
            t.add_column("Created")
            t.add_column("Modified")
            for rule in rules:
                t.add_row(
                    str(rule.id),
                    rule.name,
                    ", ".join([tag.name for tag in rule.tags]),
                    rule.get_meta_value("author", "None"),
                    rule.get_meta_value("tlp", "None"),
                    rule.get_meta_value("date", "None"),
                    rule.get_meta_value("modified", "None")
                )
            c.print(t)
