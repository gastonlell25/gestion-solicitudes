# Refactorings aplicados

Una ficha por refactoring, con el código antes/después, el principio o regla que mejora,
el commit y el resultado de los tests al aplicarlo.

---

## 1 - Replace Conditional with Polymorphism (Gabriel)

**Smell que resuelve:** S04 — If/else de transición de estados con códigos de retorno mágicos.

**Principio relacionado:** OCP y LSP (ver justificación en `docs/decisiones-tecnicas.md`).

**Archivos y métodos afectados:** `src/modelos/estado.py` (nuevo), `src/gestor_solicitudes.py` → `cambiar_estado()`, `procesar_opcion()`.

**Código antes:**
```python
def cambiar_estado(self, id, nuevo):
    s = self.buscar(id)
    if s == None:
        return -1
    if nuevo != "PENDIENTE" and nuevo != "EN_REVISION" and nuevo != "APROBADA" and nuevo != "RECHAZADA" and nuevo != "CERRADA":
        return -3
    actual = s.get_estado()
    if actual == nuevo:
        return 0
    if actual == "CERRADA":
        return -2
    elif actual == "APROBADA":
        if nuevo != "CERRADA":
            return -2
    elif actual == "RECHAZADA":
        if nuevo != "CERRADA":
            return -2
    elif actual == "PENDIENTE":
        pass
    elif actual == "EN_REVISION":
        if nuevo == "PENDIENTE":
            pass
    s.set_estado(nuevo)
    ...
    return 1
```

**Código después:**
```python
def cambiar_estado(self, id, nuevo):
    s = self.buscar(id)
    if s == None:
        return -1
    try:
        nuevo_estado = Estado.from_str(nuevo)
    except ValueError:
        raise TransicionInvalidaException("estado invalido.") from None
    actual_estado = Estado.from_str(s.get_estado())
    if actual_estado == nuevo_estado:
        return 0
    if not actual_estado.puede_pasar_a(nuevo_estado):
        raise TransicionInvalidaException(
            "no se puede pasar de " + actual_estado.value + " a " + nuevo_estado.value + "."
        )
    s.set_estado(nuevo_estado.value)
    ...
    return 1
```

El `Estado` consulta una tabla de transiciones permitidas (`puede_pasar_a()`), en vez del
if/elif. Se reprodujo exactamente la matriz de transiciones real del código original
(incluyendo que desde `EN_REVISION` en los hechos se podía pasar a cualquier estado, no
solo a `PENDIENTE` como sugería el comentario) para no alterar el comportamiento externo.

**Justificación:** agregar un estado nuevo ahora implica tocar solo `estado.py` (su tabla
de transiciones), no `gestor_solicitudes.py` (OCP). Cualquier valor de `Estado` se usa de
la misma forma donde se espera el tipo base, sin casos especiales por fuera de la tabla
(LSP). Los códigos de retorno sin nombre (`-2`, `-3`) se reemplazan por una excepción con
mensaje explícito.

**Commits:** `81bbed2` (crear `Estado`), `ac7188a` (conectarlo en `cambiar_estado()`), `bf12da2` (reemplazar códigos por `TransicionInvalidaException`).

**Resultado de los tests:** 44/44 en verde después de cada uno de los 3 commits (incluye `test_gabriel_estados.py`, que prueba exactamente las 5 transiciones T05-T09).

**Ajustes de la revisión de PR (Gastón):** se separó `EstadoInvalidoException` (valor que no es ninguno de los 5 estados) de `TransicionInvalidaException` (estado válido, transición no permitida), para poder capturarlas por separado. Se agregó `Estado.es_final()`, derivado de la propia tabla de transiciones (no hardcodeado contra `CERRADA`, para no romper OCP). Se agregaron 3 tests de punta a punta que faltaban: mismo estado, una regresión no cubierta por los T05-T09 (APROBADA → EN_REVISION) y un estado inválido. 75/75 en verde.

---

## 2 - Replace Magic String with Enum: TipoSolicitud y Prioridad (Gabriel)

