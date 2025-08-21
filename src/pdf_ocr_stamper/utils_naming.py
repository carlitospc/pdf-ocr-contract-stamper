# src/pdf_ocr_stamper/utils_naming.py
from pathlib import Path

def mark_filename(path: Path, prefix: str = "", suffix: str = "") -> Path:
    """Inserta prefix/suffix respetando la extensión."""
    if not prefix and not suffix:
        return path
    stem = path.stem
    new_name = f"{prefix}{stem}{suffix}{path.suffix}"
    return path.with_name(new_name)
