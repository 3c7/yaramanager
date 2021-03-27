import os
import re
from typing import Union

import click
from rich.prompt import Confirm

from yaramanager.db.base import Rule
from yaramanager.db.session import get_session


@click.command("del", help="Delete a rule by its ID or name. Can delete multiple rules using the name.")
@click.argument("identifier")
def delete(identifier: Union[int, str]):
    session = get_session()
    rule = session.query(Rule)
    if isinstance(identifier, int) or re.fullmatch(r"^\d+$", identifier):
        rule = rule.filter(Rule.id == int(identifier))
    else:
        rule = rule.filter(Rule.name.like(f"%{identifier}%"))
    rule = rule.all()
    rule_names = ", ".join([r.name for r in rule])
    confirmed = Confirm.ask(f"Do you really want to delete the following rules: {rule_names}")
    if confirmed:
        for r in rule:
            session.delete(r)
        session.commit()
