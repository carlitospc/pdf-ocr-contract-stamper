@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM build.bat - Compila pdf-ocr-stamper (onedir -> onefile)
REM Requisitos: Windows + Python 3.x instalado
REM Estructura del proyecto: src/pdf_ocr_stamper/cli.py
REM Dependencias: requirements.txt + requirements-dev.txt
REM ============================================================

REM Ir a la carpeta donde está este .bat
cd /d "%~dp0"

echo.
echo === [1/7] Preparando entorno virtual (.venv) ===========================
REM Si quieres conservación del venv, comenta las 2 lineas siguientes
IF EXIST ".venv" (
  echo Eliminando venv anterior...
  rmdir /s /q .venv
)

echo Creando venv...
py -3 -m venv .venv || (echo ERROR: No se pudo crear el venv & goto :fail)

echo Activando venv...
call .venv\Scripts\activate || (echo ERROR: No se pudo activar el venv & goto :fail)

echo Actualizando pip/setuptools/wheel...
python -m pip install -U pip setuptools wheel || goto :fail

echo.
echo === [2/7] Instalando dependencias de desarrollo ========================
IF NOT EXIST requirements-dev.txt (
  echo ERROR: requirements-dev.txt no existe. & goto :fail
)
python -m pip install -r requirements-dev.txt || goto :fail

echo.
echo === [3/7] Limpiando artefactos previos =================================
IF EXIST build  rmdir /s /q build
IF EXIST dist   rmdir /s /q dist
IF EXIST pdf-ocr-stamper.spec del /q pdf-ocr-stamper.spec

echo.
echo === [5/7] Compilando en ONEDIR (prueba rapida) =========================
REM Usamos PyInstaller del venv y explicitamos --paths src por layout src/
".venv\Scripts\pyinstaller.exe" ^
  src\pdf_ocr_stamper\cli.py ^
  --name pdf-ocr-stamper ^
  --onedir ^
  --console ^
  --paths src ^
  --hidden-import=typer ^
  --hidden-import=click ^
  --collect-submodules pdf_ocr_stamper ^
  --clean
IF ERRORLEVEL 1 goto :fail

echo.
echo === [6/7] Prueba de ejecucion ONEDIR ==================================
IF EXIST "dist\pdf-ocr-stamper\pdf-ocr-stamper.exe" (
  echo Ejecutable de prueba generado: dist\pdf-ocr-stamper\pdf-ocr-stamper.exe
  echo ^(Opcional^) Prueba rapida:
  echo     dist\pdf-ocr-stamper\pdf-ocr-stamper.exe --config config\config.yaml
) ELSE (
  echo ERROR: No se genero el binario ONEDIR.
  goto :fail
)

echo.
echo === [7/7] Compilando en ONEFILE (final) ================================
REM Limpiamos dist/build/spec para un onefile limpio
IF EXIST build  rmdir /s /q build
IF EXIST dist   rmdir /s /q dist
IF EXIST pdf-ocr-stamper.spec del /q pdf-ocr-stamper.spec

".venv\Scripts\pyinstaller.exe" ^
  src\pdf_ocr_stamper\cli.py ^
  --name pdf-ocr-stamper ^
  --onefile ^
  --console ^
  --paths src ^
  --hidden-import=typer ^
  --hidden-import=click ^
  --collect-submodules pdf_ocr_stamper ^
  --clean
IF ERRORLEVEL 1 goto :fail

echo.
echo ============================================================
echo   EXITO: Ejecutable final en: dist\pdf-ocr-stamper.exe
echo ------------------------------------------------------------
echo   Recuerda: DEJA recursos por fuera del .exe
echo   Estructura recomendada para ejecutar:
echo     pdf-ocr-stamper.exe
echo     rules.yaml
echo     config\config.yaml
echo     config\firma.png
echo     input\
echo     output\
echo     previews\
echo ------------------------------------------------------------
echo   Ejecutar:
echo     .\pdf-ocr-stamper.exe --config config\config.yaml
echo ============================================================
goto :end

:fail
echo.
echo *** BUILD FALLIDO ***
echo Revisa el error anterior. Sugerencias:
echo  - Asegurate de que src\pdf_ocr_stamper\cli.py existe.
echo  - Verifica que requirements-dev.txt incluye PyInstaller.
echo  - Comprueba que "python -c ^"import pdf_ocr_stamper^"" funciona.
echo  - Si cambiaste dependencias, borra build/dist/spec e intenta de nuevo.
exit /b 1

:end
endlocal
