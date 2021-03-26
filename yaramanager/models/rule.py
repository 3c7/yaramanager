from sys import stderr
from typing import Any

from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.orm import relationship
from yarabuilder import YaraBuilder

from yaramanager.db.base_class import Base


class Rule(Base):
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), index=True)
    meta = relationship("Meta", back_populates="rule")
    strings = relationship("String", back_populates="rule")
    condition = Column(Text)

    def __repr__(self):
        return f"<YaraRule {self.name}>"

    def _get_meta(self, key: str) -> Any:
        for meta in self.meta:
            if meta.key == key:
                return meta
        return None

    def get_meta_value(self, key: str, default: str) -> str:
        meta = self._get_meta(key)
        return meta.value if meta else default

    def __str__(self):
        yb = YaraBuilder()
        yb.create_rule(self.name)
        for meta in self.meta:
            yb.add_meta(
                self.name,
                meta.key,
                meta.value
            )
        for string in self.strings:
            if string.type == "text":
                yb.add_text_string(
                    self.name,
                    string.value,
                    string.name,
                    string.modifier_list
                )
            elif string.type == "hex":
                yb.add_hex_string(
                    self.name,
                    string.value,
                    string.name,
                    string.modifier_list  # Todo: Check hex string modifiers - this list should always be empty?
                )
            elif string.type == "regex":
                yb.add_regex_string(
                    self.name,
                    string.value,
                    string.name,
                    string.modifier_list
                )
            else:
                print(f"ERROR: Unknown string type \"{string.type}\".", file=stderr)
        yb.add_condition(self.name, self.condition.strip())
        return yb.build_rule(self.name)
