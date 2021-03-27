from typing import List

from sqlalchemy import Column, Integer, String as SA_String, ForeignKey, Text
from sqlalchemy.orm import relationship

from yaramanager.db.base_class import Base


class String(Base):
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(SA_String(255), index=True)
    # Types are: text, hex, regex
    type = Column(SA_String(5))
    value = Column(Text)
    modifiers = Column(Integer)
    order = Column(Integer)

    rule_id = Column(Integer, ForeignKey("rule.id"))
    rule = relationship("Rule", back_populates="strings")

    def is_ascii(self):
        return self.modifiers & 0x1 > 0

    def is_wide(self):
        return self.modifiers & 0x2 > 0

    def is_xor(self):
        return self.modifiers & 0x4 > 0

    def is_base64(self):
        return self.modifiers & 0x8 > 0

    @property
    def modifier_list(self) -> List[str]:
        m = self.modifiers
        l = []
        for mod in ["ascii", "wide", "xor", "base64"]:
            if m & 0x1:
                l.append(mod)
            m = m >> 1
        return l

    def __repr__(self):
        if self.rule:
            return f"<String {self.name} (attached to {self.rule.name})>"
        return f"<String {self.name}>"
