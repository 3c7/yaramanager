import io

import click
from rich.console import Console
from yarabuilder import YaraBuilder

from yaramanager.utils.utils import get_rule_by_identifier


@click.command(help="Get rules from the database.")
@click.argument("identifier")
@click.option("-o", "--output", help="Write output to file.")
def get(identifier, output):
    c = Console()
    rules = get_rule_by_identifier(identifier)
    if len(rules) == 0:
        c.print("Query returned empty list of Rules.")
        exit(-1)

    yb = YaraBuilder()
    _ = [rule.add_to_yarabuilder(yb) for rule in rules]

    if output and len(output) > 0:
        with io.open(output, "w") as fh:
            fh.write(yb.build_rules())
            exit(0)

    # Simple print because rich.Console adjusts to terminal size and might cut something or mess with the format for
    # readability
    print(yb.build_rules())
