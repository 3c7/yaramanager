from sqlalchemy.orm import as_declarative, declared_attr
from typing import Any


@as_declarative()
class Base:
    id: Any
    __name__: str

    @declared_attr
    def __tablename__(self) -> str:
        """This automatically generates a tablename"""
        return self.__name__.lower()
