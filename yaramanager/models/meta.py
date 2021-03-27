from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from yaramanager.db.base_class import Base


class Meta(Base):
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    key = Column(String(255), index=True)
    value = Column(String(255), index=True)
    order = Column(Integer)
    rule_id = Column(Integer, ForeignKey("rule.id"))
    rule = relationship("Rule", back_populates="meta")

    def __repr__(self):
        if self.rule:
            return f"<Meta {self.key}={self.value} (attached to {self.rule.name})>"
        return f"<Meta {self.key}={self.value}>"
