import os

import click
from alembic import command
from alembic.config import Config
from rich.console import Console
from rich.prompt import Confirm

from yaramanager.config import load_config, change_db
from yaramanager.db.session import get_path
from yaramanager.utils.output import debug_print


@click.group(help="Manage your databases")
def db():
    pass


@db.command(help="Returns info about the selected database.")
def get():
    c = Console()
    config = load_config()
    c.print(f"Selected database: {config['db']['databases'][config['db']['selected']]['path']}", highlight=False)


@db.command(help="Changes database.")
@click.argument("db_num", type=int)
def set(db_num):
    c, ec = Console(), Console(stderr=True, style="bold red")
    config = load_config()
    if db_num > len(config["db"]["databases"]) - 1:
        ec.print("Number of DB to chose is higher than number of available databases.")
        exit(-1)
    change_db(db_num)


@db.command(help="Database initialization or schema upgrade.")
def upgrade():
    c = Console()
    db_path = get_path()
    base_path = os.path.abspath(os.path.join(__file__, "..", "..", ".."))
    script_path = os.path.join(base_path, "alembic")
    config_path = os.path.join(base_path, "alembic", "alembic.ini")
    debug_print(f"Accessing alembic files in {script_path} and {config_path}.", c)
    do_upgrade = Confirm.ask(f"Upgrade database {db_path}?")
    if do_upgrade:
        c.print(f"Using scripts in {script_path} to migrate...")
        a_cfg = Config(config_path)
        a_cfg.set_main_option("script_location", script_path)
        a_cfg.set_main_option("sqlalchemy.url", db_path)
        command.upgrade(a_cfg, "head")
