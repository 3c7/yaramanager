import io
import os
import re
import subprocess
from hashlib import md5
from sys import stderr, exit
from tempfile import mkstemp
from typing import Dict, List, Union, Tuple, Optional

from plyara import Plyara
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table
from sqlalchemy.orm import Session
from yarabuilder import YaraBuilder

from yaramanager.config import load_config
from yaramanager.db.base import Rule, Meta, String, Tag, Ruleset
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
    r.meta = plyara_object_to_meta(obj)
    r.strings = plyara_object_to_strings(obj)
    r.imports = plyara_object_to_imports(obj)
    r.tags = plyara_object_to_tags(obj, session)
    r.condition = plyara_object_to_condition(obj)
    ruleset = plyara_object_to_ruleset(obj, session)
    r.ruleset = ruleset
    return r


def plyara_object_to_meta(obj: Dict) -> List[Meta]:
    """Returns a list of initialized Meta objects based on a plyara object."""
    meta: List[Meta] = []
    for idx, m_dict in enumerate(obj.get("metadata", [])):
        for k, v in m_dict.items():
            if k.lower() == "ruleset":
                continue
            m = Meta(
                key=k,
                value=v,
                order=idx
            )
            meta.append(m)
    return meta


def plyara_object_to_strings(obj: Dict) -> List[String]:
    """Returns a list of initialized String objects from a plyara object."""
    strings: List[String] = []
    for idx, ply_string in enumerate(obj.get("strings", [])):
        s = String(
            name=ply_string["name"],
            value=ply_string["value"],
            order=idx,
            type=ply_string["type"]
        )
        s.modifiers = 0
        for mod in ply_string.get("modifiers", []):
            if mod == "ascii":
                s.modifiers = s.modifiers | 0x1
            elif mod == "wide":
                s.modifiers = s.modifiers | 0x2
            elif mod == "xor":
                s.modifiers = s.modifiers | 0x4
            elif mod == "base64":
                s.modifiers = s.modifiers | 0x8
        strings.append(s)
    return strings


def plyara_object_to_imports(obj: Dict) -> int:
    """Returns an integer representing imported yara modules."""
    imports = 0
    conditions = plyara_object_to_condition(obj)
    for imp in obj.get("imports", []):
        if imp == "pe" and "pe." in conditions:
            imports = imports | 0x1
        elif imp == "elf" and "elf." in conditions:
            imports = imports | 0x2
        elif imp == "math" and "math." in conditions:
            imports = imports | 0x4
        elif imp == "hash" and "hash." in conditions:
            imports = imports | 0x8
        elif imp == "vt" and "vt." in conditions:
            imports = imports | 0x10
    return imports


def plyara_object_to_tags(obj: Dict, session: Optional[Session] = None) -> List[Tag]:
    """Returns a list of initialized Tag objects based on a plyara dict"""
    tags: List[Tag] = []
    if not session:
        session = get_session()

    for tag in obj.get("tags", []):
        t = session.query(Tag).filter(Tag.name == tag).first()
        if t:
            tags.append(t)
        else:
            t = Tag(
                name=tag
            )
            tags.append(t)
    return tags


def plyara_object_to_condition(obj: Dict) -> str:
    """Returns condition string from plyara object"""
    return obj["raw_condition"].split(":", 1)[1].strip()


def plyara_object_to_ruleset(obj: Dict, session: Session) -> Union[Ruleset, None]:
    """Returns ruleset object, if ruleset is given as meta tag, or None"""
    key = load_config().get("ruleset_meta_key", "ruleset")
    for m_dict in obj.get("metadata", []):
        for k, v in m_dict.items():
            if k != key:
                continue

            ruleset = session.query(Ruleset).filter(Ruleset.name == v).first()
            if not ruleset:
                ruleset = Ruleset(name=v)
            return ruleset
    return None


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
        for mdata in rule.get("metadata", []):
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
    c, ec = Console(), Console(stderr=True, style="bold red")
    config = load_config()
    env_editor = os.getenv("EDITOR", None)
    env_disable_status = os.getenv("DISABLE_STATUS", None)
    if env_editor:
        command = env_editor.split(" ")
    else:
        command = config.get("editor", None)
        if not command:
            ec.print("Editor not given. Please set editor config value or use EDITOR environment variable.")
            exit(-1)
    command.append(path)
    if env_disable_status:
        subprocess.call(command)
    else:
        if not status:
            status = f"{path} opened in external editor..."
        with c.status(status):
            subprocess.call(command)


