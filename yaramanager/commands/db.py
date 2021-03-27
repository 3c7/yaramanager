import click
from rich.console import Console

from yaramanager.config import load_config, write_config
from yaramanager.db.base import Base
from yaramanager.db.session import get_engine


@click.group(help="Manage your databases")
def db():
    pass


@db.command(help="Creates the database. Currently does not allow migrations to newer DB schemas. "
                 "Future versions will support alembic migrations.")
def init():
    click.echo("Initializing database...")
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


@db.command(help="Returns info about the selected database.")
def get():
    c = Console()
    config = load_config()
    c.print(f"Selected database: {config['databases'][config['db']]['path']}", highlight=False)


@db.command(help="Changes database.")
@click.argument("db_num", type=int)
def set(db_num):
    c, ec = Console(), Console(stderr=True, style="bold red")
    config = load_config()
    if db_num > len(config["databases"]) -1:
        ec.print("Number of DB to chose is higher than number of available databases.")
        exit(-1)
    config["db"] = db_num
    write_config(config)
