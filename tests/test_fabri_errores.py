"""Tests de los dos bugs del sistema base corregidos en el refactoring de S11 (Fabri).

En estado-inicial: (1) un archivo de datos dañado se reemplazaba sin aviso por los datos de
ejemplo, y (2) si el archivo no se podía escribir, se mostraba el error técnico y enseguida
un mensaje de éxito. Son de punta a punta, como T16–T19.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from persistencia.solicitud_repositorio import PersistenciaException
from persistencia.solicitud_repositorio_archivo import SolicitudRepositorioArchivo

RAIZ = Path(__file__).resolve().parent.parent
DATOS_ORIGINALES = RAIZ / "data" / "solicitudes.json"


def ejecutar_sistema(entradas: list[str], archivo_datos: Path) -> str:
    entorno = dict(os.environ, FECHA_HOY="2026-10-30", ARCHIVO_DATOS=str(archivo_datos))
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


def test_archivo_danado_no_se_sobrescribe_y_se_informa(tmp_path):
    # Arrange
    archivo = tmp_path / "solicitudes.json"
    archivo.write_text("{ esto no es json", encoding="utf-8")

    # Act
    salida = ejecutar_sistema(["6", "0"], archivo)

    # Assert
    assert "tiene un formato invalido (linea 1, columna 3)" in salida
    assert "El archivo no se modifico." in salida
    assert archivo.read_text(encoding="utf-8") == "{ esto no es json"


def test_archivo_sin_un_campo_obligatorio_lanza_persistencia_exception(tmp_path, monkeypatch):
    # Arrange
    archivo = tmp_path / "solicitudes.json"
    archivo.write_text(json.dumps({"estudiantes": []}), encoding="utf-8")
    monkeypatch.setenv("ARCHIVO_DATOS", str(archivo))

    # Act / Assert
    with pytest.raises(PersistenciaException, match="falta el dato 'responsables'"):
        SolicitudRepositorioArchivo().cargar()


@pytest.mark.skipif(hasattr(os, "geteuid") and os.geteuid() == 0, reason="root puede escribir igual")
def test_si_no_se_puede_guardar_no_informa_exito_ni_conserva_el_cambio(tmp_path):
    # Arrange
    archivo = tmp_path / "solicitudes.json"
    shutil.copy(DATOS_ORIGINALES, archivo)
    archivo.chmod(0o444)

    # Act: asignar responsable a la #1 y después listar
    try:
        salida = ejecutar_sistema(["3", "1", "1", "6", "0"], archivo)
    finally:
        archivo.chmod(0o644)

    # Assert
    assert "no se pudo guardar el archivo de datos" in salida
    assert "La operacion no se guardo." in salida
    assert "Responsable asignado" not in salida
    listado_solicitud_1 = salida.split("#1 [")[1].split("#2 [")[0]
    assert "Responsable: Sin asignar" in listado_solicitud_1
