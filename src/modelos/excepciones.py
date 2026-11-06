class OperacionRechazadaException(Exception):
    """Una operacion no se pudo hacer por una regla del sistema. El mensaje es para el usuario."""


class SolicitudNoEncontradaException(OperacionRechazadaException):
    def __init__(self, id_solicitud):
        super().__init__("no existe una solicitud con ID " + str(id_solicitud) + ".")


class ResponsableNoEncontradoException(OperacionRechazadaException):
    def __init__(self, id_responsable):
        super().__init__("no existe un responsable con ID " + str(id_responsable) + ".")


class SolicitudCerradaException(OperacionRechazadaException):
    def __init__(self):
        super().__init__("no se puede asignar responsable a una solicitud CERRADA.")
