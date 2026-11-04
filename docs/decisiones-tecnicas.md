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

## Fabri: persistencia y manejo de errores

### S10 - God Class y acoplamiento directo a ArchivoJSON
- **Qué viola:** SRP, porque `GestorSolicitudes` tiene muchas razones para cambiar: el menú, las reglas de negocio, los filtros, el reporte y la persistencia. DIP, porque la lógica de alto nivel crea y usa directamente una clase de bajo nivel (`ArchivoJSON()` en el constructor) y además conoce el formato del JSON (`proc()` y `guardar()`).
- **Qué se propone:** aplicar Extract Class y mover `cargar()`, `proc()`, `guardar()` y `datos_ejemplo()`, junto con `ArchivoJSON`, a una clase `SolicitudRepositorioArchivo`. Después, Introduce Interface: definir `SolicitudRepositorio` (clase abstracta con `abc`) con solo las operaciones que usa el servicio, y que el servicio la reciba por constructor; `main.py` arma las dependencias. Para ISP, la interfaz queda chica y específica; si al implementarla aparecen clientes que solo leen o solo escriben, se separa en una interfaz de lectura y otra de escritura.
- **Por qué:** cambiar la forma de guardar no toca la lógica, y los tests pueden usar un archivo temporal o un repositorio en memoria. Además achica la God Class antes de los refactorings de Gaston y Juan, que es el orden de merge acordado.

### S11 - Manejo de errores pobre
- **Qué viola:** las reglas de Clean Code de manejo de errores: usar excepciones en lugar de códigos de retorno, no ignorar errores con `except:` vacíos y no mezclar la presentación (`print`) con el acceso a datos. Además hay un bug real: si `data/solicitudes.json` está dañado, se pisa con los datos de ejemplo y se pierden los datos.
- **Qué se propone:** crear excepciones propias (`SolicitudNoEncontradaException`, `ResponsableNoEncontradoException`, `PersistenciaException`; el nombre `TransicionInvalidaException` se coordina con Gabriel). El repositorio captura solo excepciones específicas (`FileNotFoundError`, `json.JSONDecodeError`, `OSError`) y las convierte en `PersistenciaException`; solo la consola muestra mensajes. Si el archivo no existe se siguen generando los datos de ejemplo (comportamiento actual), pero si existe y está dañado se informa el error y no se sobrescribe. Ese cambio de comportamiento se registra como mejora intencional y se decide en grupo en `docs/pruebas.md`.
- **Alternativas consideradas:** mantener los códigos pero con constantes con nombre (`RESPONSABLE_INEXISTENTE = -2`). Se descarta porque el error se sigue pudiendo ignorar sin que nadie se entere.
- **Por qué:** un error no puede pasar desapercibido, el mensaje al usuario es claro y siempre igual, y agregar un error nuevo no obliga a tocar cada `if` del menú.
