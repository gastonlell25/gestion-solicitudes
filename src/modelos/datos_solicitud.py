class DatosSolicitud:
    """Encapsula todos los datos necesarios para registrar una solicitud."""

    def __init__(self, legajo, nombre, apellido, email, carrera, tipo, descripcion, prioridad, fecha):
        self.legajo = legajo
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.carrera = carrera
        self.tipo = tipo
        self.descripcion = descripcion
        self.prioridad = prioridad
        self.fecha = fecha
