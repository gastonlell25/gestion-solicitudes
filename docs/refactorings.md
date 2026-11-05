# Refactorings aplicados

Fichas de cada refactoring realizado en Fase 3, con justificación, impacto y verificación.

## Introduce Parameter Object: registrar_solicitud()

**ID:** IPO-01  
**Técnica:** Introduce Parameter Object  
**Smell resuelto:** S02 - Long Parameter List  
**Principio:** Clean Code (reducir parámetros)  
**Autor:** Gastón  
**Rama:** `refactor/gaston-parameter-object`  
**Commit:** 2aa00a0  

### Descripción

El método `registrar_solicitud()` tenía 9 parámetros individuales:
```python
def registrar_solicitud(self, legajo, nombre, apellido, email, carrera, tipo, descripcion, prioridad, fecha)
```

Esto hacía que:
- Las llamadas fueran largas e ilegibles
- Era fácil equivocarse en el orden
- Agregar un nuevo dato implicaba cambiar la firma y todas las llamadas

### Cambios

Se creó la clase `DatosSolicitud` que encapsula los 9 parámetros:

```python
# src/modelos/datos_solicitud.py
class DatosSolicitud:
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
```

La firma ahora es:
```python
def registrar_solicitud(self, datos):
    est = None
    for i in range(len(self.ests)):
        if self.ests[i].legajo == datos.legajo:
            est = self.ests[i]
    # ...
    s = Solicitud(aux + 1, est, datos.tipo, datos.descripcion, datos.prioridad, "PENDIENTE", None, datos.fecha, datos.fecha)
```

La llamada desde `registrar()`:
```python
# Antes
id = self.registrar_solicitud(legajo, nombre, apellido, email, carrera, tipo, descripcion, prioridad, fecha)

# Después
datos = DatosSolicitud(legajo, nombre, apellido, email, carrera, tipo, descripcion, prioridad, fecha)
id = self.registrar_solicitud(datos)
```

### Verificación

- **Tests:** 19/19 pasan ✅
  - T01-T04 (Gastón): 4 pasan
  - T05-T09 (Gabriel): 5 pasan
  - T10-T15 (Juan): 6 pasan
  - T16-T19 (Fabri): 4 pasan

- **Comportamiento externo:** Idéntico
  - Registro funciona exactamente igual desde la perspectiva del usuario

### Beneficios

- **Legibilidad:** Firma mucho más simple: 1 parámetro en lugar de 9
- **Extensibilidad:** Agregar nuevos datos solo requiere agregar atributo a `DatosSolicitud`
- **Mantenibilidad:** Menos riesgo de errores por orden de parámetros
- **Futuro:** El objeto puede tener métodos propios sin aumentar la complejidad de `registrar_solicitud()`

### Archivos modificados

- `src/modelos/datos_solicitud.py`: +12 líneas (nueva clase)
- `src/gestor_solicitudes.py`: +3 líneas (import, creación del objeto), -6 líneas (cambio de firma y acceso)

---

## Notas para futuras fases

- El objeto `DatosSolicitud` podría tener métodos de validación en el futuro
- Combinado con Extract Method, la lógica de registro es mucho más clara
