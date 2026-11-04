"""Tests de caracterización de Fabri (T16–T19): asignación de responsables y persistencia.

Son de punta a punta: ejecutan src/main.py simulando la entrada del menú y verifican la salida
y el archivo de datos. No dependen de métodos internos, así siguen valiendo después del refactoring.
Cada test trabaja sobre una copia de los datos en un directorio temporal.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATOS_ORIGINALES = RAIZ / "data" / "solicitudes.json"
FECHA_FIJA = "2026-10-30"


def ejecutar_sistema(entradas: list[str], archivo_datos: Path) -> str:
    entorno = dict(os.environ, FECHA_HOY=FECHA_FIJA, ARCHIVO_DATOS=str(archivo_datos))
    resultado = subprocess.run(
        [sys.executable, str(RAIZ / "src" / "main.py")],
        input="\n".join(entradas) + "\n",
        capture_output=True,
        text=True,
        env=entorno,
        cwd=RAIZ,
        timeout=10,
    )
    return resultado.stdout


def copiar_datos(tmp_path: Path) -> Path:
    destino = tmp_path / "solicitudes.json"
    shutil.copy(DATOS_ORIGINALES, destino)
    return destino


def leer_solicitud(archivo_datos: Path, id_solicitud: int) -> dict:
    datos = json.loads(archivo_datos.read_text(encoding="utf-8"))
    return next(s for s in datos["solicitudes"] if s["id"] == id_solicitud)
