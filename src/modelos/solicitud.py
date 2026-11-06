# Clase Solicitud
# el estado puede ser "P" (pendiente), "A" (aprobada) o "R" (rechazada)
class Solicitud:

    def __init__(self, id, estudiante, tipo, descripcion, prioridad, estado, responsable, fecha_creacion, fecha_modificacion):
        self.id = id
        self.estudiante = estudiante
        self.tipo = tipo
        self.descripcion = descripcion
        self.prioridad = prioridad
        self.estado = estado
        self.responsable = responsable
        self.fecha_creacion = fecha_creacion
        self.fecha_modificacion = fecha_modificacion

    # devuelve el estado
    def get_estado(self):
        return self.estado

    # setea el estado
    def set_estado(self, estado):
        self.estado = estado

    def get_responsable(self):
        return self.responsable

    def set_responsable(self, responsable):
        self.responsable = responsable

    def get_fecha_creacion(self):
        return self.fecha_creacion

    def set_fecha_modificacion(self, fecha):
        self.fecha_modificacion = fecha
