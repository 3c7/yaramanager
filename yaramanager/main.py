import io
import os
from argparse import ArgumentParser
from os.path import join as pjoin
from pprint import pprint
from typing import Dict, List, Union

import plyara
import yarabuilder
from rich.console import Console
from rich.table import Table

from yaramanager.db.base import Base, Rule, Meta, String
from yaramanager.db.session import get_session, get_engine
from yaramanager.utils import plyara_obj_to_rule


def parse_rule_file(path: str) -> Union[Dict, List]:
    ply = plyara.Plyara()
    with io.open(path) as fh:
        return ply.parse_string(fh.read())


def print_rule(rules: Union[Dict, List]) -> str:
    yb = yarabuilder.YaraBuilder()
    if isinstance(rules, dict):
        rules = [rules]
    for rule in rules:
        rn = rule["rule_name"]
        yb.create_rule(rn)
        for mdata in rule["metadata"]:
            for k, v in mdata.items():
                yb.add_meta(rn, k, v)
        for tag in rule["tags"]:
            yb.add_tag(rn, tag)
        for yara_string in rule["strings"]:
            s_type = yara_string["type"]
            s_name = yara_string["name"][1:]
            s_val = yara_string["value"]
            s_mod = yara_string.get("modifiers", [])
            if s_type == "text":
                yb.add_text_string(rn, s_val, s_name, s_mod)
            elif s_type == "regex":
                yb.add_regex_string(rn, s_val, s_name, s_mod)
            elif s_type == "byte":
                yb.add_hex_string(rn, s_val[1:-1].strip(), s_name)
        yb.add_condition(rn, " ".join(rule["condition_terms"]))
    return yb.build_rules()


def cli():
    parser = ArgumentParser()
    parser.add_argument("-d", "--database", type=str, help="Path to database. (Default ~/.yarman.db)",
                        default=pjoin(os.getenv("HOME"), ".yarman.db"))
    subparser = parser.add_subparsers(dest="command", help="Command to execute.")
    parse = subparser.add_parser("parse", help="Parse a yara rule")
    parse.add_argument("path", type=str, help="Path to yara rule file that should get parsed.")
    parse.add_argument("-r", "--raw", action="store_true", help="Print raw plyara output.")
    init = subparser.add_parser("init", help="Creates initial database")
    add = subparser.add_parser("add", help="Adds a new rule to the database")
    add.add_argument("path", type=str, help="Path to yara rule file.")
    list = subparser.add_parser("list", help="List rules in database")
    list.add_argument("-r", "--raw", action="store_true", help="Prints rules in yara format.")
    args = parser.parse_args()

    if args.command == "parse":
        if not args.raw:
            print(print_rule(parse_rule_file(args.path)))
        else:
            pprint(parse_rule_file(args.path))
    elif args.command == "init":
        engine = get_engine(args.database)
        Base.metadata.create_all(bind=engine)
    elif args.command == "add":
        obj = parse_rule_file(args.path)[0]
        rule = plyara_obj_to_rule(obj)
        session = get_session(args.database)
        q_rule = session.query(Rule).filter(Rule.name == rule.name).first()
        if not q_rule:
            session.add(rule)
            session.commit()
            print(f"Rule {rule.__repr__()} added to database.")
        else:
            print(f"Rule with name {rule.name} already in database.")
            exit(-1)
    elif args.command == "list":
        session = get_session(args.database)
        rules = session.query(Rule).all()
        if args.raw:
            for rule in rules:
                print(rule)
        else:
            c = Console()
            t = Table(show_header=True)
            t.add_column("Name")
            t.add_column("Created")
            t.add_column("Modified")
            t.add_column("Author")
            t.add_column("Num_Strings")
            for rule in rules:
                t.add_row(
                    rule.name,
                    rule.get_meta_value("date", "-"),
                    rule.get_meta_value("modified", "-"),
                    rule.get_meta_value("author", "-"),
                    str(len(rule.strings))
                )
            c.print(t)


if __name__ == "__main__":
    cli()
