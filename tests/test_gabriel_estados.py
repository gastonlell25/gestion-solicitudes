"""Tests de caracterización de Gabriel (T05-T09): transiciones de estado.

Son de punta a punta: ejecutan src/main.py simulando la entrada del menu y verifican la
salida y el archivo de datos. No dependen de metodos internos, asi siguen valiendo
despues del refactoring. Cada test trabaja sobre una copia de los datos en un
directorio temporal.
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


def test_pendiente_a_en_revision_es_valido(tmp_path):
    """T05: la solicitud #1 (PENDIENTE) pasa a EN_REVISION."""
    # Arrange
    archivo = copiar_datos(tmp_path)

    # Act
    salida = ejecutar_sistema(["2", "1", "EN_REVISION", "0"], archivo)

    # Assert
    assert "Estado actualizado: PENDIENTE -> EN_REVISION" in salida
    assert leer_solicitud(archivo, 1)["estado"] == "EN_REVISION"


def test_en_revision_a_aprobada_es_valido(tmp_path):
    """T06: la solicitud #2 (EN_REVISION) pasa a APROBADA."""
    # Arrange
    archivo = copiar_datos(tmp_path)

    # Act
    salida = ejecutar_sistema(["2", "2", "APROBADA", "0"], archivo)

    # Assert
    assert "Estado actualizado: EN_REVISION -> APROBADA" in salida
    assert leer_solicitud(archivo, 2)["estado"] == "APROBADA"


def test_cerrada_a_pendiente_es_rechazado(tmp_path):
    """T07: la solicitud #5 (CERRADA) no puede volver a PENDIENTE."""
    # Arrange
    archivo = copiar_datos(tmp_path)

    # Act
    salida = ejecutar_sistema(["2", "5", "PENDIENTE", "0"], archivo)

    # Assert
    assert "Error: no se puede pasar de CERRADA a PENDIENTE." in salida
    assert leer_solicitud(archivo, 5)["estado"] == "CERRADA"


def test_aprobada_a_pendiente_es_rechazado(tmp_path):
    """T08: la solicitud #4 (APROBADA) no puede volver a PENDIENTE."""
    # Arrange
    archivo = copiar_datos(tmp_path)

    # Act
    salida = ejecutar_sistema(["2", "4", "PENDIENTE", "0"], archivo)

    # Assert
    assert "Error: no se puede pasar de APROBADA a PENDIENTE." in salida
    assert leer_solicitud(archivo, 4)["estado"] == "APROBADA"


def test_aprobada_a_cerrada_es_valido(tmp_path):
    """T09: la solicitud #4 (APROBADA) pasa a CERRADA."""
    # Arrange
    archivo = copiar_datos(tmp_path)

    # Act
    salida = ejecutar_sistema(["2", "4", "CERRADA", "0"], archivo)

    # Assert
    assert "Estado actualizado: APROBADA -> CERRADA" in salida
    assert leer_solicitud(archivo, 4)["estado"] == "CERRADA"


# Casos adicionales pedidos en la revision de PR (Gaston): confirmar de punta a punta
# que "mismo estado", una regresion no listada explicitamente y un estado invalido
# tambien se comportan como espera la tabla de transiciones.


def test_mismo_estado_no_se_considera_error(tmp_path):
    """La solicitud #1 ya esta en PENDIENTE: pasar al mismo estado no es un error."""
    archivo = copiar_datos(tmp_path)

    salida = ejecutar_sistema(["2", "1", "PENDIENTE", "0"], archivo)

    assert "La solicitud ya se encuentra en estado PENDIENTE." in salida
    assert leer_solicitud(archivo, 1)["estado"] == "PENDIENTE"


def test_aprobada_a_en_revision_es_rechazado(tmp_path):
    """Una solicitud APROBADA no puede retroceder a EN_REVISION."""
    archivo = copiar_datos(tmp_path)

    salida = ejecutar_sistema(["2", "4", "EN_REVISION", "0"], archivo)

    assert "Error: no se puede pasar de APROBADA a EN_REVISION." in salida
    assert leer_solicitud(archivo, 4)["estado"] == "APROBADA"


def test_estado_invalido_muestra_error(tmp_path):
    """Un valor que no es ninguno de los 5 estados muestra el error correspondiente."""
    archivo = copiar_datos(tmp_path)

    salida = ejecutar_sistema(["2", "1", "INEXISTENTE", "0"], archivo)

    assert "Error: estado invalido." in salida
    assert leer_solicitud(archivo, 1)["estado"] == "PENDIENTE"
