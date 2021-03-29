import click
from rich.console import Console
from rich.syntax import Syntax
from yarabuilder import YaraBuilder

from yaramanager.db.base import Rule, Tag
from yaramanager.db.session import get_session
from yaramanager.utils import rules_to_table


@click.command(help="Lists rules available in DB. Default output is in a table, but raw output can be enabled.")
@click.option("--tag", "-t", help="Only display rules with given tag.")
@click.option("--raw", "-r", is_flag=True, help="Print rules to stdout.")
@click.option("--name", "-n", help="Only display rules containing [NAME].")
def list(tag: str, raw: bool, name: str):
    c, ec = Console(), Console(stderr=True, style="bold yellow")
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
                if rule.name in yb.yara_rules.keys():
                    ec.print(f"Rule name {rule.name} is duplicate. Skipping...")
                    continue
                rule.add_to_yarabuilder(yb)
            syntax = Syntax(yb.build_rules(), "python", background_color="default")
            c.print(syntax)
        else:
            c.print(rules_to_table(rules))
