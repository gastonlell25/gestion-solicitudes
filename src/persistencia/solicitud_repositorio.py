from abc import ABC, abstractmethod

from persistencia.datos_sistema import DatosSistema


class PersistenciaException(Exception):
    """No se pudieron leer o guardar los datos. El mensaje explica la causa al usuario."""


class SolicitudRepositorio(ABC):
    """Lo único que el gestor necesita de la persistencia: recuperar y guardar los datos.

    El gestor depende de esta abstracción y no de un archivo concreto (DIP). Tiene solo
    las dos operaciones que el gestor usa (ISP): no expone rutas, formatos ni detalles
    del almacenamiento.
    """

    @abstractmethod
    def cargar(self) -> DatosSistema:
        """Devuelve los datos guardados. Lanza PersistenciaException si no se pueden leer."""

    @abstractmethod
    def guardar(self, datos: DatosSistema) -> None:
        """Guarda los datos. Lanza PersistenciaException si no se pudieron guardar."""
