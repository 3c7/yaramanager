import click
from rich.console import Console

from yaramanager.db.session import get_session
from yaramanager.utils import rules_to_table, filter_rules_by_name_and_tag, rules_to_highlighted_string


@click.command(help="Lists rules available in DB. Default output is in a table, but raw output can be enabled.")
@click.option("--tag", "-t", help="Only display rules with given tag.")
@click.option("--raw", "-r", is_flag=True, help="Print rules to stdout.")
@click.option("--name", "-n", help="Only display rules containing [NAME].")
@click.option("--ensure", "-e", is_flag=True, help="Ensure meta fields and tags.")
def list(tag: str, raw: bool, name: str, ensure: bool):
    c, ec = Console(), Console(stderr=True, style="bold yellow")
    session = get_session()
    rules, count = filter_rules_by_name_and_tag(name, tag, session)

    if count == 0:
        c.print(f"Query returned empty list of rules.")
    else:
        if raw:
            c.print(rules_to_highlighted_string(rules))
        else:
            c.print(rules_to_table(rules, ensure=ensure))
