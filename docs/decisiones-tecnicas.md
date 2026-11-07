## Gaston: registro de solicitudes y consola

### S01 - Long Method en procesarOpcion()
- **Qué viola:** SRP, porque el método tiene 4 responsabilidades (leer datos, validar, guardar e imprimir). También la regla de Clean Code de que una función debe ser corta y hacer una sola cosa.
- **Qué se propone:** aplicar Extract Method y separarlo en métodos con nombre propio: `leerDatosSolicitud()`, `validarDatos()`, `guardarSolicitud()` y `mostrarResultado()`. Después, separar la parte de consola (MenuConsola) de la lógica (SolicitudService).
- **Por qué:** cada parte se puede entender, modificar y probar por separado.

### S02 - Long Parameter List en registrarSolicitud()
- **Qué viola:** la regla de Clean Code de usar pocos parámetros por función.
- **Qué se propone:** aplicar Introduce Parameter Object y agrupar los 9 parámetros en una clase `DatosSolicitud`.
- **Por qué:** las llamadas quedan más claras, no se puede confundir el orden y agregar un dato nuevo no cambia la firma del método.

### S03 - Malos nombres
- **Qué viola:** la regla de Clean Code de usar nombres que revelen la intención.
- **Qué se propone:** aplicar Rename: `x` → `opcionElegida`, `lst` → `solicitudes`, `proc()` → `procesarSolicitud()`.
- **Por qué:** el código se entiende sin tener que leer todo el método.

## Gabriel: estados, tipos y prioridades

### S04 - If/else de transición de estados con códigos de retorno mágicos
- **Qué viola:** OCP, porque agregar un estado nuevo obliga a modificar el `if/elif` de `cambiar_estado()` y el `elif` espejo en `procesar_opcion()`; también Clean Code, por usar números sin nombre como códigos de error.
- **Qué se propone:** Replace Conditional with Polymorphism (patrón State): cada estado concreto sabe a qué estados puede pasar, así agregar un estado no toca código existente (LSP: cualquier estado concreto se usa donde se espera el tipo base). Reemplazar los códigos de retorno por `TransicionInvalidaException` (nombre coordinado con Fabri).
- **Alternativas consideradas:** el patrón State clásico de GoF, con una subclase por estado (`EstadoPendiente`, `EstadoAprobada`, etc.). Se descarta porque con solo 5 estados fijos y sin datos ni comportamiento propio más allá de "a qué puedo pasar", crear 5 clases agrega complejidad sin un beneficio real; un `Enum` con una tabla de transiciones logra lo mismo (cada estado "sabe" a dónde puede ir) con mucho menos código.
- **Por qué:** la regla de transición queda en un solo lugar por estado, y el llamador no tiene que recordar qué significa cada número.
- **Implementado:** `src/modelos/estado.py` (commits `81bbed2`, `ac7188a`, `bf12da2`).

### S05 - Primitive Obsession: tipo y prioridad como strings sueltos
- **Qué viola:** Clean Code (Primitive Obsession) y OCP, porque agregar un tipo de solicitud implica tocar el menú y repetir el literal en `prioridad_por_defecto()`.
- **Qué se propone:** Replace Magic String with Enum: crear `TipoSolicitud` y `Prioridad`, con la prioridad por defecto como propiedad del propio enum de tipo.
- **Alternativas consideradas:** usar constantes de módulo (`TIPO_CERTIFICADO = "CERTIFICADO"`, etc.) en vez de un `Enum`. Se descarta porque las constantes no validan nada (cualquier string pasa) ni permiten agregarles comportamiento propio; el `Enum` sí valida con `from_opcion_menu()`/`from_str()` y permite que `prioridad_por_defecto()` viva junto al tipo, no repetida en el gestor.
- **Por qué:** hay un solo lugar que define qué tipos y prioridades existen, y un valor inválido se detecta antes de comparar strings.
- **Implementado:** `src/modelos/tipo_solicitud.py`, `src/modelos/prioridad.py` (commits `9a1b503`, `d533d4d`).

