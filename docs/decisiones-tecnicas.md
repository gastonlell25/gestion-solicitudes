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