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
| T01 | Registrar | Registrar solicitud válida con legajo existente | Legajo 10001 (Lucia Benitez, existe); menú: opción 1, tipo 1 (CERTIFICADO), descripción válida, prioridad default | `Solicitud #<id> registrada correctamente`; estado = PENDIENTE; se agrega al archivo de datos | Pasa | Pasa | Gastón |
| T02 | Registrar | Registrar sin descripción | Legajo 10001; tipo 1; descripción vacía | `Error: la descripcion no puede estar vacia.` | Pasa | Pasa | Gastón |
| T03 | Registrar | Registrar con legajo inexistente (pero datos válidos) | Legajo 99999 (no existe); nombre, apellido, email, carrera válidos; tipo 1; descripción válida | `El estudiante no esta registrado...`; `Solicitud #<id> registrada correctamente`; estado = PENDIENTE | Pasa | Pasa | Gastón |
| T04 | Listar | Listar todas las solicitudes cargadas | Menú: opción 6 | `Listado de solicitudes`; se muestran todos los IDs (#1 a #10); `Total: 10 solicitud(es).` | Pasa | Pasa | Gastón |
| T05 | Cambiar estado | Transición válida PENDIENTE → EN_REVISION | Solicitud #1 (PENDIENTE); menú: opción 2, ID 1, nuevo estado `EN_REVISION` | `Estado actualizado: PENDIENTE -> EN_REVISION`; el archivo de datos queda con la solicitud #1 en `EN_REVISION` | Pasa | Pasa | Gabriel |
| T06 | Cambiar estado | Transición válida EN_REVISION → APROBADA | Solicitud #2 (EN_REVISION); menú: opción 2, ID 2, nuevo estado `APROBADA` | `Estado actualizado: EN_REVISION -> APROBADA`; el archivo de datos queda con la solicitud #2 en `APROBADA` | Pasa | Pasa | Gabriel |
| T07 | Cambiar estado | Transición rechazada CERRADA → PENDIENTE | Solicitud #5 (CERRADA); menú: opción 2, ID 5, nuevo estado `PENDIENTE` | `Error: no se puede pasar de CERRADA a PENDIENTE.`; la solicitud #5 sigue en `CERRADA` | Pasa | Pasa | Gabriel |
| T08 | Cambiar estado | Transición rechazada APROBADA → PENDIENTE | Solicitud #4 (APROBADA); menú: opción 2, ID 4, nuevo estado `PENDIENTE` | `Error: no se puede pasar de APROBADA a PENDIENTE.`; la solicitud #4 sigue en `APROBADA` | Pasa | Pasa | Gabriel |
| T09 | Cambiar estado | Transición válida APROBADA → CERRADA | Solicitud #4 (APROBADA); menú: opción 2, ID 4, nuevo estado `CERRADA` | `Estado actualizado: APROBADA -> CERRADA`; el archivo de datos queda con la solicitud #4 en `CERRADA` | Pasa | Pasa | Gabriel |
| T10 | Buscar / filtrar | Estado PENDIENTE | Menú `4`, criterio `1`, `PENDIENTE`, salir `0` | Se muestran cinco solicitudes, IDs 1, 3, 6, 8 y 10 | Pasa (5; IDs 1, 3, 6, 8, 10) | Pasa | Juan |
| T11 | Buscar / filtrar | Tipo CERTIFICADO | Menú `4`, criterio `2`, `CERTIFICADO`, salir `0` | Se muestran tres solicitudes, IDs 1, 5 y 10 | Pasa (3; IDs 1, 5, 10) | Pasa | Juan |
| T12 | Buscar / filtrar | Prioridad ALTA | Menú `4`, criterio `3`, `ALTA`, salir `0` | Se muestran cuatro solicitudes, IDs 2, 3, 6 y 8 | Pasa (4; IDs 2, 3, 6, 8) | Pasa | Juan |
| T13 | Buscar / filtrar | Legajo 10001 | Menú `4`, criterio `4`, `10001`, salir `0` | Se muestran dos solicitudes del legajo, IDs 1 y 6 | Pasa (2; IDs 1, 6) | Pasa | Juan |
| T14 | Buscar / filtrar | Sin resultados | Menú `4`, criterio `4`, `99999`, salir `0` | Mensaje `No se encontraron solicitudes.` y ninguna solicitud listada | Pasa | Pasa | Juan |
| T15 | Reporte | Conteos generales | Menú `5`, salir `0`; fecha fija `2026-10-30` | Total 10; estados 5/2/1/1/1; tipos 3/2/2/2/1; pendientes ALTA 3; vencidas 3 | Pasa (todos los conteos) | Pasa | Juan |
| T16 | Asignar responsable | Asignar un responsable válido | Solicitud #1; menú: opción 3, ID 1, responsable 1 | `Responsable asignado: Laura Quiroga (Alumnado) -> solicitud #1`; el archivo de datos guarda el responsable 1 en la #1 | Pasa | Pasa | Fabri |
| T17 | Asignar responsable | Asignar un responsable inexistente | Solicitud #1; menú: opción 3, ID 1, responsable 9 | `Error: no existe un responsable con ID 9.`; el responsable de la #1 no cambia en el archivo | Pasa | Pasa | Fabri |
| T18 | Persistencia | Guardar y volver a cargar | Sesión 1: registra la #11 (legajo 10003, tipo 4, descripción, prioridad por defecto), le asigna el responsable 2 y sale; sesión 2 (mismo archivo): opción 6 | Se lista `#11 [PENDIENTE] EQUIVALENCIA - Prioridad: MEDIA` con `Responsable: Martin Ferreyra (Secretaria Academica)`; `Total: 11 solicitud(es).` | Pasa | Pasa | Fabri |
| T19 | Persistencia | Archivo de datos inexistente | `ARCHIVO_DATOS` apunta a un archivo que no existe; menú: opción 6 | Se cargan los datos de ejemplo (`Total: 10 solicitud(es).`) y se crea el archivo con 10 solicitudes | Pasa | Pasa | Fabri |

## Cómo verificamos que no hubo regresiones

Los 19 tests (T01–T19) se escribieron **antes** de tocar el código, sobre la versión
`estado-inicial`, y corrieron en verde ahí (columna "Resultado en estado-inicial").
Durante la Fase 3, cada uno de los 4 integrantes corrió la suite completa antes de
commitear cada paso de su refactoring (convención del equipo: "correr los tests antes de
cada commit"), así que si algo rompía el comportamiento externo, se detectaba de
inmediato, en el commit que lo causó, no al final.

Revisamos el historial de `tests/`: **ningún commit de refactoring modificó ninguno de
los 19 tests originales** (`test_gaston_registro.py`, `test_gabriel_estados.py`,
`test_juan_filtros_reportes.py`, `test_fabri_persistencia_responsables.py`). Los 19 casos
corren exactamente igual, sin adaptar ninguna firma ni ningún mensaje esperado, lo que
confirma que el comportamiento observable no cambió.

Sobre la versión final (`main` actual, con los refactors de los 4 integrantes
integrados), la suite completa da **94/94 en verde** (los 19 casos originales + los
tests unitarios/adicionales que cada uno sumó durante su refactor: `test_estado.py`,
`test_tipo_prioridad.py`, `test_normalizacion_datos.py`, `test_juan_modelo_reporte.py`,
`test_fabri_repositorio.py`, `test_fabri_errores.py`, y los 3 casos borde agregados en
`test_gabriel_estados.py` a partir de la revisión de PR de Gastón).

**Dos excepciones documentadas, no regresiones:** los dos bugs que encontró Fabri en S11
(ver tabla abajo) cambian **a propósito** el comportamiento de `estado-inicial` — son
mejoras intencionales acordadas, no efectos secundarios no buscados del refactoring.

**Comando para reproducir:** `python -m pytest tests/ -v`, desde la raíz del repo.

### Comparación de capturas antes/después — Fabri

Se repitieron sobre la versión final las capturas de la Fase 0, con **las mismas entradas**
(`docs/evidencias/antes/entradas_fabri.md`), la misma fecha fija (`FECHA_HOY=2026-10-30`) y
una copia nueva de `data/solicitudes.json`. Se comparó el texto completo de cada consola,
no solo la imagen.

| Qué se probó | Antes | Después | Resultado |
|---|---|---|---|
| Registrar una solicitud válida | `antes_fabri_registrar-valida.png` | `despues_fabri_registrar-valida.png` | Idéntica |
| Registrar sin legajo y sin descripción | `antes_fabri_registrar-datos-faltantes.png` | `despues_fabri_registrar-datos-faltantes.png` | Idéntica |
| Listar todas las solicitudes | `antes_fabri_listar-todas.png` | `despues_fabri_listar-todas.png` | Idéntica |
| Asignar un responsable válido | `antes_fabri_asignar-responsable-valido.png` | `despues_fabri_asignar-responsable-valido.png` | Idéntica |
| Asignar un responsable inexistente | `antes_fabri_asignar-responsable-inexistente.png` | `despues_fabri_asignar-responsable-inexistente.png` | Idéntica |
| Persistencia entre dos sesiones | `antes_fabri_persistencia.png` | `despues_fabri_persistencia.png` | Idéntica |
| Archivo de datos dañado | `antes_fabri_archivo-danado.png` | `despues_fabri_archivo-danado.png` | Mejora intencional (S11) |
| Guardado fallido | `antes_fabri_guardado-fallido.png` | `despues_fabri_guardado-fallido.png` | Mejora intencional (S11) |

Las seis operaciones normales dan exactamente la misma salida que en `estado-inicial`. Solo
cambian los dos casos de error de la tabla de abajo, a propósito.

## Bugs del sistema base encontrados (Fabri, S11)

Al diagnosticar S11 se encontraron dos bugs reales en `estado-inicial`. No los detectan T01–T19
porque esos tests prueban el comportamiento esperado con un archivo de datos sano.

| Bug | Cómo se reproduce | Resultado en `estado-inicial` | Decisión y resultado en la versión refactorizada |
| --- | --- | --- | --- |
| Pérdida silenciosa de datos | El archivo de datos existe pero tiene JSON inválido (por ejemplo, `{ esto no es json`) y se abre el sistema | El sistema arranca con los 10 datos de ejemplo y **sobrescribe el archivo**; se pierde lo que había, sin aviso | Se corrige en el refactoring de S11 (ficha 7): se informa `Error: el archivo de datos ... tiene un formato invalido (linea 1, columna 3).`, el sistema no arranca y el archivo **no se modifica**. Solo se generan los datos de ejemplo si el archivo no existe (T19 sigue igual) |
| Éxito falso al no poder guardar | El archivo es de solo lectura y se asigna un responsable o se cambia un estado | Se muestra `Error: [Errno 13] Permission denied: '...'` y a continuación `Responsable asignado: ...` (o `Estado actualizado: ...`). El cambio queda en memoria y se guarda en la próxima operación que funcione | Se corrige en el refactoring de S11 (ficha 7): `Error: no se pudo guardar el archivo de datos ... (Permission denied). La operacion no se guardo.`, sin mensaje de éxito, y se vuelve al último estado guardado |

Los dos cambios son **mejoras intencionales** del comportamiento externo, a confirmar por el grupo
en la revisión del PR. Los prueba `tests/test_fabri_errores.py`, y sus dos tests de punta a punta
fallan sobre `estado-inicial`. Capturas: `docs/evidencias/antes/antes_fabri_archivo-danado.png` /
`docs/evidencias/despues/despues_fabri_archivo-danado.png` y `antes_fabri_guardado-fallido.png` /
`despues_fabri_guardado-fallido.png`.
