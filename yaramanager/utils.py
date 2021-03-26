from typing import Dict
from yaramanager.models.rule import Rule
from yaramanager.models.meta import Meta
from yaramanager.models.string import String


def plyara_obj_to_rule(obj: Dict) -> Rule:
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
    r.condition = obj["raw_condition"].split("\n", 1)[1]
    return r
