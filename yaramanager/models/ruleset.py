from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from yaramanager.db.base_class import Base


class Ruleset(Base):
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(255), index=True)
    rules = relationship("Rule", back_populates="ruleset")
