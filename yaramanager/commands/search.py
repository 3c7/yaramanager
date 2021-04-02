import click
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table
from sqlalchemy.sql import and_, or_
from yarabuilder import YaraBuilder

from yaramanager.db.base import Meta, Rule, String
from yaramanager.db.session import get_session
from yaramanager.utils.utils import rules_to_table, rules_to_highlighted_string


@click.group(help="Searches through your rules.")
def search():
    pass


@search.command(help="Wilcard search in rule names and descriptions.")
@click.option("-r", "--raw", is_flag=True, help="Output rules instead of the string table.")
@click.argument("search_term")
def rule(raw: bool, search_term: str):
    c = Console()
    session = get_session()
    rules = session.query(Rule).select_from(Meta).join(Rule.meta).filter(
        or_(
            Rule.name.like(f"%{search_term}%"),
            and_(
                Meta.key.like("description"),
                Meta.value.like(f"%{search_term}%")
            )
        )
    ).all()
    if not raw:
        table = rules_to_table(rules)
        c.print(table)
    else:
        c.print(rules_to_highlighted_string(rules))


@search.command(help="Search for strings. You can use SQL wildcard syntax (%).")
@click.option("-r", "--raw", is_flag=True, help="Output rules instead of the string table.")
@click.argument("query_string")
def string(raw, query_string):
    c = Console()
    session = get_session()
    strings = session.query(String).filter(String.type == "text").filter(String.value.like(query_string)).all()
    if not raw:
        c.print(f"Found {len(strings)} strings.")
        t = Table()
        t.add_column("String")
        t.add_column("ID")
        t.add_column("Rule")
        t.add_column("Tags")
        for string in strings:
            t.add_row(
                string.value,
                str(string.rule.id),
                string.rule.name,
                ", ".join([tag.name for tag in string.rule.tags])
            )
        c.print(t)
    else:
        yb = YaraBuilder()
        for string in strings:
            if string.rule.name not in yb.yara_rules.keys():
                string.rule.add_to_yarabuilder(yb)
        syntax = Syntax(yb.build_rules(), "python", background_color="default")
        c.print(syntax)
