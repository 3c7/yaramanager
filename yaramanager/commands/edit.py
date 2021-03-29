import os
import subprocess
from sys import stderr
from typing import Union

import click
from rich.console import Console
from yarabuilder import YaraBuilder

from yaramanager.db.session import get_session
from yaramanager.utils import (
    get_md5,
    write_ruleset_to_tmp_file,
    get_rule_by_identifier,
    read_rulefile,
    plyara_obj_to_rule
)


@click.command(help="Edits a rule with your default editor. "
                    "Identifier can be part of a rule name or the specific ID.")
@click.argument("identifier")
def edit(identifier: Union[int, str]):
    c, ec = Console(), Console(file=stderr, style="bold red")
    session = get_session()
    rule = get_rule_by_identifier(identifier, session)
    if len(rule) > 1:
        ec.print(f"Found more than one rule.")
        exit(-1)
    rule = rule[0]
    yb = YaraBuilder()
    rule.add_to_yarabuilder(yb)
    path, _ = write_ruleset_to_tmp_file(yb)
    hash = get_md5(path)
    with c.status(f"{rule.name} opened in external editor..."):
        subprocess.call(["codium", "-w", path])
        edit_hash = get_md5(path)

    if hash == edit_hash:
        c.print(f"No change detected...")
    else:
        c.print(f"Change detected, updating rule...")
        edited_rule = read_rulefile(path)
        if not 0 < len(edited_rule) < 2:
            ec.print("Edited rule file must contain exactly one yara rule.")
            exit(-1)
        edited_rule = plyara_obj_to_rule(edited_rule[0], session)
        rule.name = edited_rule.name
        rule.meta = edited_rule.meta
        rule.imports = edited_rule.imports
        rule.strings = edited_rule.strings
        rule.tags = edited_rule.tags
        session.add(rule)
        # Removes edited rule from session, otherwise a copy of the rule would be created
        session.delete(edited_rule)
        session.commit()
    os.remove(path)
