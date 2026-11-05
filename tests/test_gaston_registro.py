"""Tests de caracterización de Gastón (T01-T04): registro de solicitudes.

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


def contar_solicitudes(archivo_datos: Path) -> int:
    datos = json.loads(archivo_datos.read_text(encoding="utf-8"))
    return len(datos["solicitudes"])


def leer_solicitud_por_indice(archivo_datos: Path, indice: int) -> dict:
    datos = json.loads(archivo_datos.read_text(encoding="utf-8"))
    return datos["solicitudes"][indice]


def test_registrar_solicitud_valida(tmp_path):
    """T01: Registrar una solicitud válida con legajo existente: se crea en estado PENDIENTE."""
    # Arrange
    archivo = copiar_datos(tmp_path)
    cantidad_inicial = contar_solicitudes(archivo)

    # Act: Registrar con legajo existente (10001), tipo CERTIFICADO, descripción y prioridad default
    salida = ejecutar_sistema(["1", "10001", "1", "Certificado para presentar", "", "0"], archivo)

    # Assert
    assert "Solicitud #" in salida
    assert "registrada correctamente" in salida
    assert "Estado: PENDIENTE" in salida
    cantidad_final = contar_solicitudes(archivo)
    assert cantidad_final == cantidad_inicial + 1
    nueva = leer_solicitud_por_indice(archivo, -1)
    assert nueva["estado"] == "PENDIENTE"
    assert nueva["tipo"] == "CERTIFICADO"
    assert nueva["descripcion"] == "Certificado para presentar"


def test_registrar_sin_descripcion(tmp_path):
    """T02: Registrar sin descripción: el sistema rechaza la solicitud."""
    # Arrange
    archivo = copiar_datos(tmp_path)
    cantidad_inicial = contar_solicitudes(archivo)

    # Act: Intentar registrar sin descripción (vacío)
    salida = ejecutar_sistema(["1", "10001", "1", "", "0"], archivo)

    # Assert
    assert "Error: la descripcion no puede estar vacia" in salida
    cantidad_final = contar_solicitudes(archivo)
    assert cantidad_final == cantidad_inicial  # No se creó


def test_registrar_con_legajo_inexistente(tmp_path):
    """T03: Registrar con legajo inexistente (pero datos válidos): se crea la solicitud."""
    # Arrange
    archivo = copiar_datos(tmp_path)
    cantidad_inicial = contar_solicitudes(archivo)

    # Act: Legajo inexistente (99999), ingresar datos del estudiante
    salida = ejecutar_sistema(
        ["1", "99999", "Juan", "Perez", "juan.perez@ejemplo.edu", "Tecnicatura", "1", "Certificado", "", "0"],
        archivo,
    )

    # Assert
    assert "El estudiante no esta registrado" in salida
    assert "Solicitud #" in salida
    assert "registrada correctamente" in salida
    cantidad_final = contar_solicitudes(archivo)
    assert cantidad_final == cantidad_inicial + 1
    nueva = leer_solicitud_por_indice(archivo, -1)
    assert nueva["estudiante"]["legajo"] == "99999"
    assert nueva["estado"] == "PENDIENTE"


def test_listar_todas_las_solicitudes(tmp_path):
    """T04: Listar todas: aparecen todas las solicitudes cargadas."""
    # Arrange
    archivo = copiar_datos(tmp_path)
    cantidad = contar_solicitudes(archivo)

    # Act: Opción 6 (listar todas)
    salida = ejecutar_sistema(["6", "0"], archivo)

    # Assert: Debe mostrar la tabla con solicitudes
    assert "Listado de solicitudes" in salida
    # Verificar que aparecen los IDs de las solicitudes
    assert "#1" in salida
    assert f"Total: {cantidad}" in salida
