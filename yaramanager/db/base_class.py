from typing import Any

from sqlalchemy.orm import as_declarative, declared_attr


@as_declarative()
class Base:
    id: Any
    __name__: str

    @declared_attr
    def __tablename__(self) -> str:
        """This automatically generates a table name"""
        return self.__name__.lower()
