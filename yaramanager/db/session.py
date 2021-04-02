import os

from rich.console import Console
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import text

from yaramanager.config import load_config
from yaramanager import alembic_version
from yaramanager.utils.output import debug_print


def get_session() -> Session:
    ec = Console(stderr=True, style="bold red")
    config = load_config()
    db = config.get_current_db()
    driver = db["driver"]
    path = db["path"]
    if driver == "sqlite" and not os.path.exists(path) or os.path.getsize(path) == 0:
        ec.print("Database not initialized.")
        exit(-1)
    engine = get_engine()
    s_maker = sessionmaker(autocommit=False, bind=engine)
    db_alembic_version = get_alembic_version(s_maker())
    if db_alembic_version != alembic_version:
        ec.print(f"Database schema not up to date (is {db_alembic_version}, but should be {alembic_version}). "
                 f"Please run ym db upgrade.")
        exit(-1)
    return s_maker()


def get_engine() -> Engine:
    db_path = get_path()
    debug_print(f"Connecting to database {db_path}.")
    return create_engine(db_path)


def get_path() -> str:
    config = load_config()
    db = config.get_current_db()
    driver = db["driver"]
    path = db["path"]
    if driver == "sqlite":
        driver += ":///"
    else:
        driver += "://"
    return f"{driver}{path}"


def get_alembic_version(session: Session) -> str:
    result = session.execute(text("SELECT version_num FROM alembic_version LIMIT 1;"))
    for row in result:
        debug_print(f"Alembic version of database is {row[0]}.")
        return row[0]
