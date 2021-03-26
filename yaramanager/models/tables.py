from sqlalchemy import Table, Column, Integer, ForeignKey

from yaramanager.db.base_class import Base

tags_rules = Table(
    "tags_rules",
    Base.metadata,
    Column("tag_id", Integer, ForeignKey("tag.id")),
    Column("rule_id", Integer, ForeignKey("rule.id"))
)
