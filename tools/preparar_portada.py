r"""Copia la portada oficial y actualiza el título de la práctica."""
import shutil
from pathlib import Path

from docx import Document

plantilla = Path(r"C:\Users\moral\Documents\Plantillas\PORTADA.docx")
destino = Path(__file__).resolve().parents[1] / "PORTADA_POKEDEX.docx"

shutil.copy2(plantilla, destino)
doc = Document(destino)
nuevo = "“Práctica 2: Pokédex mínima en Flutter”"

for parrafo in doc.paragraphs:
    if "Consulta de estudiantes con Cubit" in parrafo.text:
        if parrafo.runs:
            parrafo.runs[0].text = nuevo
            for run in parrafo.runs[1:]:
                run.text = ""
        else:
            parrafo.text = nuevo
        break
else:
    raise SystemExit("No se encontró el título original en la portada")

doc.save(destino)
print(destino)
