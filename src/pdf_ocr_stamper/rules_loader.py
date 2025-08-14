from pathlib import Path
import yaml
from .utils_units import name_matches

def load_rules(path: str | None):
    if not path:
        return {"defaults": {}, "rules": []}
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"rules.yaml no encontrado: {p}")
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    data.setdefault("defaults", {})
    data.setdefault("rules", [])
    return data

def pick_rule_for(filename: str, rules_cfg: dict) -> dict | None:
    rules = rules_cfg.get("rules", [])
    for r in rules:
        pat = r.get("match")
        if pat and name_matches(pat, filename):
            return r
    return None
