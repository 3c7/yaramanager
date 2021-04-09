import click
from yaramanager.db.session import get_session
from yaramanager.utils.utils import open_temp_file_with_template, read_rulefile, plyara_obj_to_rule
from rich.console import Console
from os import remove

@click.command(help="Create a new rule using you preferred editor.")
def new():
    c = Console()
    session = get_session()
    path = open_temp_file_with_template()
    plyara_list = read_rulefile(path)
    for plyara_object in plyara_list:
        rule = plyara_obj_to_rule(plyara_object, session)
        session.add(rule)
        c.print(f"Rule {rule.name} added to database.")
    session.commit()
    remove(path)