### S06 - Estados y prioridades con inconsistencias de mayúsculas, normalizadas a mano
- **Qué viola:** Clean Code (manejo de errores pobre / validación implícita) y SRP, porque `proc()` mezcla la carga de datos con la normalización de valores mal escritos.
- **Qué se propone:** reemplazar el string por un `Enum` con un único parser (`Estado.from_str()`) que normalice y lance una excepción clara si el valor no es válido, en vez de ir agregando `if` por cada variante.
- **Alternativas consideradas:** seguir agregando líneas `if` para cubrir más variantes a medida que aparecen. Se descarta porque no ataca el problema de fondo (una lista abierta e impredecible de casos); reusar `Estado.from_str()`/`Prioridad.from_str()` normaliza cualquier variante de mayúsculas/espacios sin agrandar una lista frágil, y si el valor no se reconoce se deja igual que antes (no se cambia el comportamiento ante datos corruptos).
- **Por qué:** una variante no prevista deja de pasar en silencio: se detecta al cargar el dato, no después, cuando ya afectó un reporte o un filtro.
- **Implementado:** `src/gestor_solicitudes.py` → `proc()` (commit `317165d`).

## Juan: filtros y reportes (diagnóstico)

### S07 - Duplicación de filtros
- **Evidencia:** cuatro métodos `filtrar_por_*` con lógica repetida en `src/gestor_solicitudes.py:319–349`.
- **Decisión propuesta:** compartir el recorrido en una función común con criterio explícito; conservar las llamadas públicas que usa la consola.
- **Verificación prevista:** comparar resultados por estado, tipo, prioridad y legajo, incluyendo búsqueda sin coincidencias (T10–T14).

### S08 - Feature Envy
- **Evidencia:** `dias_desde_creacion` y `esta_vencida` concentran en el gestor reglas que dependen de atributos de `Solicitud`.
- **Decisión propuesta:** aplicar Move Method y delegar el cálculo al modelo, pasando la fecha de referencia para que sea comprobable con tests.
- **Verificación prevista:** comparar los valores de antigüedad y vencimiento para fechas y prioridades iguales antes y después.

### S09 - Data Class
- **Evidencia:** `Solicitud` contiene mayormente atributos y métodos de acceso, mientras su antigüedad y vencimiento se calculan fuera.
- **Decisión propuesta:** acercar las reglas propias de una solicitud al modelo sin mezclar allí persistencia, presentación ni lógica de otros actores.
- **Verificación prevista:** conservar los valores observables de la entidad y superar las pruebas de caracterización.

## Fabri: persistencia y manejo de errores

### S10 - God Class y acoplamiento directo a ArchivoJSON
- **Qué viola:** SRP, porque `GestorSolicitudes` tiene muchas razones para cambiar: el menú, las reglas de negocio, los filtros, el reporte y la persistencia. DIP, porque la lógica de alto nivel crea y usa directamente una clase de bajo nivel (`ArchivoJSON()` en el constructor) y además conoce el formato del JSON (`proc()` y `guardar()`).
- **Qué se propone:** aplicar Extract Class y mover `cargar()`, `proc()`, `guardar()` y `datos_ejemplo()`, junto con `ArchivoJSON`, a una clase `SolicitudRepositorioArchivo`. Después, Introduce Interface: definir `SolicitudRepositorio` (clase abstracta con `abc`) con solo las operaciones que usa el servicio, y que el servicio la reciba por constructor; `main.py` arma las dependencias. Para ISP, la interfaz queda chica y específica; si al implementarla aparecen clientes que solo leen o solo escriben, se separa en una interfaz de lectura y otra de escritura.
- **Por qué:** cambiar la forma de guardar no toca la lógica, y los tests pueden usar un archivo temporal o un repositorio en memoria. Además achica la God Class antes de los refactorings de Gaston y Juan, que es el orden de merge acordado.

- **Qué se decidió (Fase 3):**
  - `SolicitudRepositorioArchivo` (`src/persistencia/`) recibe todo lo que el gestor hacía con el archivo: leer, convertir el JSON en objetos, guardar y generar los datos de ejemplo.
  - El gestor recibe un `SolicitudRepositorio` por constructor y `main.py` arma las dependencias.
  - Los datos viajan en un solo objeto, `DatosSistema` (dataclass con estudiantes, responsables y solicitudes). Así la interfaz no crece cada vez que se agrega una colección.
