import io
import os

import click
import yara
from rich.console import Console
from yarabuilder import YaraBuilder
from pathlib import Path

from yaramanager.db.session import get_session
from yaramanager.utils.utils import filter_rules_by_name_and_tag, write_ruleset_to_tmp_file


@click.command(help="Export rules from the database. The set of rules can be filtered through commandline options. "
                    "Rules will be written in to separate files if -s not given.")
@click.option("-n", "--name", help="Rule name must include [NAME].")
@click.option("-t", "--tag", help="Rules must have [TAG] attached.")
@click.option("-s", "--single", is_flag=True, help="Write set of rules into a single yara file.")
@click.option("-c", "--compiled", is_flag=True, help="Write compiled ruleset into a single file.")
@click.argument("path", type=click.Path(dir_okay=True, file_okay=True, writable=True))
def export(name: str, tag: str, single: bool, compiled: bool, path: str):
    c, ec = Console(), Console(stderr=True, style="bold red")
    session = get_session()
    rules, count = filter_rules_by_name_and_tag(name, tag, session)
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

        if not (single or compiled):
            with io.open(os.path.join(path, rule.name + ".yar"), "w") as fh:
                fh.write(yb.build_rule(rule.name))

    if single:
        if path.suffix != ".yar":
            path = Path(str(path) + ".yar")
        with io.open(path, "w") as fh:
            fh.write(yb.build_rules())

    if compiled:
        if path.suffix == ".yar":
            path = Path(str(path)[:-4] + ".yac")
        elif path.suffix == "":
            path = Path(str(path) + ".yac")
        tmp_path, size = write_ruleset_to_tmp_file(yb)
        compiled: yara.Rules = yara.compile(tmp_path)
        compiled.save(str(path))

    c.print(f"Wrote {len(rules)} rules.")
