from __future__ import annotations
from typing import Tuple
import fitz
from .utils_units import parse_length

def place_by_position(page: fitz.Page, position: str, sig_w: float, sig_h: float,
                      margin_x, margin_y, offset_x=None, offset_y=None) -> Tuple[float, float]:
    W, H = page.mediabox_size
    mx = parse_length(margin_x, ref=W) if margin_x is not None else 0
    my = parse_length(margin_y, ref=H) if margin_y is not None else 0
    ox = parse_length(offset_x, ref=W) if offset_x is not None else 0
    oy = parse_length(offset_y, ref=H) if offset_y is not None else 0

    pos = (position or "bottom_right").lower()
    if pos == "top_left":
        x, y = mx, my
    elif pos == "top_right":
        x, y = W - sig_w - mx, my
    elif pos == "bottom_left":
        x, y = mx, H - sig_h - my
    elif pos == "center":
        x, y = (W - sig_w) / 2, (H - sig_h) / 2
    else:  # bottom_right
        x, y = W - sig_w - mx, H - sig_h - my

    return x + ox, y + oy
