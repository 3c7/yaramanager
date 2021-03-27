from pprint import pprint

import click

from yaramanager.utils import print_rule, parse_rule_file


@click.command()
@click.option("--raw", "-r", is_flag=True, help="Print rules to stdout instead in a formatted list.")
@click.argument("path")
def parse(raw: bool, path: str):
    if not raw:
        print(print_rule(parse_rule_file(path)))
    else:
        pprint(parse_rule_file(path))