def open_temp_file_with_template():
    ec = Console(stderr=True, style="bold red")
    config = load_config()
    fd_temp, path = mkstemp(".yar")
    with os.fdopen(fd_temp, "w") as fh:
        try:
            fh.write(config["template"])
        except KeyError:
            ec.print("Template is missing. Please set template variable in config.")
            exit(-1)
    open_file(path)
    return path


def get_rule_by_identifier(identifier: Union[str, int], session: Optional[Session] = None) -> List[Rule]:
    if not session:
        session = get_session()
    rules = session.query(Rule)
    if isinstance(identifier, int) or re.fullmatch(r"^\d+$", identifier):
        rules = rules.filter(Rule.id == int(identifier))
    else:
        rules = rules.filter(Rule.name.like(f"%{identifier}%"))
    return rules.all()


def get_ruleset_by_identifier(identifier: Union[str, int], session: Optional[Session] = None) -> Ruleset:
    if not session:
        session = get_session()

    ruleset = session.query(Ruleset)
    if isinstance(identifier, int) or re.fullmatch(r"^\d+$", identifier):
        return ruleset.get(int(identifier))
    else:
        return ruleset.filter(Ruleset.name.like(identifier)).first()


def rules_to_table(rules: List[Rule], ensure: Optional[bool] = False) -> Table:
    """Creates a rich.table.Table object from s list of rules."""
    config = load_config()
    meta_columns = config.get("meta", {})
    ensure_meta = config.get("ensure", {}).get("ensure_meta", [])
    ensure_tags = config.get("ensure", {}).get("ensure_tag", True)
    table = Table()
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Ruleset")
    if ensure and ensure_tags:
        table.add_column("Tags [yellow]:warning:")
    else:
        table.add_column("Tags")
    for column in meta_columns.keys():
        c_header = column + " [yellow]:warning:" if meta_columns[column] in ensure_meta and ensure else column
        table.add_column(c_header)

    for rule in rules:
        if ensure and ensure_tags and len(rule.tags) == 0:
            tags = "[yellow]:warning:"
        else:
            tags = ", ".join([tag.name for tag in rule.tags])

        row = [
            str(rule.id),
            rule.name,
            rule.ruleset.name if rule.ruleset else "None",
            tags
        ]
        for column in meta_columns.values():
            m_value = rule.get_meta_value(column, default="None")
            if ensure and column in ensure_meta and m_value == "None":
                row.append("[yellow]:warning:")
            else:
                row.append(rule.get_meta_value(column, default="None"))
        table.add_row(*row)
    return table


def rules_to_highlighted_string(rules: List[Rule]):
    yb = YaraBuilder()
    for rule in rules:
        if rule.name not in yb.yara_rules.keys():
            rule.add_to_yarabuilder(yb)
    # As there is no yara lexer available in pygments, we're usign python here.
    return Syntax(yb.build_rules(), "python", background_color="default")


def filter_rules_by_name_and_tag(name: str, tag: str, session: Optional[Session] = None) -> Tuple[List[Rule], int]:
    if not session:
        session = get_session()

    rules = session.query(Rule)
    if tag and len(tag) > 0:
        rules = rules.select_from(Tag).join(Rule.tags).filter(Tag.name == tag)
    if name and len(name) > 0:
        rules = rules.filter(Rule.name.like(f"%{name}%"))
    count = rules.count()

    if count == 0:
        return [], count
    else:
        return rules.all(), count
