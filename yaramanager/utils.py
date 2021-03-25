from typing import Dict
from yaramanager.models.rule import Rule
from yaramanager.models.meta import Meta


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
    return r
