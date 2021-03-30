import click
from rich.console import Console
from rich.syntax import Syntax
from yarabuilder import YaraBuilder

from yaramanager.db.base import Rule, Tag
from yaramanager.db.session import get_session
from yaramanager.utils import rules_to_table, filter_rules_by_name_and_tag


@click.command(help="Lists rules available in DB. Default output is in a table, but raw output can be enabled.")
@click.option("--tag", "-t", help="Only display rules with given tag.")
@click.option("--raw", "-r", is_flag=True, help="Print rules to stdout.")
@click.option("--name", "-n", help="Only display rules containing [NAME].")
def list(tag: str, raw: bool, name: str):
    c, ec = Console(), Console(stderr=True, style="bold yellow")
    session = get_session()
    rules, count = filter_rules_by_name_and_tag(name, tag, session)

    if count == 0:
        c.print(f"Query returned empty list of rules.")
    else:
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
