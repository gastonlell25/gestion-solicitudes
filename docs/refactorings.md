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

## 5 - Extract Class: SolicitudRepositorioArchivo (Fabri)

**Smell que resuelve:** S10 — God Class + acoplamiento directo a la persistencia.

**Principio relacionado:** SRP; Clean Code: límites entre componentes (ver `docs/decisiones-tecnicas.md`).

**Archivos y métodos afectados:** `src/persistencia/solicitud_repositorio_archivo.py` (nuevo),
`src/persistencia/datos_sistema.py` (nuevo), `src/gestor_solicitudes.py` → `__init__()`, `cargar()`, `guardar()`;
se movieron `proc()` y `datos_ejemplo()`.

**Código antes** (`src/gestor_solicitudes.py`):
```python
def __init__(self):
    ...
    self.archivo = ArchivoJSON()

def cargar(self):
    data2 = None
    txt = self.archivo.leer()
    if txt != None:
        try:
            data2 = json.loads(txt)
        except:
            pass
    if data2 == None:
        data2 = self.datos_ejemplo()
        self.proc(data2)
        self.guardar()
    else:
        self.proc(data2)

def proc(self, data2):        # convierte el JSON en objetos (25 líneas)
    ...
def guardar(self):            # convierte los objetos en JSON y escribe el archivo
    ...
def datos_ejemplo(self):      # 26 líneas de datos de ejemplo
    ...
```

**Código después** (`src/gestor_solicitudes.py`):
```python
def cargar(self):
    datos = self.repositorio.cargar()
    self.ests = datos.estudiantes
    self.resp = datos.responsables
    self.lst = datos.solicitudes

def guardar(self):
    return self.repositorio.guardar(DatosSistema(self.ests, self.resp, self.lst))
```
`cargar()`, `proc()`, `guardar()` y `datos_ejemplo()` se movieron **sin cambios de lógica** a
`SolicitudRepositorioArchivo`, que devuelve y recibe un `DatosSistema` (dataclass con las tres listas).
`proc()` conserva su nombre porque lo renombra Gaston (S03).

**Justificación:** el gestor deja de saber cómo se guarda la información (formato JSON, conversión
de diccionarios a objetos, datos de ejemplo). Pasa de 538 a 467 líneas y pierde una razón para cambiar (SRP).
Los `except:` vacíos se movieron tal cual; se corrigen en el refactoring de S11, para que cada commit
haga una sola cosa.

**Commit:** `d6e4d10`.

**Resultado de los tests:** 75/75 en verde. Además, la salida de 14 sesiones de consola (todas las
opciones del menú, archivo inexistente, archivo dañado y archivo de solo lectura) es idéntica byte a byte a la de `main`.

**Evidencia:** `docs/evidencias/despues/despues_fabri_diff_extract-class-repositorio.png`.

---

## 6 - Introduce Interface + inyección por constructor: SolicitudRepositorio (Fabri)

**Smell que resuelve:** S10 — God Class + acoplamiento directo a la persistencia.

**Principio relacionado:** DIP e ISP (ver `docs/decisiones-tecnicas.md`).

**Archivos y métodos afectados:** `src/persistencia/solicitud_repositorio.py` (nuevo),
`src/persistencia/solicitud_repositorio_archivo.py`, `src/gestor_solicitudes.py` → `__init__()`, `src/main.py`.

**Código antes:**
```python
# gestor_solicitudes.py
from persistencia.solicitud_repositorio_archivo import SolicitudRepositorioArchivo

def __init__(self):
    ...
    self.repositorio = SolicitudRepositorioArchivo()   # el gestor elige la clase concreta

# main.py
g = GestorSolicitudes()
```

**Código después:**
```python
# persistencia/solicitud_repositorio.py
class SolicitudRepositorio(ABC):
    @abstractmethod
    def cargar(self) -> DatosSistema: ...
    @abstractmethod
    def guardar(self, datos: DatosSistema) -> bool: ...

# gestor_solicitudes.py
from persistencia.solicitud_repositorio import SolicitudRepositorio

def __init__(self, repositorio: SolicitudRepositorio):
    ...
    self.repositorio = repositorio

# main.py: arma las dependencias
g = GestorSolicitudes(SolicitudRepositorioArchivo())
```

**Justificación:** el gestor (alto nivel) depende de una abstracción y no del archivo (bajo nivel).
Para cambiar JSON por otra forma de guardar se escribe otra implementación de `SolicitudRepositorio`
y se cambia una línea de `main.py`, sin tocar el gestor (DIP). La interfaz tiene solo las dos
operaciones que el gestor usa (ISP). `tests/test_fabri_repositorio.py` lo demuestra: prueba el gestor
con un `RepositorioEnMemoria` que no toca ningún archivo.

**Commits:** `7dd5d26` (interfaz e inyección), `af4a4ff` (tests unitarios del repositorio).

