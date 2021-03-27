import click

from yaramanager.db.base import Base
from yaramanager.db.session import get_engine


@click.command(help="Creates the database. Currently does not allow migrations to newer DB schemas. "
                    "Future versions will support alembic migrations.")
def init():
    click.echo("Initializing database...")
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
