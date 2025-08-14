from __future__ import annotations
import re
from typing import Optional, Tuple, List
import fitz
from .utils_units import parse_length

BBox = Tuple[float, float, float, float]  # x0,y0,x1,y1

def find_anchor_bbox(page: fitz.Page, regex_list: list[dict]):
    """
    Busca en este orden:
      1) Por LÍNEAS (texto continuo) usando page.get_text("dict")
      2) Por PALABRAS sueltas (fallback)
    Devuelve (bbox, regla_anchor) o None.
    """
    import re

    # 1) Buscar por líneas (mejor para frases como "FIRMA DEL REPRESENTANTE LEGAL")
    try:
        d = page.get_text("dict")
        for rule in regex_list or []:
            pattern = rule.get("regex")
            if not pattern:
                continue
            rx = re.compile(pattern, flags=re.I)

            for block in d.get("blocks", []):
                for line in block.get("lines", []):
                    # texto completo de la línea
                    line_text = "".join(span.get("text", "") for span in line.get("spans", []))
                    if rx.search(line_text or ""):
                        # bbox = unión de spans de la línea
                        x0s, y0s, x1s, y1s = [], [], [], []
                        for span in line.get("spans", []):
                            b = span.get("bbox", None)
                            if not b: 
                                continue
                            x0s.append(b[0]); y0s.append(b[1]); x1s.append(b[2]); y1s.append(b[3])
                        if x0s:
                            bbox = (min(x0s), min(y0s), max(x1s), max(y1s))
                            return bbox, rule
    except Exception:
        pass  # si algo falla, seguimos con búsqueda por palabras

    # 2) Fallback: por PALABRAS sueltas (sirve para anclas de una sola palabra, p.ej. "AUTORIZO")
    words = page.get_text("words")  # [x0,y0,x1,y1, text, ...]
    if not words:
        return None

    for rule in regex_list or []:
        pattern = rule.get("regex")
        if not pattern:
            continue
        rx = re.compile(pattern, flags=re.I)
        for x0, y0, x1, y1, text, *_ in words:
            if rx.search(text or ""):
                return (float(x0), float(y0), float(x1), float(y1)), rule

    return None


def compute_pos_from_anchor(anchor_bbox: BBox, align: str, dx: float, dy: float, sig_w: float, sig_h: float) -> tuple[float, float]:
    x0, y0, x1, y1 = anchor_bbox
    anchor_cx = (x0 + x1) / 2
    anchor_cy = (y0 + y1) / 2

    align = (align or "below_left").lower()
    if align == "below_left":
        x, y = x0, y1
    elif align == "below_center":
        x, y = anchor_cx - sig_w / 2, y1
    elif align == "right_center":
        x, y = x1, anchor_cy - sig_h / 2
    elif align == "above_left":
        x, y = x0, y0 - sig_h
    elif align == "above_center":
        x, y = anchor_cx - sig_w / 2, y0 - sig_h
    else:
        x, y = x0, y1

    return x + float(dx or 0), y + float(dy or 0)

def find_signature_line(page: fitz.Page, min_width: str | float | None, dy_above_line: float | None) -> Optional[tuple[float, float]]:
    """
    Busca una línea horizontal larga y retorna (x, y_sup_izq) donde colocar
    la firma (y desplazada hacia arriba por dy_above_line).
    """
    drawings = page.get_drawings()
    W, H = page.mediabox_size
    min_w_pts = parse_length(min_width, ref=W) if min_width else None
    best = None  # (y, x0, x1)

    for d in drawings:
        t = d.get("type")
        pts = None
        if t == "line":
            (op, p0), (_, p1) = d["items"]
            pts = (p0, p1)
        elif t == "polyline" and len(d["items"]) == 2:
            (op, p0), (_, p1) = d["items"]
            pts = (p0, p1)

        if not pts:
            continue

        (x0, y0), (x1, y1) = pts
        if abs(y1 - y0) < 1.0:  # casi horizontal
            width = abs(x1 - x0)
            if min_w_pts is None or width >= min_w_pts:
                y = (y0 + y1) / 2.0
                if (best is None) or (y > best[0]):  # la más baja
                    best = (y, min(x0, x1), max(x0, x1))

    if best:
        y, x0, x1 = best
        y_top = y - float(dy_above_line or 10)
        return (x0, y_top)
    return None