- **DIP:** antes, `GestorSolicitudes` (alto nivel) creaba `ArchivoJSON()` (bajo nivel) y conocía el formato del JSON. Ahora los dos dependen de la abstracción `SolicitudRepositorio`. Prueba de que funciona: `tests/test_fabri_repositorio.py` usa el gestor con un repositorio en memoria, sin archivo.
- **ISP:** la interfaz tiene solo `cargar()` y `guardar()`, las dos operaciones que usa su único cliente (el gestor). No se separó en una interfaz de lectura y otra de escritura porque no hay ningún cliente que use solo una de las dos: separarla agregaría una abstracción sin uso (YAGNI). Si aparece uno (por ejemplo, un reporte de solo lectura), se separa.
- **Alternativas consideradas:**
  - Un repositorio con operaciones por entidad (`buscar(id)`, `agregar(solicitud)`, `listar()`…): es más fino, pero obligaba a reescribir la lógica de búsqueda y de generación de IDs, que es del área de Gaston, y mezclaba el refactor con cambios de comportamiento. Se eligió el contrato que el sistema ya usaba (cargar todo al inicio y guardar todo después de cada cambio).
  - Usar `typing.Protocol` en vez de `abc.ABC`: también cumple DIP, pero `ABC` hace explícito el contrato y falla al instanciar una implementación incompleta, algo más fácil de mostrar y de explicar.
- **Orden de los commits:** primero se movió el código tal cual (Extract Class, con la salida de consola idéntica) y después se agregó la interfaz. Los `except:` vacíos quedaron como estaban; se corrigen en el refactoring de S11, para no mezclar cambios.

### S11 - Manejo de errores pobre
- **Qué viola:** las reglas de Clean Code de manejo de errores: usar excepciones en lugar de códigos de retorno, no ignorar errores con `except:` vacíos y no mezclar la presentación (`print`) con el acceso a datos. Además hay un bug real: si `data/solicitudes.json` está dañado, se pisa con los datos de ejemplo y se pierden los datos.
- **Qué se propone:** crear excepciones propias (`SolicitudNoEncontradaException`, `ResponsableNoEncontradoException`, `PersistenciaException`; el nombre `TransicionInvalidaException` se coordina con Gabriel). El repositorio captura solo excepciones específicas (`FileNotFoundError`, `json.JSONDecodeError`, `OSError`) y las convierte en `PersistenciaException`; solo la consola muestra mensajes. Si el archivo no existe se siguen generando los datos de ejemplo (comportamiento actual), pero si existe y está dañado se informa el error y no se sobrescribe. Ese cambio de comportamiento se registra como mejora intencional y se decide en grupo en `docs/pruebas.md`.
- **Alternativas consideradas:** mantener los códigos pero con constantes con nombre (`RESPONSABLE_INEXISTENTE = -2`). Se descarta porque el error se sigue pudiendo ignorar sin que nadie se entere.
- **Por qué:** un error no puede pasar desapercibido, el mensaje al usuario es claro y siempre igual, y agregar un error nuevo no obliga a tocar cada `if` del menú.

- **Qué se decidió (Fase 3):**
  - **Errores de persistencia:** `PersistenciaException` se define junto a la interfaz `SolicitudRepositorio`, porque es parte de su contrato. `ArchivoJSON` solo maneja el caso esperado (`FileNotFoundError` → el archivo todavía no existe) y deja pasar el resto. El repositorio traduce `OSError`, `json.JSONDecodeError`, `KeyError` y `TypeError` a `PersistenciaException`, con un mensaje para el usuario.
  - **Dónde se muestran:** la consola los captura en un solo lugar. En `iniciar()`, al cargar, el sistema no arranca y avisa que el archivo no se modificó. En el bucle del menú, al guardar, muestra el error y recarga el último estado guardado, para no persistir después un cambio que el usuario vio fallar.
  - **Errores de reglas:** `src/modelos/excepciones.py` define `OperacionRechazadaException` como base de `SolicitudNoEncontradaException`, `ResponsableNoEncontradoException` y `SolicitudCerradaException`. Cada una lleva su mensaje y el menú hace `print("Error: " + str(e))`, igual que con `TransicionInvalidaException` de Gabriel. Se coordinó no mover las excepciones de Gabriel, que siguen en `modelos/estado.py`.
