import os

from rich.console import Console
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

from yaramanager.config import load_config


def get_session() -> Session:
    config = load_config()
    db = config.get_current_db()
    driver = db["driver"]
    path = db["path"]
    if driver == "sqlite" and not os.path.exists(path) or os.path.getsize(path) == 0:
        ec = Console(stderr=True, style="bold red")
        ec.print("Database not initialized.")
        exit(-1)
    engine = get_engine()
    return sessionmaker(autocommit=False, bind=engine)()


def get_engine() -> Engine:
    db_path = get_path()
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
