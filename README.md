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

# Instalación
1. Tesseract
1.1 Descargar e instalar tesseract desde https://github.com/UB-Mannheim/tesseract/wiki.
-> Tesseract installer for Windows -> tesseract-ocr-w64-setup-5.5.0.20241111.exe (64 bit) -> https://github.com/tesseract-ocr/tesseract/releases/download/5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe

1.2 Durante la instalación, en el apartado de "Seleccion de componentes", marcamos "Aditional languaje data (download)" y seleccionamos "Spanish"

1.3 Agregamos Tesseract a las variables de entorno:
1.3.1 Variables del sistema
1.3.1.1 Seleccionamos "Path" -> "Editar" -> Nuevo | Agregamos "C:\Program Files\Tesseract-OCR\" (Sin las comillas)
1.3.1.2 Click en "Nueva..." -> Agregamos en Nombre de la variable: TESSDATA_PREFIX | Valor de la variable: C:\Program Files\Tesseract-OCR\tessdata

1.3 Verificacmos desde la consola de windows:
1.3.1 Verificacmos la instalacion: tesseract --version
1.3.2 Verificamos el lenguaje (debe estar presente apa): tesseract --list-langs

# Development
1. Clonar el repositorio
2. Crear/activae el entorno virtual venv:
python -m venv .venv
call .venv\Scripts\activate
3. Instalar dependencias:
pip install -r requirements.txt
4. Ejecutar run.bat o run-preview.bat


## 📦 Instalación

## 1. Instalar Tesseract OCR

1. Descargar e instalar Tesseract desde la página oficial (Tesseract installer for Windows -> tesseract-ocr-w64-setup-5.5.0.20241111.exe (64 bit)):  
   👉 [Tesseract installer for Windows (64 bit)](https://github.com/tesseract-ocr/tesseract/releases/download/5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe)  
   Fuente: [Wiki UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki).

2. Durante la instalación:
   - En **Selección de componentes**, marcar **Additional language data (download)**.
   - Seleccionar el idioma **Spanish**.

3. Agregar Tesseract a las variables de entorno de Windows:
   - Abrir **Variables de entorno** → En **Variables del sistema**:
     1. Editar la variable `Path` y agregar:
        ```
        C:\Program Files\Tesseract-OCR\
        ```
     2. Crear una nueva variable:
        - **Nombre**: `TESSDATA_PREFIX`
        - **Valor**: `C:\Program Files\Tesseract-OCR\tessdata`

4. Verificar la instalación en la consola de Windows (CMD o PowerShell):
   ```bash
   tesseract --version
   tesseract --list-langs

# Development

1. Clonar el repositorio:
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    ```
2. Crear/activae el entorno virtual venv:
    ```bash
    python -m venv .venv
    call .venv\Scripts\activate
    ```
3. Instalar dependencias:
    ```bash
    pip install -r requirements.txt
    ```
4. Ejecutar 
    ```bash
    run.bat o run-preview.bat
    ```

# Configuración:

1. La firma se debe agregar a config/firma.png
2. los archivos a firma deben agregarse a input/
3. Los archivos firmados se agregan a output/
4. Los archivos de muestra generados mediante run-preview.bat se generan en previews/
5. Las regla de configuración debe realizarse en rules.yaml 