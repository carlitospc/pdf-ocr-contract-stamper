@echo off
setlocal
REM Asegura que se ejecuta desde la carpeta del proyecto
cd /d "%~dp0"

REM Agrega 'src' al PYTHONPATH para que 'python -m pdf_ocr_stamper.cli' encuentre el paquete
set PYTHONPATH=%CD%\src;%PYTHONPATH%

REM Ejecuta con config.yaml, manifest.csv y rules.yaml (permite flags extra con %*)
python -m pdf_ocr_stamper.cli -c config\config.yaml -m manifest.csv --rules rules.yaml %*
pause
