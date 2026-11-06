"""Regresiones de S07–S09: filtros, reglas de vencimiento y reporte.

Tests adicionales a T10–T15, sin escribir en el JSON del repositorio.
"""
from datetime import date

import pytest

from gestor_solicitudes import GestorSolicitudes
from modelos.estudiante import Estudiante
from modelos.solicitud import Solicitud
from servicios.reporte_service import ReporteService


def solicitud(*, prioridad="ALTA", estado="PENDIENTE", creada="2026-10-20", legajo="10001"):
    estudiante = Estudiante(legajo, "Ana", "Suárez", "ejemplo@edu.test", "TUP")
    return Solicitud(1, estudiante, "CERTIFICADO", "Ejemplo", prioridad, estado, None,
                     creada, creada)


@pytest.mark.parametrize("prioridad,dias,esperado", [
    ("ALTA", 3, False), ("ALTA", 4, True),
    ("MEDIA", 7, False), ("MEDIA", 8, True),
    ("BAJA", 15, False), ("BAJA", 16, True),
    ("OTRA", 30, False),
])
def test_plazos_estrictos_de_vencimiento(prioridad, dias, esperado):
    s = solicitud(prioridad=prioridad)
    referencia = date(2026, 10, 20).toordinal() + dias
    assert s.dias_desde_creacion(date.fromordinal(referencia).isoformat()) == dias
    assert s.esta_vencida(date.fromordinal(referencia).isoformat()) is esperado


@pytest.mark.parametrize("estado", ["APROBADA", "RECHAZADA", "CERRADA"])
def test_estados_resueltos_nunca_vencen(estado):
    s = solicitud(estado=estado)
    assert s.esta_vencida("2026-12-01") is False


def test_filtrado_conserva_semantica_de_texto():
    gestor = GestorSolicitudes()
    gestor.lst = [solicitud(legajo="Abc"), solicitud(legajo="abc")]
    assert gestor.filtrar_por_tipo(" certificado ") == gestor.lst
    assert gestor.filtrar_por_estado(" pendiente ") == gestor.lst
    assert gestor.filtrar_por_prioridad(" alta ") == gestor.lst
    assert gestor.filtrar_por_legajo(" Abc ") == gestor.lst[:1]
    assert gestor.filtrar_por_legajo(" ABC ") == []


def test_reporte_service_retorna_texto_y_no_imprime(capsys):
    s = solicitud()
    texto = ReporteService.generar([s], "2026-10-20")
    assert "Total de solicitudes: 1" in texto
    assert "Pendientes de prioridad ALTA: 1" in texto
    assert "Solicitudes vencidas: 0" in texto
    assert "CERTIFICADO: 1" in texto
    assert capsys.readouterr().out == ""
