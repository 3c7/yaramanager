import io
from hashlib import md5
from typing import Dict, List, Union

from plyara import Plyara
from sqlalchemy.orm import Session
from yarabuilder import YaraBuilder

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


def parse_rule_file(path: str) -> Union[Dict, List]:
    ply = Plyara()
    with io.open(path) as fh:
        return ply.parse_string(fh.read())


def print_rule(rules: Union[Dict, List]) -> str:
    yb = YaraBuilder()
    if isinstance(rules, dict):
        rules = [rules]
    for rule in rules:
        rn = rule["rule_name"]
        yb.create_rule(rn)
        for mdata in rule["metadata"]:
            for k, v in mdata.items():
                yb.add_meta(rn, k, v)
        for tag in rule["tags"]:
            yb.add_tag(rn, tag)
        for yara_string in rule["strings"]:
            s_type = yara_string["type"]
            s_name = yara_string["name"][1:]
            s_val = yara_string["value"]
            s_mod = yara_string.get("modifiers", [])
            if s_type == "text":
                yb.add_text_string(rn, s_val, s_name, s_mod)
            elif s_type == "regex":
                yb.add_regex_string(rn, s_val, s_name, s_mod)
            elif s_type == "byte":
                yb.add_hex_string(rn, s_val[1:-1].strip(), s_name)
        yb.add_condition(rn, " ".join(rule["condition_terms"]))
    return yb.build_rules()


def get_md5(path: str):
    """Creates md5 hash of a file."""
    hasher = md5()
    with io.open(path, "rb") as fh:
        hasher.update(fh.read())
    return hasher.hexdigest()
