from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from yaramanager.db.base_class import Base
from yaramanager.models.tables import tags_rules


class Tag(Base):
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(255), index=True)
    rules = relationship("Rule", back_populates="tags", secondary=tags_rules)

    def __repr__(self):
        return f"<Tag {self.name}>"
