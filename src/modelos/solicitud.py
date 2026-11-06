class Solicitud:
    """Solicitud academica. El estado es uno de los valores de Estado (modelos/estado.py)."""

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

    def dias_desde_creacion(self, fecha_referencia):
        """Antigüedad de la solicitud a una fecha explícita (AAAA-MM-DD)."""
        from datetime import date
        # La lectura por partes conserva fechas sin ceros iniciales admitidas por el original.
        creacion = date(*map(int, self.fecha_creacion.split("-")))
        referencia = date(*map(int, fecha_referencia.split("-")))
        return (referencia - creacion).days

    def esta_vencida(self, fecha_referencia):
        """Reproduce los plazos originales: ALTA=3, MEDIA=7, BAJA=15 días."""
        if self.estado not in ("PENDIENTE", "EN_REVISION"):
            return False
        dias = self.dias_desde_creacion(fecha_referencia)
        plazos = {"ALTA": 3, "MEDIA": 7, "BAJA": 15}
        # Prioridad no reconocida sigue sin estar vencida, como en el original.
        return self.prioridad in plazos and dias > plazos[self.prioridad]

    def get_estado(self):
        return self.estado

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
