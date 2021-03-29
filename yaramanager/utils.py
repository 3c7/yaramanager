import io
import os
import re
import subprocess
from hashlib import md5
from sys import stderr
from tempfile import mkstemp
from typing import Dict, List, Union, Tuple, Optional

from plyara import Plyara
from rich.console import Console
from rich.table import Table
from sqlalchemy.orm import Session
from yarabuilder import YaraBuilder

from yaramanager.config import load_config
from yaramanager.db.base import Rule, Meta, String, Tag
from yaramanager.db.session import get_session


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


def parse_rule(rule: str) -> Union[Dict, List]:
    ply = Plyara()
    return ply.parse_string(rule)


def parse_rule_file(path: str) -> Union[Dict, List]:
    with io.open(path) as fh:
        return parse_rule(fh.read())


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
    """Creates md5 hash of a file. Used for monitoring file changes during rule editing."""
    hasher = md5()
    with io.open(path, "rb") as fh:
        hasher.update(fh.read())
    return hasher.hexdigest()


def write_ruleset_to_tmp_file(yb: YaraBuilder) -> Tuple[str, int]:
    """Writes a ruleset defined by yarabuilder to a temporary file and returns the path."""
    fd_temp, path = mkstemp(suffix=".yar")
    bytes = write_ruleset_to_file(yb, fd_temp)
    return path, bytes


def write_ruleset_to_file(yb: YaraBuilder, file: Union[int, str]) -> int:
    """Write a ruleset defined by yarabuilder to a given filedescriptor or filepath."""
    text = yb.build_rules()
    if isinstance(file, int):
        with os.fdopen(file, "w") as fh:
            b = fh.write(text)
    else:
        with io.open(file, "w") as fh:
            b = fh.write(text)
    if b <= 0:
        ec = Console(file=stderr)
        ec.print(f"ERR: Number of bytes written should be greater 0 but was {b}.")
    return b


def open_file(path: str, status: Optional[str] = None):
    c = Console()
    config = load_config()
    command = config["editor"]
    command.append(path)
    if not status:
        status = f"File {path} opened in external editor..."
    with c.status(status):
        subprocess.call(command)


def get_rule_by_identifier(identifier: Union[str, int], session: Optional[Session] = None) -> List[Rule]:
    if not session:
        session = get_session()
    rules = session.query(Rule)
    if isinstance(identifier, int) or re.fullmatch(r"^\d+$", identifier):
        rules = rules.filter(Rule.id == int(identifier))
    else:
        rules = rules.filter(Rule.name.like(f"%{identifier}%"))
    return rules.all()


def rules_to_table(rules: List[Rule]) -> Table:
    """Creates a rich.table.Table object from s list of rules."""
    meta_columns = load_config().get("meta", {})
    table = Table()
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Tags")
    for column in meta_columns.keys():
        table.add_column(column)

    for rule in rules:
        row = [
            str(rule.id),
            rule.name,
            ", ".join([tag.name for tag in rule.tags])
        ]
        for column in meta_columns.values():
            row.append(rule.get_meta_value(column, default="None"))
        table.add_row(*row)
    return table
