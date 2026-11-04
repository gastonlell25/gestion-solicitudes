| ID | Smell | Evidencia | Ubicación | Impacto | Riesgo de mantenimiento | Prioridad | Principio violado | Refactoring propuesto | Autor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S01 | Long Method | `procesarOpcion()` tiene 80 líneas y mezcla lectura de datos, validación, guardado e impresión. Ver `codigo_gaston_S01.png` | `GestorSolicitudes.java` → `procesarOpcion()`, l. 40–120 | Difícil de leer y de entender; no se puede testear cada parte por separado | Cambiar una parte (por ejemplo, la validación) puede romper otra (el guardado o la impresión) | Alta | SRP; Clean Code: funciones cortas que hacen una sola cosa | Extract Method | Gaston |
| S02 | Long Parameter List | `registrarSolicitud(legajo, nombre, apellido, email, carrera, tipo, descripcion, prioridad, fecha)` recibe 9 parámetros. Ver `codigo_gaston_S02.png` | `GestorSolicitudes.java` → `registrarSolicitud(...)`, l. 130 | Fácil equivocarse en el orden de los parámetros; las llamadas son largas y poco claras | Agregar un dato nuevo obliga a cambiar la firma y todas las llamadas al método | Media | Clean Code: pocos parámetros por función | Introduce Parameter Object | Gaston |
| S03 | Malos nombres | Variables `x`, `lst`, `aux` y método `proc()` que no dicen qué contienen ni qué hacen. Ver `codigo_gaston_S03.png` | `GestorSolicitudes.java` → `proc()` l. 150; `lst` l. 45; `x` l. 62 | Hay que leer todo el código para entender qué representa cada nombre | Alto riesgo de confundir variables al modificar el código | Media | Clean Code: nombres que revelan intención | Rename | Gaston |
| S10 | God Class + acoplamiento directo a la persistencia | `GestorSolicitudes` tiene 544 líneas y 26 métodos: muestra el menú, lee la consola, valida, aplica las reglas de estado, filtra, arma el reporte, calcula vencimientos, convierte JSON ↔ objetos y guarda. Además crea su propio acceso a datos con `self.archivo = ArchivoJSON()`. Ver `codigo_fabri_S10.png` | `src/gestor_solicitudes.py` → clase `GestorSolicitudes`, l. 11–544; `__init__()` l. 17; `cargar()`, `proc()` y `guardar()` l. 466–517. `src/archivo_json.py` → `__init__()` l. 8 | Cualquier cambio (de menú, de regla o de formato del archivo) obliga a tocar la misma clase; no se puede probar la lógica sin leer y escribir el archivo real | Cambiar JSON por otra forma de guardar obliga a modificar el gestor; muchos conflictos de merge porque todos los integrantes tocan el mismo archivo | Alta | SRP; DIP (la lógica depende de una clase concreta de archivo, no de una abstracción) | Extract Class (`SolicitudRepositorioArchivo`) + Introduce Interface (`SolicitudRepositorio`) inyectada por constructor | Fabri |



### S01 - Long Method
![S01 - procesarOpcion()](evidencias/antes/codigo_gaston_S01.png)

### S02 - Long Parameter List
![S02 - registrarSolicitud()](evidencias/antes/codigo_gaston_S02.png)

### S03 - Malos nombres
![S03 - nombres x, lst, proc()](evidencias/antes/codigo_gaston_S03.png)

### S10 - God Class y acoplamiento directo a la persistencia
![S10 - GestorSolicitudes crea ArchivoJSON y conoce el formato del JSON](evidencias/antes/codigo_fabri_S10.png)
