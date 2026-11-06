"""Cálculo del reporte de solicitudes, independiente de la consola y persistencia.

La salida de texto preserva el formato original para los tests de caracterización.
"""
from collections import Counter


class ReporteService:
    ESTADOS = ("PENDIENTE", "EN_REVISION", "APROBADA", "RECHAZADA", "CERRADA")
    TIPOS = ("CERTIFICADO", "CAMBIO_COMISION", "REVISION_NOTA", "EQUIVALENCIA", "OTRO")

    @classmethod
    def generar(cls, solicitudes, fecha_referencia):
        conteo_estados = Counter(s.estado for s in solicitudes)
        conteo_tipos = Counter(s.tipo for s in solicitudes)
        pendientes_alta = sum(
            1 for s in solicitudes if s.estado[:4] == "PEND" and s.prioridad.upper() == "ALTA"
        )
        vencidas = sum(1 for s in solicitudes if s.esta_vencida(fecha_referencia))
        lineas = [
            "============ REPORTE ============",
            f"Total de solicitudes: {len(solicitudes)}",
            "",
            "Cantidad por estado:",
        ]
        lineas.extend(f"  {estado}: {conteo_estados[estado]}" for estado in cls.ESTADOS)
        lineas.extend(("", "Cantidad por tipo:"))
        lineas.extend(f"  {tipo}: {conteo_tipos[tipo]}" for tipo in cls.TIPOS)
        lineas.extend((
            "",
            f"Pendientes de prioridad ALTA: {pendientes_alta}",
            f"Solicitudes vencidas: {vencidas}",
            "=================================",
        ))
        return "\n".join(lineas)
