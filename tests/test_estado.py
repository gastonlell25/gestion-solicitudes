"""Tests unitarios del enum Estado (paso 1 del refactoring de Gabriel).

No reemplazan a los tests de caracterizacion de tests/test_gabriel_estados.py (que
siguen probando el sistema de punta a punta); estos verifican directamente la tabla de
transiciones antes de conectarla con gestor_solicitudes.py.
"""

import pytest

from modelos.estado import Estado, EstadoInvalidoException, TransicionInvalidaException


@pytest.mark.parametrize(
    "texto, esperado",
    [
        ("PENDIENTE", Estado.PENDIENTE),
        ("en_revision", Estado.EN_REVISION),
        ("En Revision", Estado.EN_REVISION),
        (" aprobada ", Estado.APROBADA),
        ("RECHAZADA", Estado.RECHAZADA),
        ("Cerrada", Estado.CERRADA),
    ],
)
def test_from_str_normaliza_y_reconoce_estados_validos(texto, esperado):
    assert Estado.from_str(texto) == esperado


def test_from_str_con_valor_invalido_lanza_estado_invalido_exception():
    with pytest.raises(EstadoInvalidoException):
        Estado.from_str("INEXISTENTE")


def test_estado_invalido_exception_es_tambien_value_error():
    # Para que el codigo que ya capturaba ValueError no se rompa.
    assert issubclass(EstadoInvalidoException, ValueError)


@pytest.mark.parametrize(
    "actual, nuevo, permitido",
    [
        (Estado.PENDIENTE, Estado.EN_REVISION, True),
        (Estado.PENDIENTE, Estado.APROBADA, True),
        (Estado.PENDIENTE, Estado.RECHAZADA, True),
        (Estado.PENDIENTE, Estado.CERRADA, True),
        (Estado.EN_REVISION, Estado.PENDIENTE, True),
        (Estado.EN_REVISION, Estado.APROBADA, True),
        (Estado.EN_REVISION, Estado.RECHAZADA, True),
        (Estado.EN_REVISION, Estado.CERRADA, True),
        (Estado.APROBADA, Estado.CERRADA, True),
        (Estado.APROBADA, Estado.PENDIENTE, False),
        (Estado.APROBADA, Estado.EN_REVISION, False),
        (Estado.RECHAZADA, Estado.CERRADA, True),
        (Estado.RECHAZADA, Estado.PENDIENTE, False),
        (Estado.CERRADA, Estado.PENDIENTE, False),
        (Estado.CERRADA, Estado.EN_REVISION, False),
        (Estado.CERRADA, Estado.APROBADA, False),
        (Estado.CERRADA, Estado.RECHAZADA, False),
    ],
)
def test_puede_pasar_a_respeta_la_tabla_de_transiciones(actual, nuevo, permitido):
    assert actual.puede_pasar_a(nuevo) is permitido


def test_transicion_invalida_exception_es_una_excepcion_comun():
    assert issubclass(TransicionInvalidaException, Exception)


@pytest.mark.parametrize(
    "estado, es_final",
    [
        (Estado.PENDIENTE, False),
        (Estado.EN_REVISION, False),
        (Estado.APROBADA, False),
        (Estado.RECHAZADA, False),
        (Estado.CERRADA, True),
    ],
)
def test_es_final_solo_cerrada_no_tiene_transiciones_salientes(estado, es_final):
    assert estado.es_final() is es_final
