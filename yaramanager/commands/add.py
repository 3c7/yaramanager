import os
from typing import List

import click
from rich.progress import Progress

from yaramanager.db.session import get_session
from yaramanager.utils import parse_rule_file, plyara_obj_to_rule


@click.command(help="Add a new rule to the database. Use - as path for reading from stdin.")
@click.argument("paths", type=click.Path(exists=True, dir_okay=False), nargs=-1)
def add(paths: List[str]):
    session = get_session()
    with Progress() as progress:
        t1 = progress.add_task("Processing rule files...", total=len(paths))
        for rule_path in paths:
            progress.console.print(f"Processing {os.path.basename(rule_path)}...")
            plyara_list = parse_rule_file(rule_path)
            for plyara_obj in plyara_list:
                r = plyara_obj_to_rule(plyara_obj, session)
                session.add(r)
            progress.update(t1, advance=1)
        session.commit()
