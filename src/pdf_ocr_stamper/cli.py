import typer
from pdf_ocr_stamper.config_loader import load_config
from pdf_ocr_stamper.pipeline import process_batch

def main(
    config: str = typer.Option("config/config.yaml", "--config", "-c"),
    manifest: str = typer.Option(None, "--manifest", "-m"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    rules: str = typer.Option(None, "--rules", help="Ruta a rules.yaml"),
    outlog: str = typer.Option("output/placement_log.csv", "--outlog", help="CSV con estrategia usada")
):
    cfg = load_config(config)
    if manifest:
        cfg["manifest_csv"] = manifest
    cfg["dry_run"] = dry_run
    if rules:
        cfg["rules_yaml"] = rules
    cfg["outlog"] = outlog
    process_batch(cfg)

if __name__ == "__main__":
    typer.run(main)
