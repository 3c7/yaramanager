import os
from sys import stderr
from typing import Union

import click
from rich.console import Console
from yarabuilder import YaraBuilder

from yaramanager.db.session import get_session
from yaramanager.utils.utils import (
    get_md5,
    write_ruleset_to_tmp_file,
    get_rule_by_identifier,
    read_rulefile,
    plyara_object_to_meta,
    plyara_object_to_strings,
    plyara_object_to_condition,
    plyara_object_to_imports,
    plyara_object_to_tags,
    open_file,
    plyara_object_to_ruleset
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
    open_file(path, f"{rule.name} opened in external editor...")
    edit_hash = get_md5(path)

    if hash == edit_hash:
        c.print(f"No change detected...")
    else:
        c.print(f"Change detected, updating rule...")
        edited_rule = read_rulefile(path)
        if not 0 < len(edited_rule) < 2:
            ec.print("Edited rule file must contain exactly one yara rule.")
            exit(-1)
        rule.name = edited_rule[0].get("rule_name", "Unnamed rule")
        rule.meta = plyara_object_to_meta(edited_rule[0])
        rule.imports = plyara_object_to_imports(edited_rule[0])
        rule.strings = plyara_object_to_strings(edited_rule[0])
        rule.tags = plyara_object_to_tags(edited_rule[0], session)
        rule.condition = plyara_object_to_condition(edited_rule[0])
        rule.ruleset = plyara_object_to_ruleset(edited_rule[0], session)
        session.commit()
    os.remove(path)
