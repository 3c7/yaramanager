import os
import re
import subprocess
from sys import stderr
from typing import Union

import click
from rich.console import Console
from yarabuilder import YaraBuilder

from yaramanager.db.base import Rule
from yaramanager.db.session import get_session
from yaramanager.utils import get_md5, write_ruleset_to_tmp_file


@click.command(help="Edit a rule. The default editor is codium, this will be adjustable in a future version.")
@click.argument("identifier")
def edit(identifier: Union[int, str]):
    c, ec = Console(), Console(file=stderr)
    session = get_session()
    rule = session.query(Rule)
    if isinstance(identifier, int) or re.fullmatch(r"^\d+$", identifier):
        rule = rule.filter(Rule.id == int(identifier))
    else:
        rule = rule.filter(Rule.name.like(f"%{identifier}%"))
    rule = rule.all()
    if len(rule) > 1:
        ec.print(f"Found more than one rule.")
        exit(-1)
    rule = rule[0]
    yb = YaraBuilder()
    rule.add_to_yarabuilder(yb)
    path, num_bytes = write_ruleset_to_tmp_file(yb)
    hash = get_md5(path)
    with c.status(f"{rule.name} opened in external editor..."):
        subprocess.call(["codium", "-w", path])
        edit_hash = get_md5(path)

    if hash == edit_hash:
        c.print(f"No change detected...")
    else:
        c.print(f"Change detected, updating rule...")
    os.remove(path)
