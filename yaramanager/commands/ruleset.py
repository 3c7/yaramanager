import click
from rich.console import Console
from rich.table import Table
from yarabuilder import YaraBuilder
from yaramanager.db.base import Ruleset
from yaramanager.db.session import get_session
from yaramanager.utils.utils import get_ruleset_by_identifier, rules_to_table


@click.group(help="Manage your rulesets")
def ruleset():
    pass


@ruleset.command("list", help="Print a list of your rulests.")
def ruleset_list():
    c = Console()
    session = get_session()
    rulesets = session.query(Ruleset).all()
    if len(rulesets) == 0:
        c.print("No rulesets found.")
        exit(-1)

    t = Table()
    t.add_column("ID")
    t.add_column("Name")
    t.add_column("Number of rules")
    for ruleset in rulesets:
        t.add_row(
            str(ruleset.id),
            ruleset.name,
            str(len(ruleset.rules))
        )
    c.print(t)


@ruleset.command(help="Get all rules assigned to a ruleset.")
@click.option("-r", "--raw", is_flag=True, help="Print rules to stdout")
@click.argument("identifier")
def get(raw: bool, identifier: str):
    c = Console()
    session = get_session()
    ruleset = get_ruleset_by_identifier(identifier, session)
    if not ruleset:
        c.print("Ruleset not found.")
        exit(-1)

    if not raw:
        c.print(rules_to_table(ruleset.rules))
    else:
        yb = YaraBuilder()
        for rule in ruleset.rules:
            rule.add_to_yarabuilder(yb)
        c.print(yb.build_rules())

@ruleset.command(help="Create a new ruleset.")
@click.argument("name")
def create(name: str):
    c, ec = Console(), Console(stderr=True, style="bold red")
    session = get_session()
    ruleset = session.query(Ruleset).filter(Ruleset.name == name).first()
    if ruleset:
        ec.print("Ruleset with that name already exists.")
        exit(-1)

    ruleset = Ruleset(
        name=name
    )
    session.add(ruleset)
    session.commit()
    c.print("New ruleset added.")
