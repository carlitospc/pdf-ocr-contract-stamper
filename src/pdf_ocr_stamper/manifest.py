import csv
from pathlib import Path

def parse_page_range(expr: str | None, page_count: int):
    expr = (expr or "").strip()
    if not expr:
        return None
    result = set()
    parts = [p.strip() for p in expr.split(",") if p.strip()]
    for p in parts:
        if "-" in p:
            a, b = p.split("-", 1)
            a = a.strip()
            b = b.strip()
            start = int(a) if a else 1
            end = int(b) if b else page_count
            for i in range(start, end + 1):
                if 1 <= i <= page_count:
                    result.add(i)
        else:
            i = int(p)
            if 1 <= i <= page_count:
                result.add(i)
    return sorted(result) or None

def load_manifest(path: str | None):
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"manifest.csv no encontrado: {p}")
    per_file: dict[str, list[dict]] = {}
    with p.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            fname = (row.get("filename") or "").strip().lower()
            if not fname:
                continue
            per_file.setdefault(fname, []).append(row)
    return per_file
