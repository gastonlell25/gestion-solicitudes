"""T10–T15: pruebas de caracterización de filtros y reporte (Juan).

Se ejercita la interfaz de consola sin importar funciones del sistema. Cada caso
utiliza una copia temporal del JSON y una fecha fija para poder comparar el
comportamiento inicial con la versión refactorizada.
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATOS_INICIALES = RAIZ / "data" / "solicitudes.json"
FECHA_FIJA = "2026-10-30"


def ejecutar_sistema(entradas: list[str], datos: Path) -> str:
    entorno = dict(os.environ, ARCHIVO_DATOS=str(datos), FECHA_HOY=FECHA_FIJA)
    resultado = subprocess.run(
        [sys.executable, str(RAIZ / "src" / "main.py")],
        input="\n".join(entradas) + "\n",
        text=True,
        capture_output=True,
        cwd=RAIZ,
        env=entorno,
        timeout=10,
        check=False,
    )
    assert resultado.returncode == 0, resultado.stderr
    return resultado.stdout


def preparar_datos(tmp_path: Path) -> Path:
    archivo = tmp_path / "solicitudes.json"
    shutil.copyfile(DATOS_INICIALES, archivo)
    return archivo


def ids_mostrados(salida: str) -> list[int]:
    """IDs de resultados visibles por consola (sin acoplarse al gestor)."""
    return [int(valor) for valor in re.findall(r"(?m)^#(\d+) \[", salida)]


def test_t10_filtrar_por_estado(tmp_path):
    """T10: PENDIENTE muestra las cinco solicitudes, incluso datos normalizados."""
    datos = preparar_datos(tmp_path)
    salida = ejecutar_sistema(["4", "1", "PENDIENTE", "0"], datos)
    assert "Se encontraron 5 solicitud(es):" in salida
    assert ids_mostrados(salida) == [1, 3, 6, 8, 10]


def test_t11_filtrar_por_tipo(tmp_path):
    """T11: CERTIFICADO devuelve solo las tres solicitudes de ese tipo."""
    datos = preparar_datos(tmp_path)
    salida = ejecutar_sistema(["4", "2", "CERTIFICADO", "0"], datos)
    assert "Se encontraron 3 solicitud(es):" in salida
    assert ids_mostrados(salida) == [1, 5, 10]


def test_t12_filtrar_por_prioridad(tmp_path):
    """T12: ALTA incluye los registros normalizados a esa prioridad."""
    datos = preparar_datos(tmp_path)
    salida = ejecutar_sistema(["4", "3", "ALTA", "0"], datos)
    assert "Se encontraron 4 solicitud(es):" in salida
    assert ids_mostrados(salida) == [2, 3, 6, 8]


def test_t13_filtrar_por_legajo(tmp_path):
    """T13: el legajo 10001 tiene exactamente dos solicitudes."""
    datos = preparar_datos(tmp_path)
    salida = ejecutar_sistema(["4", "4", "10001", "0"], datos)
    assert "Se encontraron 2 solicitud(es):" in salida
    assert ids_mostrados(salida) == [1, 6]
    assert salida.count("Estudiante: 10001") == 2


def test_t14_busqueda_sin_resultados(tmp_path):
    """T14: un legajo sin solicitudes muestra un aviso, sin resultados listados."""
    datos = preparar_datos(tmp_path)
    salida = ejecutar_sistema(["4", "4", "99999", "0"], datos)
    assert "No se encontraron solicitudes." in salida
    assert ids_mostrados(salida) == []


def test_t15_reporte_basico_conteos(tmp_path):
    """T15: se verifican todos los conteos observables del reporte original."""
    datos = preparar_datos(tmp_path)
    salida = ejecutar_sistema(["5", "0"], datos)
    assert "============ REPORTE ============" in salida
    for texto in (
        "Total de solicitudes: 10",
        "PENDIENTE: 5",
        "EN_REVISION: 2",
        "APROBADA: 1",
        "RECHAZADA: 1",
        "CERRADA: 1",
        "CERTIFICADO: 3",
        "CAMBIO_COMISION: 2",
        "REVISION_NOTA: 2",
        "EQUIVALENCIA: 2",
        "OTRO: 1",
        "Pendientes de prioridad ALTA: 3",
        "Solicitudes vencidas: 3",
    ):
        assert texto in salida, f"Faltó el dato de reporte: {texto}"
