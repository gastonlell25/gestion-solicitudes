"""Test de caracterizacion de S06: normalizacion de estado/prioridad al cargar datos.

data/solicitudes.json trae a proposito variantes de mayusculas/minusculas (solicitud #3
con estado "pendiente", #6 y #10 con prioridad "Alta"/"media"). proc() debe normalizarlas
usando Estado y Prioridad antes de mostrarlas.
"""

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


def test_estado_y_prioridad_con_minusculas_se_muestran_normalizados(tmp_path):
    archivo = copiar_datos(tmp_path)

    salida = ejecutar_sistema(["6", "0"], archivo)

    # Solicitud #3: estado "pendiente" en el archivo -> debe verse "PENDIENTE"
    assert "#3 [PENDIENTE] REVISION_NOTA - Prioridad: ALTA" in salida
    # Solicitud #6: prioridad "Alta" en el archivo -> debe verse "ALTA"
    assert "#6 [PENDIENTE] REVISION_NOTA - Prioridad: ALTA" in salida
    # Solicitud #10: prioridad "media" en el archivo -> debe verse "MEDIA"
    assert "#10 [PENDIENTE] CERTIFICADO - Prioridad: MEDIA" in salida
