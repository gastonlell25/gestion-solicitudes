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
