import os
import re
from sys import stderr
from tempfile import mkstemp
from typing import Union

import click
from rich.console import Console
from yarabuilder import YaraBuilder

from yaramanager.db.base import Rule
from yaramanager.db.session import get_session
from yaramanager.utils import get_md5
import subprocess

@click.command(help="Edit a rule. You can replace the editor to use via EDITOR evironment variable, "
                    "default is \"codium\".")
@click.option("--database", "-d", default=os.path.join(os.getenv("HOME"), ".config", "yarman", "database.db"),
              help="Path to database (default ~/.config/yarman/database.db).")
@click.argument("identifier")
def edit(database: str, identifier: Union[int, str]):
    c, ec = Console(), Console(file=stderr)
    session = get_session(database)
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
    fd_temp, path = mkstemp(suffix=".yar")
    with os.fdopen(fd_temp, "w") as fh:
        yb = YaraBuilder()
        rule.add_to_yarabuilder(yb)
        fh.write(yb.build_rules())
    hash = get_md5(path)
    with c.status(f"{rule.name} opened in external editor..."):
        subprocess.call(["codium",  "-w", path])
        edit_hash = get_md5(path)

    if hash == edit_hash:
        c.print(f"No change detected...")
    else:
        c.print(f"Change detected, updating rule...")
    os.remove(path)
