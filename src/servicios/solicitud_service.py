import datetime
from modelos.estudiante import Estudiante
from modelos.solicitud import Solicitud
from modelos.estado import Estado, EstadoInvalidoException, TransicionInvalidaException
from modelos.tipo_solicitud import TipoSolicitud
from modelos.prioridad import Prioridad
from modelos.datos_solicitud import DatosSolicitud
from modelos.excepciones import (
    OperacionRechazadaException,
    ResponsableNoEncontradoException,
    SolicitudCerradaException,
    SolicitudNoEncontradaException,
)
from persistencia.datos_sistema import DatosSistema
from persistencia.solicitud_repositorio import PersistenciaException, SolicitudRepositorio


class SolicitudService:
    """Lógica de negocio: transacciones, validaciones y cálculos sobre solicitudes."""

    def __init__(self, repositorio: SolicitudRepositorio):
        self.solicitudes = []
        self.estudiantes = []
        self.responsables = []
        self.repositorio = repositorio

    def cargar(self):
        """Carga datos del repositorio."""
        datos = self.repositorio.cargar()
        self.estudiantes = datos.estudiantes
        self.responsables = datos.responsables
        self.solicitudes = datos.solicitudes

    def guardar(self):
        """Persiste datos en el repositorio."""
        self.repositorio.guardar(DatosSistema(self.estudiantes, self.responsables, self.solicitudes))

    def registrar_solicitud(self, datos: DatosSolicitud):
        """Registra una nueva solicitud y devuelve su ID."""
        estudiante = None
        for i in range(len(self.estudiantes)):
            if self.estudiantes[i].legajo == datos.legajo:
                estudiante = self.estudiantes[i]
        if estudiante == None:
            estudiante = Estudiante(datos.legajo, datos.nombre, datos.apellido, datos.email, datos.carrera)
            self.estudiantes.append(estudiante)
        proximo_id = 0
        for i in range(len(self.solicitudes)):
            if self.solicitudes[i].id > proximo_id:
                proximo_id = self.solicitudes[i].id
        solicitud = Solicitud(proximo_id + 1, estudiante, datos.tipo, datos.descripcion, datos.prioridad, "PENDIENTE", None, datos.fecha, datos.fecha)
        self.solicitudes.append(solicitud)
        self.guardar()
        return solicitud.id

    def cambiar_estado(self, id, nuevo):
        """Cambia el estado de una solicitud. Devuelve True si cambió, False si ya estaba en ese estado."""
        solicitud = self.buscar_existente(id)
        nuevo_estado = Estado.from_str(nuevo)
        actual_estado = Estado.from_str(solicitud.get_estado())
        if actual_estado == nuevo_estado:
            return False
        if not actual_estado.puede_pasar_a(nuevo_estado):
            raise TransicionInvalidaException(
                "no se puede pasar de " + actual_estado.value + " a " + nuevo_estado.value + "."
            )
        solicitud.set_estado(nuevo_estado.value)
        solicitud.set_fecha_modificacion(self._hoy())
        self.guardar()
        return True

    def asignar_responsable(self, id_solicitud, id_responsable):
        """Asigna un responsable a una solicitud."""
        solicitud = self.buscar_existente(id_solicitud)
        responsable_encontrado = None
        for i in range(len(self.responsables)):
            if str(self.responsables[i].id) == id_responsable:
                responsable_encontrado = self.responsables[i]
        if responsable_encontrado == None:
            raise ResponsableNoEncontradoException(id_responsable)
        if solicitud.estado == "CERRADA":
            raise SolicitudCerradaException()
        solicitud.set_responsable(responsable_encontrado)
        solicitud.set_fecha_modificacion(self._hoy())
        self.guardar()

    def buscar(self, id):
        """Busca una solicitud por ID."""
        try:
            n = int(id)
        except ValueError:
            return None
        for i in range(len(self.solicitudes)):
            if self.solicitudes[i].id == n:
                return self.solicitudes[i]
        return None

    def buscar_existente(self, id):
        """Busca una solicitud o lanza excepción si no existe."""
        solicitud = self.buscar(id)
        if solicitud is None:
            raise SolicitudNoEncontradaException(id)
        return solicitud

    def _filtrar(self, obtener_valor, valor):
        """Recorrido único para filtrado; cada función pública conserva la semántica original."""
        return [solicitud for solicitud in self.solicitudes
                if obtener_valor(solicitud) == valor]

    def filtrar_por_estado(self, estado):
        """Filtra solicitudes por estado."""
        return self._filtrar(lambda s: s.estado.upper(), estado.upper().strip().replace(" ", "_"))

    def filtrar_por_tipo(self, tipo):
        """Filtra solicitudes por tipo."""
        return self._filtrar(lambda s: s.tipo.upper(), tipo.upper().strip().replace(" ", "_"))

    def filtrar_por_prioridad(self, prioridad):
        """Filtra solicitudes por prioridad."""
        return self._filtrar(lambda s: s.prioridad.upper(), prioridad.upper().strip())

    def filtrar_por_legajo(self, legajo):
        """Filtra solicitudes por legajo del estudiante."""
        return self._filtrar(lambda s: s.estudiante.legajo, legajo.strip())

    def _hoy(self):
        """Obtiene la fecha actual (puede ser reemplazada en tests)."""
        import os
        if os.environ.get("FECHA_HOY"):
            return os.environ.get("FECHA_HOY")
        return datetime.date.today().strftime("%Y-%m-%d")
