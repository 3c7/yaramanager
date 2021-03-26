import io
from typing import Dict, List

from plyara import Plyara
from sqlalchemy.orm import Session

from yaramanager.models.meta import Meta
from yaramanager.models.rule import Rule
from yaramanager.models.string import String
from yaramanager.models.tag import Tag


def read_rulefile(path: str) -> List[Dict]:
    """
    Reads a file given through `path` and returns the plyara parsed list.

    >>> list_of_rules = read_rulefile(path)
    """
    with io.open(path, "r") as handle:
        raw = handle.read()
    return Plyara().parse_string(raw)


def plyara_obj_to_rule(obj: Dict, session: Session) -> Rule:
    """
    Converts a yara rule dictionary representation into a Rule object.

    >>> r = plyara_obj_to_rule(...)
    >>> r.__repr__()
    <Rule apt_ZZ_SlippingTRex_Loader_Mar2021_1>
    """
    r = Rule()
    r.name = obj.get("rule_name", "Unnamed rule")
    for idx, meta in enumerate(obj.get("metadata", [])):
        for k, v in meta.items():
            m = Meta(
                key=k,
                value=v,
                order=idx
            )
            r.meta.append(m)
    for idx, string in enumerate(obj.get("strings", [])):
        s = String(
            name=string["name"],
            value=string["value"],
            order=idx,
            type=string["type"]
        )
        s.modifiers = 0
        for mod in string.get("modifiers", []):
            if mod == "ascii":
                s.modifiers = s.modifiers | 0x1
            elif mod == "wide":
                s.modifiers = s.modifiers | 0x2
            elif mod == "xor":
                s.modifiers = s.modifiers | 0x4
            elif mod == "base64":
                s.modifiers = s.modifiers | 0x8
        r.strings.append(s)
    r.imports = 0
    for imp in obj.get("imports", []):
        if imp == "pe":
            r.imports = r.imports | 0x1
        elif imp == "elf":
            r.imports = r.imports | 0x2
        elif imp == "math":
            r.imports = r.imports | 0x4
        elif imp == "hash":
            r.imports = r.imports | 0x8
        elif imp == "vt":
            r.imports = r.imports | 0x10
    for tag in obj.get("tags", []):
        t = session.query(Tag).filter(Tag.name == tag).first()
        if t:
            r.tags.append(t)
        else:
            t = Tag(
                name=tag
            )
            r.tags.append(t)
    r.condition = obj["raw_condition"].split("\n", 1)[1]
    return r
