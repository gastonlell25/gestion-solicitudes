# Pruebas de caracterización

Tests de punta a punta, escritos antes del refactoring, sobre la versión `estado-inicial`.
Cada test simula la entrada del menú por consola (vía `subprocess`) y usa una copia
temporal de `data/solicitudes.json`, nunca el archivo real, para que cada corrida arranque
igual. Sirven para comprobar que después de refactorizar, el comportamiento externo del
sistema no cambió, por lo cual si siguen en verde sobre la versión final, no hubo regresiones.

**Framework:** pytest. Lo instala quien vaya a correr la suite (ver "Pruebas" en el
README para la instalación con entorno virtual).

**Comando único para correr toda la suite** (desde la raíz del repo):

```bash
python -m pytest tests/ -v
```

## Por qué pytest

Seleccionamos este framework porque es el estándar de facto en Python, una de las
opciones más usadas y mejor documentadas. Nos permite:
- Escribir los tests como funciones simples con `assert`, sin heredar de una clase ni
  escribir boilerplate de `setUp`/`tearDown`.
- Usar de fábrica la fixture `tmp_path`, que da un directorio temporal único por test —
  es justo lo que se necesita para aislar cada corrida con su propia copia de
  `data/solicitudes.json` sin tocar el archivo real ni limpiar nada a mano.

## Cómo se simula la entrada de consola

Se evaluaron dos formas de probar un programa que lee con `input()`:

1. **Mockear `input()`** (`unittest.mock.patch("builtins.input", ...)`): más rápido,
   pero obliga a importar el módulo y llamar directamente a sus funciones internas. Un
   test así se acopla a la implementación (por ejemplo, al método `leer()` del gestor) y
   se rompe con refactors que no cambian el comportamiento, solo la estructura interna —
   justo lo que estas pruebas de caracterización no quieren.
2. **Correr el programa como subproceso real** (`subprocess.run`, pasándole las entradas
   del menú por `stdin` con el parámetro `input=` y capturando `stdout`): prueba el
   sistema exactamente como lo usa una persona real, de punta a punta, sin conocer nada
   de su implementación interna. Es un poco más lento, pero sigue valiendo sin cambios
   después de cualquier refactoring, mientras el comportamiento observable no cambie.

Se eligió la opción 2 por ese motivo. Las variables de entorno `FECHA_HOY` (fecha fija,
para resultados reproducibles) y `ARCHIVO_DATOS` (ruta del archivo de datos temporal) ya
las soporta el sistema (ver README), así que los tests las usan para no depender de la
fecha real ni tocar `data/solicitudes.json`.

