import sys

import click
from rich.console import Console

from yaramanager.db.session import get_session
from yaramanager.utils.utils import parse_rule, plyara_obj_to_rule


@click.command(help="Read rules from stdin.")
def read():
    c = Console()
    session = get_session()
    stdin = ""
    for line in sys.stdin:
        stdin += line
    plyara_list = parse_rule(stdin)
    for plyara_obj in plyara_list:
        rule = plyara_obj_to_rule(plyara_obj, session)
        session.add(rule)
        c.print(f"Added rule {rule.name} from stdin.")
    session.commit()
