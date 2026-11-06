from enum import Enum


class TransicionInvalidaException(Exception):
    """Se lanza al intentar una transicion de estado que la solicitud no permite."""


class Estado(Enum):
    PENDIENTE = "PENDIENTE"
    EN_REVISION = "EN_REVISION"
    APROBADA = "APROBADA"
    RECHAZADA = "RECHAZADA"
    CERRADA = "CERRADA"

    @classmethod
    def from_str(cls, valor: str) -> "Estado":
        normalizado = valor.strip().upper().replace(" ", "_")
        try:
            return cls(normalizado)
        except ValueError:
            raise ValueError(f"Estado invalido: {valor!r}") from None

    def puede_pasar_a(self, nuevo: "Estado") -> bool:
        return nuevo in _TRANSICIONES_PERMITIDAS[self]


_TRANSICIONES_PERMITIDAS = {
    Estado.PENDIENTE: frozenset(
        {Estado.EN_REVISION, Estado.APROBADA, Estado.RECHAZADA, Estado.CERRADA}
    ),
    Estado.EN_REVISION: frozenset(
        {Estado.PENDIENTE, Estado.APROBADA, Estado.RECHAZADA, Estado.CERRADA}
    ),
    Estado.APROBADA: frozenset({Estado.CERRADA}),
    Estado.RECHAZADA: frozenset({Estado.CERRADA}),
    Estado.CERRADA: frozenset(),
}
