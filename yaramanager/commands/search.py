import click
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table
from yarabuilder import YaraBuilder

from yaramanager.db.base import String
from yaramanager.db.session import get_session


@click.group(help="Searches through your rules.")
def search():
    pass


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
