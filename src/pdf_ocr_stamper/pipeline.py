from pathlib import Path
import csv
import traceback
import fitz
from PIL import Image

from .manifest import load_manifest, parse_page_range
from .rules_loader import load_rules, pick_rule_for
from .anchors import find_anchor_bbox, compute_pos_from_anchor, find_signature_line
from .placement import place_by_position
from .signature import get_signature

def _calc_sig_size(img_w, img_h, width, height, scale, keep_aspect):
    if (width is None and height is None) and scale is not None:
        width = img_w * scale
        height = img_h * scale
    elif width is not None and height is None and keep_aspect:
        height = width * (img_h / img_w)
    elif height is not None and width is None and keep_aspect:
        width = height * (img_w / img_h)
    if width is None:  width = img_w
    if height is None: height = img_h
    return float(width), float(height)

def _append_error(err_rows, file_name, where, exc: Exception):
    err_rows.append({
        "file": file_name,
        "where": where,
        "error": f"{type(exc).__name__}: {exc}",
        "stack": "".join(traceback.format_exception_only(type(exc), exc)).strip()
    })

def process_batch(cfg: dict):
    input_dir = Path(cfg["input_dir"])
    output_dir = Path(cfg["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = load_manifest(cfg.get("manifest_csv"))
    dry_run = bool(cfg.get("dry_run"))
    previews_dir = Path("previews") if dry_run else None
    if previews_dir:
        previews_dir.mkdir(parents=True, exist_ok=True)

    rules_cfg = load_rules(cfg.get("rules_yaml"))
    outlog_path = Path(cfg.get("outlog", "output/placement_log.csv"))
    outlog_path.parent.mkdir(parents=True, exist_ok=True)

    placement_rows = []
    error_rows = []
    error_log_path = output_dir / "error_log.csv"

    default_x = cfg.get("x", 0)
    default_y = cfg.get("y", 0)
    default_width = cfg.get("width")
    default_height = cfg.get("height")
    default_rotation = cfg.get("rotation", 0)
    default_scale = cfg.get("scale")
    default_keep_aspect = bool(cfg.get("keep_aspect", True))
    default_page = cfg.get("page", 1)
    default_range = cfg.get("stamp_page_range")

    try:
        img_bytes, img_w, img_h = get_signature(cfg)
    except Exception as e:
        _append_error(error_rows, "(global)", "load_signature", e)
        with error_log_path.open("w", newline="", encoding="utf-8") as ef:
            w = csv.DictWriter(ef, fieldnames=["file", "where", "error", "stack"])
            w.writeheader()
            w.writerows(error_rows)
        raise

    for pdf_path in input_dir.glob("*.pdf"):
        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            _append_error(error_rows, pdf_path.name, "open_pdf", e)
            continue

        try:
            page_count = doc.page_count
            if page_count <= 0:
                _append_error(error_rows, pdf_path.name, "validate_pdf", ValueError("PDF sin páginas"))
                doc.close()
                continue

            try:
                rule = pick_rule_for(pdf_path.name, rules_cfg)
                defaults_rule = rules_cfg.get("defaults", {}) or {}
            except Exception as e:
                _append_error(error_rows, pdf_path.name, "load_rules_for_file", e)
                rule = None
                defaults_rule = {}

            rows = manifest.get(pdf_path.name.lower(), []) or [dict()]

            for row in rows:
                # -------- Resolver páginas (con search_last_pages) --------
                try:
                    row_range = row.get("stamp_page_range") if row else None

                    # N últimas páginas desde la regla aplicada o defaults de rules.yaml
                    try:
                        search_last = int(
                            ((rule or {}).get("search_last_pages")
                             or (rules_cfg.get("defaults", {}) or {}).get("search_last_pages")
                             or 0)
                        )
                    except Exception:
                        search_last = 0

                    explicit_range = bool(row_range or default_range)
                    explicit_page  = bool((row.get("page") if row else None) or cfg.get("page"))

                    if explicit_range:
                        pages = parse_page_range(row_range or default_range, page_count)

                    elif explicit_page:
                        # Se respeta 'page' si viene en manifest o en config.yaml
                        page1 = int((row.get("page") if row else None) or cfg.get("page") or 1)
                        pages = [min(max(page1, 1), page_count)]

                    elif search_last > 0:
                        # SIN page/range → usar ÚLTIMAS N páginas
                        start = max(1, page_count - search_last + 1)
                        pages = list(range(start, page_count + 1))

                    else:
                        # Fallback clásico (si no hay reglas)
                        pages = [1]

                except Exception as e:
                    _append_error(error_rows, pdf_path.name, "resolve_pages", e)
                    continue

                # -------- PATCH B: preferir último y cortar tras primer ancla --------
                prefer_last = (search_last > 0) and not explicit_range and not explicit_page
                iter_pages = reversed(pages) if prefer_last else pages
                placed_on_this_row = False
                # --------------------------------------------------------------------

                try:
                    def _f(v):
                        v = (v or "").strip() if isinstance(v, str) else v
                        return None if v in ("", None) else v

                    x = float(_f(row.get("x")) or default_x)
                    y = float(_f(row.get("y")) or default_y)
                    width = _f(row.get("width")) or default_width
                    height = _f(row.get("height")) or default_height
                    width = float(width) if width is not None else None
                    height = float(height) if height is not None else None
                    scale = _f(row.get("scale")) or default_scale or defaults_rule.get("scale")
                    scale = float(scale) if scale is not None else None
                    rotation = int(_f(row.get("rotation")) or default_rotation)
                    keep_aspect = str(_f(row.get("keep_aspect")) or default_keep_aspect or defaults_rule.get("keep_aspect", True)).lower() == "true"

                    sig_w, sig_h = _calc_sig_size(img_w, img_h, width, height, scale, keep_aspect)
                except Exception as e:
                    _append_error(error_rows, pdf_path.name, "resolve_geometry", e)
                    continue

                for p1 in iter_pages:
                    try:
                        page = doc.load_page(p1 - 1)

                        strategy_used = None
                        place_x, place_y = None, None

                        # 1) Anchor por texto
                        try:
                            anchor_list = (rule or {}).get("anchors") or defaults_rule.get("anchors")
                            if anchor_list:
                                found = find_anchor_bbox(page, anchor_list)
                                if found:
                                    bbox, anchor_rule = found
                                    dx = anchor_rule.get("dx", 0)
                                    dy = anchor_rule.get("dy", 0)
                                    align = anchor_rule.get("align", "below_left")
                                    place_x, place_y = compute_pos_from_anchor(bbox, align, dx, dy, sig_w, sig_h)
                                    strategy_used = f"anchor:{anchor_rule.get('regex')}"
                        except Exception as e:
                            _append_error(error_rows, pdf_path.name, f"anchor_page_{p1}", e)

                        # 2) Detección de línea
                        if place_x is None:
                            try:
                                lcfg = ((rule or {}).get("line_detection") or {})
                                if lcfg.get("enabled"):
                                    min_w = lcfg.get("min_width")
                                    dy_above_line = lcfg.get("dy_above_line", 10)
                                    xy = find_signature_line(page, min_w, dy_above_line)
                                    if xy:
                                        lx, ly = xy
                                        place_x, place_y = lx, ly
                                        strategy_used = f"line_detection(min_width={min_w})"
                            except Exception as e:
                                _append_error(error_rows, pdf_path.name, f"line_detection_page_{p1}", e)

                        # 3) Posición relativa
                        if place_x is None:
                            try:
                                fback = (rule or {}).get("fallback") or {}
                                position = fback.get("position") or defaults_rule.get("position")
                                margin_x = fback.get("margin_x", defaults_rule.get("margin_x"))
                                margin_y = fback.get("margin_y", defaults_rule.get("margin_y"))
                                offset_x = fback.get("offset_x", defaults_rule.get("offset_x"))
                                offset_y = fback.get("offset_y", defaults_rule.get("offset_y"))
                                if position:
                                    place_x, place_y = place_by_position(page, position, sig_w, sig_h, margin_x, margin_y, offset_x, offset_y)
                                    strategy_used = f"relative:{position}"
                            except Exception as e:
                                _append_error(error_rows, pdf_path.name, f"relative_pos_page_{p1}", e)

                        # 4) Absoluto
                        if place_x is None:
                            place_x, place_y = x, y
                            strategy_used = "absolute_xy"

                        rect = fitz.Rect(place_x, place_y, place_x + sig_w, place_y + sig_h)

                        if dry_run:
                            try:
                                page.insert_image(rect, stream=img_bytes, rotate=rotation)
                                out_dir = (Path("previews") / Path(pdf_path.stem))
                                out_dir.mkdir(parents=True, exist_ok=True)
                                pix = page.get_pixmap()
                                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                                img.save(out_dir / f"page-{p1}.jpg", format="JPEG", quality=92)

                                # Si fue por ancla, marcamos para cortar esta fila
                                if strategy_used and strategy_used.startswith("anchor:"):
                                    placed_on_this_row = True

                            except Exception as e:
                                _append_error(error_rows, pdf_path.name, f"dry_run_render_page_{p1}", e)
                            finally:
                                try:
                                    orig_path = doc.name
                                    doc.close()
                                    doc = fitz.open(orig_path)
                                except Exception as e:
                                    _append_error(error_rows, pdf_path.name, "dry_run_reopen_doc", e)
                                    break
                        else:
                            try:
                                page.insert_image(rect, stream=img_bytes, rotate=rotation)

                                # Si fue por ancla, marcamos para cortar esta fila
                                if strategy_used and strategy_used.startswith("anchor:"):
                                    placed_on_this_row = True

                            except Exception as e:
                                _append_error(error_rows, pdf_path.name, f"insert_image_page_{p1}", e)
                                continue

                        placement_rows.append({
                            "file": pdf_path.name,
                            "page": p1,
                            "strategy": strategy_used,
                            "x": round(place_x, 2),
                            "y": round(place_y, 2),
                            "w": round(sig_w, 2),
                            "h": round(sig_h, 2),
                            "rotation": rotation
                        })

                        # PATCH B: si ya colocamos por ancla en esta fila, detenemos aquí
                        if placed_on_this_row:
                            break

                    except Exception as e:
                        _append_error(error_rows, pdf_path.name, f"process_page_{p1}", e)

            if not dry_run:
                try:
                    out_path = output_dir / pdf_path.name
                    doc.save(out_path)
                except Exception as e:
                    _append_error(error_rows, pdf_path.name, "save_pdf", e)

        finally:
            try:
                doc.close()
            except Exception:
                pass

    with outlog_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["file", "page", "strategy", "x", "y", "w", "h", "rotation"])
        w.writeheader()
        w.writerows(placement_rows)

    if error_rows:
        with error_log_path.open("w", newline="", encoding="utf-8") as ef:
            w = csv.DictWriter(ef, fieldnames=["file", "where", "error", "stack"])
            w.writeheader()
            w.writerows(error_rows)
