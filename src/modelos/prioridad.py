from enum import Enum


class Prioridad(Enum):
    ALTA = "ALTA"
    MEDIA = "MEDIA"
    BAJA = "BAJA"

    @classmethod
    def from_str(cls, valor: str) -> "Prioridad":
        normalizado = valor.strip().upper()
        try:
            return cls(normalizado)
        except ValueError:
            raise ValueError(f"Prioridad invalida: {valor!r}") from None
