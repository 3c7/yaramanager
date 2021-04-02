from pprint import pprint

import click

from yaramanager.utils.utils import print_rule, parse_rule_file


@click.command(help="Parses rule files. This is mainly used for development and debugging purposes.", deprecated=True)
@click.option("--raw", "-r", is_flag=True, help="Print plyara output instead of yara.")
@click.argument("path")
def parse(raw: bool, path: str):
    if not raw:
        print(print_rule(parse_rule_file(path)))
    else:
        pprint(parse_rule_file(path))