| ID | Operación | Descripción | Entrada | Resultado esperado | Resultado en estado-inicial | Resultado en versión final | Autor |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T01 | Registrar | Registrar solicitud válida con legajo existente | Legajo 10001 (Lucia Benitez, existe); menú: opción 1, tipo 1 (CERTIFICADO), descripción válida, prioridad default | `Solicitud #<id> registrada correctamente`; estado = PENDIENTE; se agrega al archivo de datos | Pasa | Pendiente (Fase 4) | Gastón |
| T02 | Registrar | Registrar sin descripción | Legajo 10001; tipo 1; descripción vacía | `Error: la descripcion no puede estar vacia.` | Pasa | Pendiente (Fase 4) | Gastón |
| T03 | Registrar | Registrar con legajo inexistente (pero datos válidos) | Legajo 99999 (no existe); nombre, apellido, email, carrera válidos; tipo 1; descripción válida | `El estudiante no esta registrado...`; `Solicitud #<id> registrada correctamente`; estado = PENDIENTE | Pasa | Pendiente (Fase 4) | Gastón |
| T04 | Listar | Listar todas las solicitudes cargadas | Menú: opción 6 | `Listado de solicitudes`; se muestran todos los IDs (#1 a #10); `Total: 10 solicitud(es).` | Pasa | Pendiente (Fase 4) | Gastón |
| T05 | Cambiar estado | Transición válida PENDIENTE → EN_REVISION | Solicitud #1 (PENDIENTE); menú: opción 2, ID 1, nuevo estado `EN_REVISION` | `Estado actualizado: PENDIENTE -> EN_REVISION`; el archivo de datos queda con la solicitud #1 en `EN_REVISION` | Pasa | Pendiente (Fase 4) | Gabriel |
| T06 | Cambiar estado | Transición válida EN_REVISION → APROBADA | Solicitud #2 (EN_REVISION); menú: opción 2, ID 2, nuevo estado `APROBADA` | `Estado actualizado: EN_REVISION -> APROBADA`; el archivo de datos queda con la solicitud #2 en `APROBADA` | Pasa | Pendiente (Fase 4) | Gabriel |
| T07 | Cambiar estado | Transición rechazada CERRADA → PENDIENTE | Solicitud #5 (CERRADA); menú: opción 2, ID 5, nuevo estado `PENDIENTE` | `Error: no se puede pasar de CERRADA a PENDIENTE.`; la solicitud #5 sigue en `CERRADA` | Pasa | Pendiente (Fase 4) | Gabriel |
| T08 | Cambiar estado | Transición rechazada APROBADA → PENDIENTE | Solicitud #4 (APROBADA); menú: opción 2, ID 4, nuevo estado `PENDIENTE` | `Error: no se puede pasar de APROBADA a PENDIENTE.`; la solicitud #4 sigue en `APROBADA` | Pasa | Pendiente (Fase 4) | Gabriel |
| T09 | Cambiar estado | Transición válida APROBADA → CERRADA | Solicitud #4 (APROBADA); menú: opción 2, ID 4, nuevo estado `CERRADA` | `Estado actualizado: APROBADA -> CERRADA`; el archivo de datos queda con la solicitud #4 en `CERRADA` | Pasa | Pendiente (Fase 4) | Gabriel |
| T10 | Buscar / filtrar | Estado PENDIENTE | Menú `4`, criterio `1`, `PENDIENTE`, salir `0` | Se muestran cinco solicitudes, IDs 1, 3, 6, 8 y 10 | Pasa (5; IDs 1, 3, 6, 8, 10) | Pendiente (Fase 4) | Juan |
| T11 | Buscar / filtrar | Tipo CERTIFICADO | Menú `4`, criterio `2`, `CERTIFICADO`, salir `0` | Se muestran tres solicitudes, IDs 1, 5 y 10 | Pasa (3; IDs 1, 5, 10) | Pendiente (Fase 4) | Juan |
| T12 | Buscar / filtrar | Prioridad ALTA | Menú `4`, criterio `3`, `ALTA`, salir `0` | Se muestran cuatro solicitudes, IDs 2, 3, 6 y 8 | Pasa (4; IDs 2, 3, 6, 8) | Pendiente (Fase 4) | Juan |
| T13 | Buscar / filtrar | Legajo 10001 | Menú `4`, criterio `4`, `10001`, salir `0` | Se muestran dos solicitudes del legajo, IDs 1 y 6 | Pasa (2; IDs 1, 6) | Pendiente (Fase 4) | Juan |
| T14 | Buscar / filtrar | Sin resultados | Menú `4`, criterio `4`, `99999`, salir `0` | Mensaje `No se encontraron solicitudes.` y ninguna solicitud listada | Pasa | Pendiente (Fase 4) | Juan |
| T15 | Reporte | Conteos generales | Menú `5`, salir `0`; fecha fija `2026-10-30` | Total 10; estados 5/2/1/1/1; tipos 3/2/2/2/1; pendientes ALTA 3; vencidas 3 | Pasa (todos los conteos) | Pendiente (Fase 4) | Juan |
| T16 | Asignar responsable | Asignar un responsable válido | Solicitud #1; menú: opción 3, ID 1, responsable 1 | `Responsable asignado: Laura Quiroga (Alumnado) -> solicitud #1`; el archivo de datos guarda el responsable 1 en la #1 | Pasa | Pendiente (Fase 4) | Fabri |
| T17 | Asignar responsable | Asignar un responsable inexistente | Solicitud #1; menú: opción 3, ID 1, responsable 9 | `Error: no existe un responsable con ID 9.`; el responsable de la #1 no cambia en el archivo | Pasa | Pendiente (Fase 4) | Fabri |
| T18 | Persistencia | Guardar y volver a cargar | Sesión 1: registra la #11 (legajo 10003, tipo 4, descripción, prioridad por defecto), le asigna el responsable 2 y sale; sesión 2 (mismo archivo): opción 6 | Se lista `#11 [PENDIENTE] EQUIVALENCIA - Prioridad: MEDIA` con `Responsable: Martin Ferreyra (Secretaria Academica)`; `Total: 11 solicitud(es).` | Pasa | Pendiente (Fase 4) | Fabri |
| T19 | Persistencia | Archivo de datos inexistente | `ARCHIVO_DATOS` apunta a un archivo que no existe; menú: opción 6 | Se cargan los datos de ejemplo (`Total: 10 solicitud(es).`) y se crea el archivo con 10 solicitudes | Pasa | Pendiente (Fase 4) | Fabri |
