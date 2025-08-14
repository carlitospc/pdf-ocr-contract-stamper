@echo off
setlocal
cd /d "%~dp0"
set PYTHONPATH=%CD%\src;%PYTHONPATH%

REM Previsualización SIEMPRE (no modifica PDFs)
python -m pdf_ocr_stamper.cli -c config\config.yaml -m manifest.csv --rules rules.yaml --dry-run %*
pause
