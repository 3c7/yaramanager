import os.path

import click

from yaramanager.db.base import Base
from yaramanager.db.session import create_engine


@click.command()
@click.option("--database", "-d", default=os.path.join(os.getenv("HOME"), ".config", "yarman", "database.db"),
              help="Path to database (default ~/.config/yarman/database.db).")
def init(database: str):
    click.echo("Initializing database...")
    engine = create_engine(f"sqlite:///{database}")
    Base.metadata.create_all(bind=engine)
