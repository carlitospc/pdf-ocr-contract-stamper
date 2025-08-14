from pathlib import Path
import yaml

def load_config(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config no encontrada: {p}")
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    sig = data.get("signature", {})
    if not sig or not sig.get("path"):
        raise ValueError("Debes configurar signature.path en config.yaml")
    return data
