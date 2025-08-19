import typer
from pathlib import Path
import os, sys
from pdf_ocr_stamper.config_loader import load_config
from pdf_ocr_stamper.pipeline import process_batch

def _abs(p: str | None) -> str:
    if not p:
        return ""
    try:
        return str(Path(p).resolve())
    except Exception:
        return str(p)

def main(
    config: str = typer.Option("config/config.yaml", "--config", "-c"),
    manifest: str = typer.Option(None, "--manifest", "-m"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    rules: str = typer.Option(None, "--rules", help="Ruta a rules.yaml"),
    outlog: str = typer.Option("output/placement_log.csv", "--outlog", help="CSV con estrategia usada"),
    yes: bool = typer.Option(False, "--yes", "-y", help="No pedir confirmación; continuar automáticamente")
):
    cfg = load_config(config)
    if manifest:
        cfg["manifest_csv"] = manifest
    cfg["dry_run"] = dry_run
    if rules:
        cfg["rules_yaml"] = rules
    cfg["outlog"] = outlog
    
    
    # === Diagnóstico: muestra de dónde se tomará cada cosa ===
    print("──────────────── Configuración de rutas ────────────────")
    print(f"[INFO] Working dir: {Path.cwd()}")
    if getattr(sys, "frozen", False):
        print(f"[INFO] Ejecutable (PyInstaller): {Path(sys.executable)}")
        print(f"[INFO] Carpeta del EXE: {Path(sys.executable).parent}")
    print(f"[INFO] Config recibido: {config}  ->  {_abs(config)}")

    # Soportar ambas claves si tu config usa 'rules_yaml' o 'rules_file'
    rules_src = cfg.get("rules_yaml") or cfg.get("rules_file")
    if rules_src:
        abs_rules = _abs(rules_src)
        print(f"[INFO] Rules (cfg): {rules_src}  ->  {abs_rules}")
        print(f"[INFO] Rules existe?: {Path(abs_rules).exists()}")
    else:
        print("[WARN] Rules no definido en cfg (se usará valor por defecto interno/convención).")

    if cfg.get("manifest_csv"):
        print(f"[INFO] Manifest: {cfg['manifest_csv']}  ->  {_abs(cfg['manifest_csv'])}")

    print(f"[INFO] OutLog CSV: {outlog}  ->  {_abs(outlog)}")
    print(f"[INFO] Dry-run: {dry_run}")
    print("──────────────────────────────────────────────────────")
    
    
    # pasa el flag al pipeline
    process_batch(cfg, auto_confirm=yes)

if __name__ == "__main__":
    typer.run(main)
