import os.path

import click
from typing import List
from yaramanager.db.session import get_session
from yaramanager.utils import parse_rule_file, plyara_obj_to_rule


@click.command(help="Add a new rule to the database.")
@click.option("--database", "-d", default=os.path.join(os.getenv("HOME"), ".config", "yarman", "database.db"),
              help="Path to database (default ~/.config/yarman/database.db).")
@click.argument("paths", type=click.Path(exists=True, dir_okay=False), nargs=-1)
def add(database: str, paths: List[str]):
    session = get_session(database)
    for rule_path in paths:
        plyara_list = parse_rule_file(rule_path)
        for plyara_obj in plyara_list:
            r = plyara_obj_to_rule(plyara_obj, session)
            session.add(r)
            click.echo(f"Added {r.__repr__()} to database.")
    session.commit()
