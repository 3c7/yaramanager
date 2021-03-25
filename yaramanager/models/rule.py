from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from yaramanager.db.base_class import Base


class Rule(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    meta = relationship("Meta", back_populates="rule")

    def __repr__(self):
        return f"<Rule {self.name}>"
