from dataclasses import dataclass, field

from modelos.estudiante import Estudiante
from modelos.responsable import Responsable
from modelos.solicitud import Solicitud


@dataclass
class DatosSistema:
    """Todo lo que se guarda y se recupera del almacenamiento, en un solo objeto."""

    estudiantes: list[Estudiante] = field(default_factory=list)
    responsables: list[Responsable] = field(default_factory=list)
    solicitudes: list[Solicitud] = field(default_factory=list)
