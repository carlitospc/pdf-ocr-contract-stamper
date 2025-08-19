@echo off
REM ============================================
REM Script para ejecutar PDF OCR Contract Stamper
REM ============================================

cd /d "%~dp0"

echo Ejecutando pdf-ocr-stamper...

.\pdf-ocr-stamper.exe --config config\config.yaml

echo.
echo Proceso terminado.
pause
