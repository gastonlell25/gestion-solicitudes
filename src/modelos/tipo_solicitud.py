from enum import Enum

from modelos.prioridad import Prioridad


class TipoSolicitud(Enum):
    CERTIFICADO = "CERTIFICADO"
    CAMBIO_COMISION = "CAMBIO_COMISION"
    REVISION_NOTA = "REVISION_NOTA"
    EQUIVALENCIA = "EQUIVALENCIA"
    OTRO = "OTRO"

    @classmethod
    def from_opcion_menu(cls, opcion: str) -> "TipoSolicitud":
        try:
            return cls(_OPCIONES_MENU[opcion])
        except KeyError:
            raise ValueError(f"Opcion de tipo invalida: {opcion!r}") from None

    def prioridad_por_defecto(self) -> Prioridad:
        return _PRIORIDAD_POR_DEFECTO[self]


_OPCIONES_MENU = {
    "1": "CERTIFICADO",
    "2": "CAMBIO_COMISION",
    "3": "REVISION_NOTA",
    "4": "EQUIVALENCIA",
    "5": "OTRO",
}

_PRIORIDAD_POR_DEFECTO = {
    TipoSolicitud.CERTIFICADO: Prioridad.BAJA,
    TipoSolicitud.CAMBIO_COMISION: Prioridad.ALTA,
    TipoSolicitud.REVISION_NOTA: Prioridad.ALTA,
    TipoSolicitud.EQUIVALENCIA: Prioridad.MEDIA,
    TipoSolicitud.OTRO: Prioridad.BAJA,
}