**Resultado de los tests:** 79/79 en verde (75 + 4 nuevos). Salida de consola idéntica a `main` en las 14 sesiones.

**Evidencia:** `docs/evidencias/despues/despues_fabri_diff_introduce-interface.png`,
`docs/evidencias/despues/despues_fabri_tests_repositorio.png`.

---

## 7 - Replace Error Code with Exception: PersistenciaException (Fabri)

**Smell que resuelve:** S11 — Manejo de errores pobre (parte de persistencia).

**Principio relacionado:** Clean Code: manejo de errores (excepciones en vez de códigos, no ignorar
errores, no mezclar la consola con el acceso a datos).

**Archivos y métodos afectados:** `src/archivo_json.py` → `leer()`, `escribir()`;
`src/persistencia/solicitud_repositorio_archivo.py` → `cargar()`, `guardar()`, `leer_texto()` (nuevo);
`src/persistencia/solicitud_repositorio.py` → `PersistenciaException` (nueva);
`src/gestor_solicitudes.py` → `iniciar()`, `registrar()`, `registrar_solicitud()`, `guardar()`.

**Código antes:**
```python
# archivo_json.py
def leer(self):
    try:
        ...
    except:                       # cualquier error (incluso permisos) se vuelve None
        return None

def escribir(self, txt):
    try:
        ...
        return True
    except Exception as e:
        print("Error: " + str(e))  # la capa de datos imprime en consola
        return False

# repositorio: un archivo dañado se trata igual que uno inexistente
try:
    data2 = json.loads(txt)
except:
    pass
if data2 == None:
    datos = self.proc(self.datos_ejemplo())
    self.guardar(datos)           # pisa el archivo dañado: se pierden los datos

# gestor: el resultado de guardar() se ignora
s.set_responsable(x)
self.guardar()
return 1                          # la consola muestra "Responsable asignado"
```

**Código después:**
```python
# archivo_json.py: solo se maneja el caso esperado
def leer(self):
    try:
        with open(self.ruta, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return None

# repositorio: traduce los errores técnicos a una excepción con mensaje para el usuario
def cargar(self):
    txt = self.leer_texto()
    if txt is None:               # primera ejecución: se crean los datos de ejemplo
        ...
    try:
        return self.proc(json.loads(txt))
    except json.JSONDecodeError as e:
        raise PersistenciaException(self.descripcion_archivo() + " tiene un formato invalido (linea ...)") from e

# gestor: un único lugar muestra el error y descarta el cambio que no se guardó
try:
    flag = self.procesar_opcion(op)
except PersistenciaException as e:
    print("Error: " + str(e) + ". La operacion no se guardo.")
    self.cargar()
```

