"""Tests unitarios del repositorio de solicitudes (Fabri, Fase 3).

Complementan a T16–T19, que prueban la persistencia de punta a punta. Acá se prueba el
repositorio por separado y que el gestor funcione con cualquier implementación de
SolicitudRepositorio (DIP), por ejemplo una en memoria que no toca ningún archivo.
"""
import json

import pytest

from gestor_solicitudes import GestorSolicitudes
from modelos.estudiante import Estudiante
from modelos.responsable import Responsable
from modelos.solicitud import Solicitud
from persistencia.datos_sistema import DatosSistema
from persistencia.solicitud_repositorio import SolicitudRepositorio
from persistencia.solicitud_repositorio_archivo import SolicitudRepositorioArchivo


class RepositorioEnMemoria(SolicitudRepositorio):
    def __init__(self, datos: DatosSistema):
        self.datos = datos
        self.guardados: list[DatosSistema] = []

    def cargar(self) -> DatosSistema:
        return self.datos

    def guardar(self, datos: DatosSistema) -> bool:
        self.guardados.append(datos)
        return True


def crear_datos() -> DatosSistema:
    estudiante = Estudiante("20001", "Ana", "Paz", "ana.paz@ejemplo.edu", "TUP")
    responsable = Responsable(1, "Laura Quiroga", "Alumnado")
    solicitud = Solicitud(
        1, estudiante, "CERTIFICADO", "Constancia", "BAJA", "PENDIENTE", None,
        "2026-10-20", "2026-10-20",
    )
    return DatosSistema([estudiante], [responsable], [solicitud])


@pytest.fixture
def archivo_temporal(tmp_path, monkeypatch):
    archivo = tmp_path / "datos.json"
    monkeypatch.setenv("ARCHIVO_DATOS", str(archivo))
    return archivo


def test_solicitud_repositorio_es_abstracto():
    with pytest.raises(TypeError):
        SolicitudRepositorio()


def test_repositorio_archivo_guardar_y_cargar_conserva_los_datos(archivo_temporal):
    # Arrange
    repositorio = SolicitudRepositorioArchivo()
    datos = crear_datos()
    datos.solicitudes[0].responsable = datos.responsables[0]

    # Act
    repositorio.guardar(datos)
    recuperados = SolicitudRepositorioArchivo().cargar()

    # Assert
    solicitud = recuperados.solicitudes[0]
    assert solicitud.id == 1
    assert solicitud.estudiante.legajo == "20001"
    assert solicitud.responsable.nombre == "Laura Quiroga"
    assert [r.area for r in recuperados.responsables] == ["Alumnado"]


def test_repositorio_archivo_inexistente_devuelve_datos_de_ejemplo_y_crea_el_archivo(archivo_temporal):
    # Act
    datos = SolicitudRepositorioArchivo().cargar()

    # Assert
    assert len(datos.solicitudes) == 10
    assert len(json.loads(archivo_temporal.read_text(encoding="utf-8"))["solicitudes"]) == 10


def test_gestor_funciona_con_un_repositorio_en_memoria():
    # Arrange
    repositorio = RepositorioEnMemoria(crear_datos())
    gestor = GestorSolicitudes(repositorio)

    # Act
    gestor.cargar()
    gestor.guardar()

    # Assert
    assert gestor.buscar("1").descripcion == "Constancia"
    assert repositorio.guardados[-1].solicitudes[0].id == 1
