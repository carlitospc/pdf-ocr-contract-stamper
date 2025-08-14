def parse_length(val: str | float | int | None, ref: float | None = None) -> float | None:
    """
    Convierte "10%" a puntos (usando ref como 100%), o número directo.
    """
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    if not s:
        return None
    if s.endswith("%"):
        if ref is None:
            raise ValueError("Porcentaje sin referencia (ref=None).")
        pct = float(s[:-1])
        return ref * pct / 100.0
    return float(s)

def name_matches(pattern: str, filename: str) -> bool:
    import fnmatch
    return fnmatch.fnmatch(filename.lower(), pattern.lower())