**Justificación:** ningún error queda escondido. La capa de datos ya no imprime y el usuario recibe
siempre el mismo tipo de mensaje. Además se corrigen dos bugs del sistema base (ver "Bugs del sistema
base" en `docs/pruebas.md`):
- un archivo de datos dañado ya no se reemplaza por los datos de ejemplo;
- un guardado fallido ya no muestra un mensaje de éxito ni deja el cambio pendiente en memoria.

**Commits:** `511b9fd` (guardado), `37cc26e` (lectura y archivo dañado), `6f58b7c` (tests).

**Resultado de los tests:** 79/79 en verde después de cada commit; 82/82 con los 3 tests nuevos de
`tests/test_fabri_errores.py`. Los dos tests de punta a punta de ese archivo **fallan sobre `main`**,
o sea que detectan los bugs. En las sesiones de consola solo cambian los dos casos de error; el resto es idéntico.

**Evidencia:** `docs/evidencias/despues/despues_fabri_diff_excepciones-persistencia.png`; pares
`antes_/despues_fabri_archivo-danado.png` y `antes_/despues_fabri_guardado-fallido.png`.

---

## 8 - Replace Error Code with Exception: excepciones propias del gestor (Fabri)

**Smell que resuelve:** S11 — Manejo de errores pobre (códigos `-1`, `-2`, `-3` y `except:` vacíos).

**Principio relacionado:** Clean Code: manejo de errores; OCP (un error nuevo no obliga a tocar los `if` del menú).

**Archivos y métodos afectados:** `src/modelos/excepciones.py` (nuevo), `src/gestor_solicitudes.py` →
`procesar_opcion()`, `cambiar_estado()`, `asignar_responsable()`, `buscar_existente()` (nuevo), `buscar()`.

**Código antes:**
```python
def asignar_responsable(self, id_solicitud, id_responsable):
    s = self.buscar(id_solicitud)
    if s == None:
        return -1
    ...
    if x == None:
        return -2
    if s.estado == "CERRADA":
        return -3
    ...
    return 1

# procesar_opcion(): el menú tiene que saber qué significa cada número
res = self.asignar_responsable(id2, idr)
if res == 1:
    print("Responsable asignado: ...")
elif res == -2:
    print("Error: no existe un responsable con ID " + idr + ".")
elif res == -3:
    print("Error: no se puede asignar responsable a una solicitud CERRADA.")
else:
    print("Error: no se pudo asignar el responsable.")
```

**Código después:**
```python
# modelos/excepciones.py
class OperacionRechazadaException(Exception): ...
class SolicitudNoEncontradaException(OperacionRechazadaException): ...
class ResponsableNoEncontradoException(OperacionRechazadaException): ...
class SolicitudCerradaException(OperacionRechazadaException): ...

def asignar_responsable(self, id_solicitud, id_responsable):
    s = self.buscar_existente(id_solicitud)        # lanza SolicitudNoEncontradaException
    ...
    if x == None:
        raise ResponsableNoEncontradoException(id_responsable)
    if s.estado == "CERRADA":
        raise SolicitudCerradaException()
    ...

# procesar_opcion()
try:
    self.asignar_responsable(id2, idr)
except OperacionRechazadaException as e:
    print("Error: " + str(e))
    return True
print("Responsable asignado: ...")
```
`cambiar_estado()` devuelve `True`/`False` (cambió o ya estaba en ese estado) en lugar de `1`/`0`/`-1`,
y `buscar()` captura solo `ValueError` en lugar de un `except:` vacío.

**Justificación:** el error tiene nombre y lleva su propio mensaje, así que el menú no interpreta
números. Para agregar un error nuevo se crea otra subclase de `OperacionRechazadaException` y el
`except` del menú ya la cubre. Los mensajes al usuario son exactamente los mismos que antes.

**Commits:** `6a122c0` (excepciones propias), `ec75ac8` (`buscar()`).

**Resultado de los tests:** 79/79 en verde después de cada commit (T16 y T17 prueban los mensajes de
asignación y T05–T09 los de cambio de estado). La salida de consola es idéntica a la del paso anterior en las 14 sesiones.

**Evidencia:** `docs/evidencias/despues/despues_fabri_diff_excepciones-propias.png`,
`docs/evidencias/despues/despues_fabri_tests_excepciones.png`.

---

## 9 - Remove Dead Code y comentarios desactualizados (Fabri)

**Smell que resuelve:** S12 — Código muerto y comentarios desactualizados.

**Principio relacionado:** Clean Code: sin código muerto (YAGNI); comentarios que explican el "por qué" y no mienten.

**Archivos y métodos afectados:** `src/gestor_solicitudes.py` → `validar_email()` y `exportar_csv()` (eliminados);
`src/modelos/solicitud.py` → 7 getters y setters sin uso (eliminados) y comentarios; `src/archivo_json.py` y
`src/persistencia/solicitud_repositorio_archivo.py` → comentarios.

**Código antes:**
```python
# solicitud.py
# Clase Solicitud
# el estado puede ser "P" (pendiente), "A" (aprobada) o "R" (rechazada)   <- falso: son 5 estados en mayúsculas
class Solicitud:
    def get_id(self): ...            # nadie lo llama (igual que get_estudiante, get_tipo,
    def get_descripcion(self): ...   # get_prioridad, set_prioridad y get_fecha_modificacion)
    # devuelve el estado            <- repite el código
    def get_estado(self): ...

# gestor_solicitudes.py
def validar_email(self, email): ...      # nunca se llama; registrar() valida con find("@")
def exportar_csv(self, ruta):            # nunca se llama
    ...
    except:
        pass

# archivo_json.py
# Clase para manejar la base de datos     <- es un archivo JSON, no una base de datos
```

**Código después:**
```python
# solicitud.py
class Solicitud:
    """Solicitud academica. El estado es uno de los valores de Estado (modelos/estado.py)."""
    ...                                   # quedan solo los accesores que se usan

# archivo_json.py
class ArchivoJSON:
    """Lee y escribe el archivo de datos (data/solicitudes.json, o la ruta de ARCHIVO_DATOS)."""
```

**Justificación:** hay menos código para leer y mantener (−48 líneas) y desaparece el último `except:` vacío del
proyecto, que estaba en `exportar_csv()`. Además, ya no hay dos validaciones de email distintas que puedan dar resultados
diferentes, y los comentarios dicen la verdad. Si en el futuro hace falta exportar a CSV, el código se recupera del historial de Git.

**Commits:** `f0fc485` (`validar_email()` y `exportar_csv()`), `bd10463` (getters y setters), `630830f` (comentarios).

**Resultado de los tests:** 82/82 en verde después de cada commit. La salida de consola es idéntica a la del paso anterior en las 14 sesiones.

**Evidencia:** `docs/evidencias/despues/despues_fabri_diff_remove-dead-code.png`,
`docs/evidencias/despues/despues_fabri_tests_codigo-muerto.png`.

---

## Notas para futuras fases

- El objeto `DatosSolicitud` podría tener métodos de validación en el futuro
- Combinado con Extract Method, la lógica de registro es mucho más clara
