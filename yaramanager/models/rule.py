from sys import stderr
from typing import Any, List

from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from yarabuilder import YaraBuilder

from yaramanager.db.base_class import Base
from yaramanager.models.tables import tags_rules
from yaramanager.config import load_config


class Rule(Base):
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), index=True)
    meta = relationship("Meta", back_populates="rule", cascade="all, delete, delete-orphan")
    strings = relationship("String", back_populates="rule", cascade="all, delete, delete-orphan")
    condition = Column(Text)
    imports = Column(Integer)
    tags = relationship("Tag", back_populates="rules", secondary=tags_rules)
    ruleset_id = Column(Integer, ForeignKey("ruleset.id"))
    ruleset = relationship("Ruleset", back_populates="rules")

    @property
    def import_list(self) -> List[str]:
        imports = self.imports
        for imp in ["pe", "elf", "math", "hash", "vt"]:
            if imports & 0x1 > 0:
                yield imp
            imports = imports >> 1

    def __repr__(self):
        return f"<Rule {self.name}>"

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
        self.add_to_yarabuilder(yb)
        return yb.build_rule(self.name)

    def add_to_yarabuilder(self, yb: YaraBuilder) -> None:
        """Add the rule object to a given YaraBuilder instance

        >>> rule = Rule(...)
        >>> yb = YaraBuilder()
        >>> rule.add_to_yarabuilder(yb)
        >>> print(yb.build_rules())
        """
        yb.create_rule(self.name)
        key = load_config().get("ruleset_meta_key", "ruleset")
        if self.ruleset:
            yb.add_meta(self.name, key, self.ruleset.name)
        for meta in self.meta:
            yb.add_meta(
                self.name,
                meta.key,
                meta.value
            )
        for string in self.strings:
            s_name = string.name[1:]
            if string.type == "text":
                yb.add_text_string(
                    self.name,
                    string.value,
                    s_name,
                    string.modifier_list
                )
            elif string.type == "byte":
                yb.add_hex_string(
                    self.name,
                    string.value,
                    s_name,
                    string.modifier_list  # Todo: Check hex string modifiers - this list should always be empty?
                )
            elif string.type == "regex":
                yb.add_regex_string(
                    self.name,
                    string.value,
                    s_name,
                    string.modifier_list
                )
            else:
                print(f"ERROR: Unknown string type \"{string.type}\".", file=stderr)
        for tag in self.tags:
            yb.add_tag(self.name, tag.name)
        for imp in self.import_list:
            yb.add_import(self.name, imp)
        yb.add_condition(self.name, self.condition.strip())
