# launcher.py
import typer
from pdf_ocr_stamper.cli import main as app_main

if __name__ == "__main__":
    # esto emula `python -m pdf_ocr_stamper.cli`
    typer.run(app_main)
