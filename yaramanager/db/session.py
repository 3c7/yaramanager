from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session


def get_session(path: str) -> Session:
    engine = create_engine(f"sqlite:///{path}")
    return sessionmaker(autocommit=False, bind=engine)()


def get_engine(path: str) -> Engine:
    return create_engine(f"sqlite:///{path}")
