# pdf-ocr-stamper

Sellado de firma en PDFs con:
- `manifest.csv` por archivo
- Reglas (`rules.yaml`): anclajes por texto (regex), posiciones relativas, detección de líneas
- `--dry-run`: genera JPGs de previsualización sin tocar PDFs
- Log CSV con estrategia usada por página

## Uso rápido

```bash
# Previsualización
python -m pdf_ocr_stamper.cli -c config/config.yaml -m manifest.csv --rules rules.yaml --dry-run

# Sellado real
python -m pdf_ocr_stamper.cli -c config/config.yaml -m manifest.csv --rules rules.yaml
```