**Smell que resuelve:** S05 — Primitive Obsession: tipo y prioridad como strings sueltos.

**Principio relacionado:** Clean Code (Primitive Obsession), OCP.

**Archivos y métodos afectados:** `src/modelos/tipo_solicitud.py` (nuevo), `src/modelos/prioridad.py` (nuevo), `src/gestor_solicitudes.py` → `registrar()` (se elimina `prioridad_por_defecto()`, que pasa a vivir en `TipoSolicitud`).

**Código antes:**
```python
op = self.leer("Tipo: ")
tipo = ""
if op == "1":
    tipo = "CERTIFICADO"
elif op == "2":
    tipo = "CAMBIO_COMISION"
...
pd = self.prioridad_por_defecto(tipo)
...

def prioridad_por_defecto(self, tipo):
    if tipo == "CERTIFICADO":
        return "BAJA"
    elif tipo == "CAMBIO_COMISION":
        return "ALTA"
    ...
```

**Código después:**
```python
op = self.leer("Tipo: ")
try:
    tipo = TipoSolicitud.from_opcion_menu(op)
except ValueError:
    print("Error: tipo invalido.")
    return
...
pd = tipo.prioridad_por_defecto()
```
```python
# src/modelos/tipo_solicitud.py
def prioridad_por_defecto(self) -> Prioridad:
    return _PRIORIDAD_POR_DEFECTO[self]
```

**Justificación:** la relación tipo→prioridad por defecto estaba duplicada (una vez en el
menú de `registrar()`, otra en `prioridad_por_defecto()`); ahora vive en un solo lugar,
dentro del propio enum. Un valor de tipo o prioridad inválido se detecta con una
excepción clara en vez de colarse como string sin validar.

**Commit:** `9a1b503` (crear los enums), `d533d4d` (conectarlos en `registrar()` y borrar el método duplicado).

**Resultado de los tests:** 65/65 en verde (incluye `test_gaston_registro.py`, que ejercita `registrar()` directamente).

---

## 3 - Replace Magic String with Enum: normalización en proc() (Gabriel)

**Smell que resuelve:** S06 — Estados y prioridades con inconsistencias de mayúsculas, normalizadas a mano.

**Principio relacionado:** Clean Code (manejo de errores pobre / validación implícita), SRP.

**Archivos y métodos afectados:** `src/gestor_solicitudes.py` → `proc()`.

**Código antes:**
```python
est = x["estado"]
if est == "pendiente" or est == "Pendiente": est = "PENDIENTE"
if est == "en revision" or est == "En revision" or est == "en_revision": est = "EN_REVISION"
if est == "aprobada" or est == "Aprobada": est = "APROBADA"
if est == "rechazada" or est == "Rechazada": est = "RECHAZADA"
if est == "cerrada" or est == "Cerrada": est = "CERRADA"
pri = x["prioridad"]
if pri == "alta" or pri == "Alta": pri = "ALTA"
if pri == "media" or pri == "Media": pri = "MEDIA"
if pri == "baja" or pri == "Baja": pri = "BAJA"
```

**Código después:**
```python
try:
    est = Estado.from_str(x["estado"]).value
except ValueError:
    est = x["estado"]
try:
    pri = Prioridad.from_str(x["prioridad"]).value
except ValueError:
    pri = x["prioridad"]
```

**Justificación:** `Estado.from_str()`/`Prioridad.from_str()` normalizan cualquier
variante de mayúsculas/espacios (no solo la lista fija de 8 casos que había antes), y si
el valor no se reconoce se deja igual que antes (mismo comportamiento ante datos
corruptos, no se agrega un crash nuevo). Se reusa la misma lógica de validación que ya
existe para S04 y S05, en vez de mantener una lista de `if` aparte.

**Commit:** `317165d`.

**Resultado de los tests:** 66/66 en verde, incluyendo `test_normalizacion_datos.py` (nuevo), que prueba directamente que las solicitudes #3, #6 y #10 de `data/solicitudes.json` (que ya traían variantes en minúscula) se muestran normalizadas.

---

## 4 - Introduce Parameter Object: registrar_solicitud()

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
