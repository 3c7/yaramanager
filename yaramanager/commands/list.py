import click
from rich.console import Console
from sys import exit
from yaramanager.db.session import get_session
from yaramanager.utils.utils import (
    rules_to_table,
    filter_rules_by_name_and_tag,
    rules_to_highlighted_string,
    get_ruleset_by_identifier
)


@click.command(help="Lists rules available in DB. Default output is in a table, but raw output can be enabled.")
@click.option("--tag", "-t", help="Only display rules with given tag.")
@click.option("--raw", "-r", is_flag=True, help="Print rules to stdout.")
@click.option("--name", "-n", help="Only display rules containing [NAME].")
@click.option("--ensure", "-e", is_flag=True, help="Ensure meta fields and tags.")
@click.option("--assign", "-a", help="Assign listed rules to ruleset. This has to be either a legitimate Ruleset id or "
                                     "a Ruleset name.")
def list(tag: str, raw: bool, name: str, ensure: bool, assign: str):
    c, ec = Console(), Console(stderr=True, style="bold yellow")
    session = get_session()
    rules, count = filter_rules_by_name_and_tag(name, tag, session)

    if count == 0:
        c.print(f"Query returned empty list of rules.")
        exit(-1)

    if assign and len(assign) > 0:
        ruleset = get_ruleset_by_identifier(assign, session)
        if not ruleset:
            ec.print("Ruleset not found.")
            exit(-1)

        for rule in rules:
            rule.ruleset = ruleset
        session.commit()
    if raw:
        c.print(rules_to_highlighted_string(rules))
    else:
        c.print(rules_to_table(rules, ensure=ensure))
