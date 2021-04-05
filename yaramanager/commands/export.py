import io
import os

import click
from rich.console import Console
from yarabuilder import YaraBuilder

from yaramanager.db.session import get_session
from yaramanager.utils.utils import filter_rules_by_name_and_tag


@click.command(help="Export rules from the database. The set of rules can be filtered through commandline options. "
                    "Rules will be written in to separate files if -s not given.")
@click.option("-n", "--name", help="Rule name must include [NAME].")
@click.option("-t", "--tag", help="Rules must have [TAG] attached.")
@click.option("-s", "--single", is_flag=True, help="Write set of rules into a single yara file.")
@click.argument("path", type=click.Path(dir_okay=True, file_okay=True, writable=True))
def export(name: str, tag: str, single: bool, path: str):
    c, ec = Console(), Console(stderr=True, style="bold red")
    session = get_session()
    rules, count = filter_rules_by_name_and_tag(name, tag, session)

    if count == 0:
        ec.print(f"Found no matching rules.")
        exit(-1)

    if single and os.path.isdir(path):
        ec.print(f"Given path ({path}) is a directory.")
        exit(-1)

    yb = YaraBuilder()
    for rule in rules:
        rule.add_to_yarabuilder(yb)

        if not single:
            with io.open(os.path.join(path, rule.name + ".yar"), "w") as fh:
                fh.write(yb.build_rule(rule.name))

    if single:
        with io.open(path, "w") as fh:
            fh.write(yb.build_rules())

    c.print(f"Wrote {len(rules)} rules.")
