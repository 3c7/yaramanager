import os.path

import click

from yaramanager.db.session import get_session
from yaramanager.utils import parse_rule_file, plyara_obj_to_rule


@click.command(help="Add a new rule to the database.")
@click.option("--database", "-d", default=os.path.join(os.getenv("HOME"), ".config", "yarman", "database.db"),
              help="Path to database (default ~/.config/yarman/database.db).")
@click.argument("path")
def add(database: str, path: str):
    session = get_session(database)
    plyara_list = parse_rule_file(path)
    for plyara_obj in plyara_list:
        r = plyara_obj_to_rule(plyara_obj, session)
        session.add(r)
        click.echo(f"Added {r.__repr__()} to database.")
    session.commit()
