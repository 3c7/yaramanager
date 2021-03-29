import os

import click
from alembic import command
from alembic.config import Config
from rich.console import Console
from rich.prompt import Confirm

from yaramanager.config import load_config, write_config
from yaramanager.db.base import Base
from yaramanager.db.session import get_engine, get_path


@click.group(help="Manage your databases")
def db():
    pass


@db.command(help="Creates the database. Currently does not allow migrations to newer DB schemas. "
                 "Future versions will support alembic migrations.", deprecated=True)
def init():
    c = Console()
    c.print("Initializing database...")
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
    if db_num > len(config["databases"]) - 1:
        ec.print("Number of DB to chose is higher than number of available databases.")
        exit(-1)
    config["db"] = db_num
    write_config(config)


@db.command(help="Init or update the currently chosen database using alembic.")
def upgrade():
    c = Console()
    db_path = get_path()
    base_path = os.path.abspath(os.path.join(__file__, "..", "..", ".."))
    script_path = os.path.join(base_path, "alembic")
    config_path = os.path.join(base_path, "alembic.ini")
    do_upgrade = Confirm.ask(f"Upgrade database {db_path}?")
    if do_upgrade:
        c.print(f"Using scripts in {script_path} to migrate...")
        a_cfg = Config(config_path)
        a_cfg.set_main_option("script_location", script_path)
        a_cfg.set_main_option("sqlalchemy.url", db_path)
        command.upgrade(a_cfg, "head")
