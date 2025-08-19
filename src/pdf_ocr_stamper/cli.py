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

def _open_folder(p: Path):
    try:
        if sys.platform.startswith("win"):
            os.startfile(p)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            os.system(f'open "{p}"')
        else:
            os.system(f'xdg-open "{p}"')
    except Exception:
        print(f"[WARN] No se pudo abrir: {p}")

def main(
    config: str = typer.Option("config/config.yaml", "--config", "-c"),
    manifest: str = typer.Option(None, "--manifest", "-m"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    rules: str = typer.Option(None, "--rules", help="Ruta a rules.yaml"),
    outlog: str = typer.Option("output/placement_log.csv", "--outlog", help="CSV con estrategia usada"),
    yes: bool = typer.Option(False, "--yes", "-y", help="No pedir confirmación; continuar automáticamente"),
    menu: bool = typer.Option(False, "--menu", help="Mostrar menú interactivo")
):
    base_cwd = Path.cwd()
    cfg = load_config(config)
    if manifest:
        cfg["manifest_csv"] = manifest
    cfg["dry_run"] = dry_run
    if rules:
        cfg["rules_yaml"] = rules
    cfg["outlog"] = outlog
    
    
    # Muestra de dónde se tomará cada cosa
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
    print(f"[INFO] Menu: {menu}")
    print("──────────────────────────────────────────────────────")
    
    
    # Pasa el flag al pipeline
    if not menu:
        process_batch(cfg, auto_confirm=yes)
        return
    
    # Menú interactivo
    input_dir = Path(cfg.get("input_dir", "input"))
    output_dir = Path(cfg.get("output_dir", "output"))
    previews_dir = Path(cfg.get("previews_dir", "previews"))

    while True:
        print("\n")
        print("┌────────────────────────────────────────────────────┐")
        print("│ PDF OCR Contract Stamper — Menú                    │")
        print("└────────────────────────────────────────────────────┘")
        print("  [1] Procesar (normal)")
        print("  [2] Dry‑run (simulación)")
        print("  [3] Procesar con manifest.csv")
        print("  [4] Abrir carpeta INPUT")
        print("  [5] Abrir carpeta OUTPUT")
        print("  [6] Editar config.yaml")
        print("  [7] Editar rules.yaml")
        print("  [8] Limpiar OUTPUT y PREVIEWS")
        print("  [0] Salir")
        choice = input("\nSeleccione una opción: ").strip()

        if choice == "1":
            cfg_run = dict(cfg)
            cfg_run["dry_run"] = False
            process_batch(cfg_run, auto_confirm=yes)

        elif choice == "2":
            cfg_run = dict(cfg)
            cfg_run["dry_run"] = True
            process_batch(cfg_run, auto_confirm=yes)

        elif choice == "3":
            default_manifest = cfg.get("manifest_csv") or "manifest.csv"
            path_in = input(f"Ruta a manifest.csv [{default_manifest}]: ").strip() or default_manifest
            cfg_run = dict(cfg)
            cfg_run["manifest_csv"] = path_in
            process_batch(cfg_run, auto_confirm=yes)

        elif choice == "4":
            input_dir.mkdir(exist_ok=True)
            _open_folder(base_cwd / input_dir)

        elif choice == "5":
            output_dir.mkdir(exist_ok=True)
            _open_folder(base_cwd / output_dir)

        elif choice == "6":
            print("Abre el archivo y guarda cambios; luego regresa al menú.")
            _open_folder((base_cwd / Path(config)).parent)

        elif choice == "7":
            if rules_src:
                _open_folder((base_cwd / Path(rules_src)).parent)
            else:
                print("No hay rules definido en config; define rules_yaml: rules.yaml")

        elif choice == "8":
            try:
                for folder in (output_dir, previews_dir):
                    fp = base_cwd / folder
                    if fp.exists():
                        # Borrar contenidos sin borrar carpeta
                        for item in fp.iterdir():
                            if item.is_dir():
                                for root, dirs, files in os.walk(item, topdown=False):
                                    for f in files:
                                        Path(root, f).unlink(missing_ok=True)
                                    for d in dirs:
                                        Path(root, d).rmdir()
                                item.rmdir()
                            else:
                                item.unlink(missing_ok=True)
                    fp.mkdir(exist_ok=True)
                print("OUTPUT y PREVIEWS limpiados.")
            except Exception as e:
                print(f"[ERROR] Limpiando carpetas: {e}")

        elif choice == "0":
            print("Saliendo…")
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    typer.run(main)