- **Comportamiento que cambia (mejora intencional):** archivo dañado y guardado fallido; están detallados en `docs/pruebas.md` → "Bugs del sistema base encontrados". El resto de los mensajes al usuario quedó igual, letra por letra.
- **Alternativas consideradas:**
  - Que `ArchivoJSON` lance directamente `PersistenciaException`: se descartó porque `ArchivoJSON` no conoce el formato. Solo el repositorio puede distinguir "archivo dañado" de "no se pudo leer".
  - Deshacer el cambio con la técnica de "copiar y restaurar" cada objeto antes de modificarlo: más código en cada operación. Recargar desde el repositorio deja el sistema en el último estado guardado con una sola línea.
  - Una única excepción genérica con un código adentro: volvía a obligar al menú a interpretar códigos.
- **Caso no cubierto (mejora pendiente):** el guardado falla y, además, el archivo fue borrado mientras el sistema estaba abierto. La recarga intenta recrearlo con los datos de ejemplo, vuelve a fallar y el programa termina con un error técnico. Se deja así por ser un caso extremo.
- **Límite conocido: la escritura no es atómica (observación CR-03 de Juan, Fase 5).** `ArchivoJSON.escribir()` abre el archivo en modo `"w"`, que lo vacía antes de escribir. Si el proceso se corta justo en ese momento (por ejemplo, se cierra la terminal o se llena el disco), el archivo puede quedar incompleto y en la próxima carga se informa como dañado. La corrección de S11 evita el mensaje de éxito falso, pero no esto.
  - **Alternativa evaluada:** escribir en un archivo temporal de la misma carpeta y reemplazar el original con `os.replace()`, que es atómico.
  - **Por qué no se aplicó ahora:** cambia el comportamiento con un archivo de solo lectura. `os.replace()` depende de los permisos de la carpeta y no de los del archivo, así que el guardado dejaría de fallar en el caso que cubre `test_si_no_se_puede_guardar_no_informa_exito_ni_conserva_el_cambio`. Para mantenerlo habría que agregar una verificación de permisos aparte. Como Juan pidió no cambiar el alcance sin una decisión del grupo, queda como **mejora pendiente** para las conclusiones (Apartado 10).

### S12 - Código muerto y comentarios desactualizados
- **Qué viola:** las reglas de Clean Code de no dejar código muerto y de que los comentarios expliquen el "por qué" y sean verdaderos.
- **Qué se propone:** aplicar Remove Dead Code: borrar `exportar_csv()` (si en el futuro hace falta exportar, se recupera del historial de Git), los getters y setters sin uso y las ramas `elif ... pass`. Con `validar_email()` se decide junto con Gaston (área de registro): si `registrar()` pasa a usarla, cambia el comportamiento y se documenta como mejora intencional; si no, se borra. Comentarios: eliminar los que repiten el código y corregir o eliminar los falsos (estados "P/A/R", "devuelve True", "base de datos").
- **Por qué:** hay menos código para leer y mantener, y los comentarios dejan de dar información equivocada.
- **Qué se decidió (Fase 3):**
  - Se borraron `exportar_csv()`, `validar_email()` y los 7 getters y setters sin uso.
  - Con `validar_email()` (área de registro, de Gaston) se eligió borrarlo y no conectarlo a `registrar()`: conectarlo cambiaba qué emails se aceptan (por ejemplo, `a@b` dejaría de ser válido), y eso es una regla de negocio, no un refactoring. Si el grupo quiere esa validación más estricta, se agrega como mejora con su test.
  - Se mantuvieron los accesores que sí se usan (`get_estado`, `set_estado`, `get_responsable`, `set_responsable`, `get_fecha_creacion`, `set_fecha_modificacion`).
  - `proc()` conserva su nombre: lo renombra Gaston (S03).
  - Los comentarios de `iniciar()`, `leer()` y `registrar()` quedan para el Extract Class de consola de Gaston. El de `reporte()` desaparece con el `ReporteService` de Juan.
- **Alternativas consideradas:** comentar el código en lugar de borrarlo. Se descartó porque es otra forma de código muerto: el historial de Git ya guarda la versión anterior.
