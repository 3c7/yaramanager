from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
import os
from yaramanager.config import load_config
from rich.console import Console


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
    config = load_config()
    db = config.get_current_db()
    driver = db["driver"]
    path = db["path"]
    if driver == "sqlite":
        driver += ":///"
    else:
        driver += "://"
    return create_engine(f"{driver}{path}")
