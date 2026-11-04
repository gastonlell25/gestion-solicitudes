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


def test_asignar_responsable_valido_asigna_y_guarda(tmp_path):
    """T16: asignar a la solicitud #1 el responsable 1 (Alumnado)."""
    # Arrange
    archivo = copiar_datos(tmp_path)

    # Act
    salida = ejecutar_sistema(["3", "1", "1", "0"], archivo)

    # Assert
    assert "Responsable asignado: Laura Quiroga (Alumnado) -> solicitud #1" in salida
    assert leer_solicitud(archivo, 1)["responsable"]["id"] == 1


def test_asignar_responsable_inexistente_muestra_error_y_no_modifica(tmp_path):
    """T17: asignar a la solicitud #1 un responsable que no existe (ID 9)."""
    # Arrange
    archivo = copiar_datos(tmp_path)
    responsable_previo = leer_solicitud(archivo, 1)["responsable"]

    # Act
    salida = ejecutar_sistema(["3", "1", "9", "0"], archivo)

    # Assert
    assert "Error: no existe un responsable con ID 9." in salida
    assert leer_solicitud(archivo, 1)["responsable"] == responsable_previo


def test_persistencia_al_reabrir_conserva_solicitud_y_responsable(tmp_path):
    """T18: se registra la #11 y se le asigna responsable; al reabrir el programa sigue estando."""
    # Arrange
    archivo = copiar_datos(tmp_path)
    primera_sesion = [
        "1", "10003", "4", "Equivalencia de Fisica I aprobada en otra facultad", "",
        "3", "11", "2",
        "0",
    ]
    ejecutar_sistema(primera_sesion, archivo)

    # Act
    salida = ejecutar_sistema(["6", "0"], archivo)

    # Assert
    assert "#11 [PENDIENTE] EQUIVALENCIA - Prioridad: MEDIA" in salida
    assert "Responsable: Martin Ferreyra (Secretaria Academica)" in salida
    assert "Total: 11 solicitud(es)." in salida
