"""Tests unitarios de los enums TipoSolicitud y Prioridad (S05, paso 1)."""

import pytest

from modelos.prioridad import Prioridad
from modelos.tipo_solicitud import TipoSolicitud


@pytest.mark.parametrize(
    "opcion, esperado",
    [
        ("1", TipoSolicitud.CERTIFICADO),
        ("2", TipoSolicitud.CAMBIO_COMISION),
        ("3", TipoSolicitud.REVISION_NOTA),
        ("4", TipoSolicitud.EQUIVALENCIA),
        ("5", TipoSolicitud.OTRO),
    ],
)
def test_from_opcion_menu_reconoce_las_cinco_opciones(opcion, esperado):
    assert TipoSolicitud.from_opcion_menu(opcion) == esperado


@pytest.mark.parametrize("opcion_invalida", ["0", "6", "01", " 1", "1.0", "", "abc"])
def test_from_opcion_menu_rechaza_opciones_invalidas(opcion_invalida):
    with pytest.raises(ValueError):
        TipoSolicitud.from_opcion_menu(opcion_invalida)


@pytest.mark.parametrize(
    "tipo, prioridad_esperada",
    [
        (TipoSolicitud.CERTIFICADO, Prioridad.BAJA),
        (TipoSolicitud.CAMBIO_COMISION, Prioridad.ALTA),
        (TipoSolicitud.REVISION_NOTA, Prioridad.ALTA),
        (TipoSolicitud.EQUIVALENCIA, Prioridad.MEDIA),
        (TipoSolicitud.OTRO, Prioridad.BAJA),
    ],
)
def test_prioridad_por_defecto_por_tipo(tipo, prioridad_esperada):
    assert tipo.prioridad_por_defecto() == prioridad_esperada


@pytest.mark.parametrize(
    "texto, esperado",
    [("ALTA", Prioridad.ALTA), ("media", Prioridad.MEDIA), (" Baja ", Prioridad.BAJA)],
)
def test_prioridad_from_str_normaliza(texto, esperado):
    assert Prioridad.from_str(texto) == esperado


def test_prioridad_from_str_invalida():
    with pytest.raises(ValueError):
        Prioridad.from_str("URGENTE")
