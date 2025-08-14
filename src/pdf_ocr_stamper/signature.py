from pathlib import Path
from PIL import Image
import io

_CACHE = {"bytes": None, "w": None, "h": None, "path": None}

def get_signature(cfg: dict | None = None):
    """
    Retorna (img_bytes, img_w, img_h).
    La ruta proviene de cfg['signature']['path'] si se pasa; si no, de _CACHE['path'].
    """
    global _CACHE
    path = None
    if cfg and cfg.get("signature", {}).get("path"):
        path = cfg["signature"]["path"]
    elif _CACHE["path"]:
        path = _CACHE["path"]
    else:
        raise ValueError("No se ha definido signature.path en config.")

    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Firma no encontrada: {p}")

    if _CACHE["bytes"] is not None and _CACHE["path"] == str(p):
        return _CACHE["bytes"], _CACHE["w"], _CACHE["h"]

    img = Image.open(p).convert("RGBA")
    w, h = img.size
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    data = buf.getvalue()

    _CACHE.update({"bytes": data, "w": w, "h": h, "path": str(p)})
    return data, w, h
