from pathlib import Path
from typing import Tuple

import click
from rich.console import Console

from yaramanager.db.session import get_session
from yaramanager.models.yarabuilder import YaraBuilder
from yaramanager.utils.utils import filter_rules_by_name_and_tag


@click.command(help="Export rules from the database. The set of rules can be filtered through commandline options. "
                    "Rules will be written in to separate files if -s not given.")
@click.option("-n", "--name", help="Rule name must include [NAME].")
@click.option("--tag", "-t", multiple=True, help="Only export rules with given tag.")
@click.option("--exclude-tag", "-T", multiple=True, help="Exclude rules with given tag.")
@click.option("-s", "--single", is_flag=True, help="Write set of rules into a single yara file.")
@click.option("-c", "--compiled", is_flag=True, help="Write compiled ruleset into a single file.")
@click.argument("path", type=click.Path(dir_okay=True, file_okay=True, writable=True))
def export(name: str, tag: Tuple[str], exclude_tag: Tuple[str], single: bool, compiled: bool, path: str):
    c, ec = Console(), Console(stderr=True, style="bold red")
    session = get_session()
    rules, count = filter_rules_by_name_and_tag(name, tag, exclude_tag, session)
    path = Path(path)

    if count == 0:
        ec.print(f"Found no matching rules.")
        exit(-1)

    if single and path.is_dir():
        ec.print(f"Given path ({path}) is a directory.")
        exit(-1)

    yb = YaraBuilder()
    for rule in rules:
        rule.add_to_yarabuilder(yb)

    yb.write_rules_to_file(path, single_file=single, compiled=compiled)
    c.print(f"Wrote {len(rules)} rules.")
