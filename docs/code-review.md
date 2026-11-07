# Code review profesional — SGSA

**Coordinador:** Juan Cruz Leal · **Revisión inicial:** 2026-11-06 · **Estado:** revisión documental independiente lista para PR; no constituye aprobación de los PR de Fabri ni del proyecto final.  
**Base examinada:** `main` en `f089fc38923d9f03223c27d821f9771e86d40d0e` al preparar este paquete; PR #20 (Juan, fusionado) y PR #21–#23 (Fabri, aún sin integrar). Revalidar el commit en GitHub antes de aprobar.  
**Rotación:** Juan revisa el trabajo de Fabri; Gabriel revisa el de Juan.

## Alcance y método

Se contrastaron las consignas de la Fase 5, la estructura de `/docs`, los archivos modificados y las diferencias de los PR. No se dispone todavía de una ejecución de la suite completa **sobre una rama que integre #21, #22 y #23 con #20**. Los resultados de tests indicados por los autores de los PR no sustituyen esa verificación integrada.

Los campos **Cumple**, **Severidad**, **Acción correctiva** y **Commit de corrección** se actualizan después de la revisión y del merge. **Pendiente** no significa que exista un defecto: significa que no hay evidencia suficiente de la versión definitiva.

## Hallazgos de revisión y seguimiento

| ID / ítem | Cumple (sí/no/parcial) | Observación verificable | Severidad | Acción correctiva / criterio de cierre | Responsable | Commit de corrección | Revisor |
|---|---|---|---|---|---|---|---|
| CR-01 / CC-06, CC-07 | Parcial | **PR #21**: GitHub marca conflicto con `main` tras integrarse el PR #20 de filtros/ReporteService. No se puede verificar la integración real hasta reconciliar ambos cambios de `src/gestor_solicitudes.py`. | Alta (bloquea merge) | Actualizar #21 sobre `main` sin perder `ReporteService`, `_filtrar` ni la delegación de vencimientos a `Solicitud`; correr T01–T19 y la suite ampliada. | Fabri, coordinación con Juan | `ac15560` (PR #21; conflictos resueltos en `8fe5420`: se conservan `ReporteService`, `_filtrar` y los vencimientos en `Solicitud`; 94/94 en verde) | Juan |
| CR-02 / CC-09, CC-10 | Pendiente | **PR #22** propone corregir pérdida de datos por JSON corrupto y falsos mensajes de éxito al fallar el guardado; son cambios intencionales respecto de la versión inicial, no solo reorganización interna. | Alta (definición de aceptación) | Registrar acuerdo del grupo, pruebas y evidencias de los dos escenarios; volver a validar tras resolver #21. | Fabri + equipo | Pendiente | Juan |
| CR-03 / CC-09, CC-10 | Parcial | En `src/archivo_json.py` de **PR #22**, la escritura sigue usando `open(..., 'w')`; si el proceso falla después de abrir el archivo, puede quedar truncado. La mejora evita el éxito falso, pero no garantiza escritura atómica. | Media | Valorar escritura a temporal y `os.replace`, o documentar como límite y mejora futura. No cambiar el alcance sin decisión del equipo. | Fabri + equipo | `1071b5c` (documentado como límite conocido y mejora pendiente en `decisiones-tecnicas.md`, S11; sin cambio de código) | Juan |
| CR-04 / CC-15 | No, en `main` revisado | El PR #20 de Juan está fusionado, pero `docs/refactorings.md` todavía no contiene las fichas de S07–S09, sus tres commits y evidencias del diff. Se incluyen fichas independientes en `docs/juan/refactorings-S07-S09.md` para evitar editar ahora el archivo que Fabri modifica en #21–#23. | Media | Fichas J-01/J-02/J-03 ya redactadas en `docs/juan/refactorings-S07-S09.md`; agregar enlaces o consolidarlas en `docs/refactorings.md` al unir el informe, sin duplicar ni borrar las fichas de Fabri. Adjuntar diff y tests reales. | Juan | Pendiente | Gabriel |
| CR-05 / CC-13 | Parcial | Los 19 tests T01–T19 existen en `/tests`, pero en el `main` evaluado `docs/pruebas.md` solo registra T01–T15. El PR #22 incorpora T16–T19. | Media | Confirmar que las cuatro filas queden integradas desde #22; no duplicarlas desde otra rama. | Fabri / Gabriel | `ac15560` (T16–T19 integradas en `docs/pruebas.md` por PR #21) | Juan |
| CR-06 / CC-16 | Pendiente | No se encontraron revisiones publicadas sobre PR #21, #22 ni #23 al momento de esta comprobación. El guion pide revisión con comentarios técnicos concretos en línea. | Media | Dejar al menos dos comentarios genuinos por PR sobre puntos observados; responder y corregir, guardando capturas reales del intercambio. | Juan revisa; Fabri responde | Pendiente | Juan |
| CR-07 / CC-15 | Parcial | `docs/registro-ia.md` en `main` recoge usos de Fabri, pero faltan verificaciones de aportes/evidencias de los restantes integrantes. | Media | Cada miembro registra sus intervenciones reales, adjunta los PDFs según el guion y valida enlaces. | Cada integrante; Fabri consolida | Pendiente | Juan |
| CR-08 / CC-14, CC-16 | Pendiente | **PR #23** depende de #22, que depende de #21. Los resultados de tests publicados por Fabri (82/82) corresponden a sus ramas y deben comprobarse sobre la versión efectivamente fusionada. | Alta (cierre de Fase 3) | Fusionar en orden #21→#22→#23, resolver conflictos, correr suite y conservar evidencia después. | Fabri + equipo | `ac15560` (#22 y #23 se mergearon dentro de #21 y entraron juntos a `main`; suite 94/94 sobre `main`) | Juan |
| CR-09 / CC-02, CC-08 | Sí | **PR #17 (Gabriel):** `src/modelos/estado.py`. Enum `Estado` centraliza las transiciones permitidas en `_TRANSICIONES_PERMITIDAS` (dict con frozensets). Métodos `puede_pasar_a()` y `es_final()` encapsulan lógica que antes estaba dispersa en if/elif del gestor. CC-08 (OCP/LSP) cumplido: agregar un estado nuevo no requiere modificar consola ni gestor. | Baja | Nada, se acepta. Excelente aplicación de OCP. | Gabriel | — | Gastón |
| CR-10 / CC-01, CC-02 | Sí | **PR #17:** Nombres consistentes: `Estado.PENDIENTE`, `Estado.EN_REVISION`, etc. Excepciones tipificadas: `EstadoInvalidoException` (valor inválido) vs `TransicionInvalidaException` (transición no permitida). CC-01 cumplido sin ambigüedad. | Baja | Nada, excelente. | Gabriel | — | Gastón |
| CR-11 / CC-04, CC-12 | Sí | **PR #17:** Métodos pequeños (4-7 líneas). Método `from_str()` normaliza entrada (strip, upper, replace) de forma centralizada. Constantes en enum, no strings mágicos. CC-04 y CC-12 cumplidos. | Baja | Nada. Modelo limpio. | Gabriel | — | Gastón |
| CR-16 / CC-05, CC-15 | No | **Área de Gastón (registro y consola), revisada sobre `main` en `5b7a315`.** El Introduce Parameter Object, que es obligatorio, no está en el código: `SolicitudService.registrar_solicitud()` recibe 9 parámetros (`src/servicios/solicitud_service.py:37`) y `GestorSolicitudes.registrar()` la llama con 9 (`src/gestor_solicitudes.py:193`). `DatosSolicitud` (`src/modelos/datos_solicitud.py`) no se usa en ningún archivo. El PR #15 sí lo aplicó (`dbfd73a`, 20:33), pero el PR #14 se mergeó después (`1480b4e`, 20:40) y volvió a la firma de 9 parámetros. La ficha 4 de `docs/refactorings.md` lo da por aplicado y cita el commit `2aa00a0`, que no existe en el repositorio. | Alta (refactoring obligatorio; bloquea el tag `etapa-refactoring`) | Reaplicarlo sobre `SolicitudService`: `registrar_solicitud(self, datos: DatosSolicitud)`, con `registrar()` armando el objeto. Actualizar el hash de la ficha 4 y correr T01–T04. | Gastón | Pendiente | Fabri |
| CR-17 / CC-05 | Parcial | `mostrar_resultado_registro(id_solicitud, legajo, apellido, nombre, tipo, prioridad, fecha)` tiene 7 parámetros (`src/gestor_solicitudes.py:266`); son los mismos datos que agruparía `DatosSolicitud`. | Media | Con CR-16 resuelta, recibir `(id_solicitud, datos)`. | Gastón | Pendiente | Fabri |
| CR-18 / CC-01 | Parcial | El Rename quedó parcial en el área: `flag` en el bucle del menú (`src/gestor_solicitudes.py:31`), `id` como parámetro tapa la función de Python (`src/servicios/solicitud_service.py:55, 86, 97`), `n` (`:89`) y recorridos por índice `for i in range(len(...))` (`solicitud_service.py:40, 47, 75, 92`; `gestor_solicitudes.py:121, 162, 172, 213`). | Baja | `ejecutando`, `id_solicitud`, `numero` e iterar directo (`for estudiante in self.estudiantes`). | Gastón | Pendiente | Fabri |
| CR-19 / CC-11, CC-06 | Parcial | La búsqueda de estudiante por legajo está duplicada: la consola recorre `self.servicio.estudiantes` en `cargar_datos_estudiante()` (`src/gestor_solicitudes.py:213–220`) y el servicio repite el mismo recorrido en `registrar_solicitud()` (`src/servicios/solicitud_service.py:40–42`). Además, la consola lee directamente las listas internas del servicio. | Media | Agregar `SolicitudService.buscar_estudiante(legajo)` y usarlo en los dos lugares. | Gastón | Pendiente | Fabri |
| CR-20 / CC-12, CC-06 | Parcial | `_hoy()` está marcado como privado, pero la consola lo llama 4 veces (`src/gestor_solicitudes.py:192, 281, 283, 294`) y el método importa `os` adentro (`src/servicios/solicitud_service.py:127`). Quedan literales de estado en el servicio: `"PENDIENTE"` (`:50`) y `"CERRADA"` (`:80`) en vez de `Estado`. | Baja | Hacerlo público (`hoy()`), mover el import arriba y usar `Estado.PENDIENTE.value` / `Estado.CERRADA.value`. | Gastón | Pendiente | Fabri |
| CR-21 / CC-15 | Parcial | En `docs/refactorings.md` hay dos fichas con el número 9: "Remove Dead Code" (Fabri) y "Rename" (Gastón). | Baja | Renumerar las fichas de Gastón como 10 y 11. | Gastón | Pendiente | Fabri |
| CR-22 / CC-03, CC-06 | Sí | **PR #25 (Gastón):** la extracción de `SolicitudService` separa bien consola y lógica: el servicio no tiene ningún `print` ni `input`, y `registrar()` (`src/gestor_solicitudes.py:176–194`) quedó partido en pasos con nombre (`leer_y_validar_legajo`, `cargar_datos_estudiante`, `leer_y_mapear_tipo`, …). Los 94 tests pasan sin haber adaptado ningún caso de T01–T19. | — | Ninguna. | — | — | Fabri |

## Observaciones positivas respaldadas por código y commits

- **PR #20 de Juan:** `_filtrar()` concentra el recorrido; los cuatro métodos públicos mantienen sus contratos. `Solicitud` incorpora cálculo de días y vencimiento con fecha explícita; `ReporteService` se ocupa del cálculo del informe y el gestor conserva la impresión. Los tests T10–T15 y los unitarios adicionales están en el repositorio.
- **PR #21 de Fabri:** propone una interfaz específica (`cargar`, `guardar`) y un repositorio de archivo inyectable; añade test con repositorio en memoria. Se valora como diseño, pero sigue pendiente la reconciliación con `main`.
- **PR #22 de Fabri:** ajusta la interfaz `guardar()` para lanzar excepción en lugar de devolver un `bool`, preservando coherencia entre contrato y nueva implementación; añade tests de error.
- **PR #23 de Fabri:** retira métodos sin uso de `Solicitud` y código muerto del gestor; el diff publicado está acotado al smell S12.

## Comentarios propuestos para revisión en GitHub (todavía no publicados)

Los siguientes textos son **borradores de feedback**, no comentarios que ya consten en GitHub. Se publican en la vista *Files changed* de cada PR cuando su base sea actual y se haya comprobado la línea:

- **PR #21, `src/gestor_solicitudes.py` (zona de imports, `cargar` y `guardar`):** «El PR tiene conflicto con el `main` donde ya está #20. Al resolverlo, mantengamos `ReporteService`, `_filtrar()` y la delegación a `Solicitud`, junto con la nueva inyección de `SolicitudRepositorio`. ¿Podés mostrar la suite completa y el diff del archivo ya reconciliado?»
- **PR #21, `tests/test_fabri_repositorio.py`:** «El test del repositorio en memoria comprueba la sustitución de persistencia, algo valioso para DIP. Después de actualizar la rama, ¿podemos verificar su ejecución junto con T10–T15 y las pruebas de antigüedad/reporte? Así comprobamos la compatibilidad con el cambio de Juan.»
- **PR #22, `src/archivo_json.py` (`escribir`):** «Con `open(..., 'w')` hay riesgo de truncamiento si una escritura falla a mitad. ¿Lo documentamos expresamente como límite o conviene añadir escritura atómica (archivo temporal y reemplazo)? No es necesario ampliar alcance sin decisión del grupo.»
- **PR #22, `tests/test_fabri_errores.py`:** «El caso de archivo solo lectura depende de permisos del sistema y puede comportarse distinto en Windows. Sería útil verificar también el camino de error con un objeto que falle de forma controlada, para que el test sea reproducible.»
- **PR #23, `src/modelos/solicitud.py`:** «La eliminación de accesores sin uso está acotada al diagnóstico S12. Después de integrar #21 y #22, confirmemos con búsqueda y suite completa que ninguna nueva capa de repositorio los utiliza.»
- **PR #23, `src/gestor_solicitudes.py`:** «Se elimina `validar_email()` y `exportar_csv()` para quitar código sin llamadas. ¿Podés confirmar que la validación del registro sigue siendo la misma (en particular los emails aceptados) y adjuntar la suite después de actualizar la rama contra `main`?»

## Métricas y evidencias

| Métrica | Antes (`estado-inicial`) | Después (versión final) |
|---|---|---|
| Pylint | 7,08/10 | **Pendiente de medir; ejecutar `herramientas/validar_juan_intermedio.py`** |
| Incidencias Pylint | 161: 115 de convención, 12 advertencias y 34 refactorizaciones | **Pendiente de medir; ejecutar `herramientas/validar_juan_intermedio.py`** |
| Clase más extensa | Requiere verificar con mismo procedimiento AST en ambas revisiones | **Pendiente de medir; ejecutar `herramientas/validar_juan_intermedio.py`** |
| Método más extenso | Requiere verificar con mismo procedimiento AST en ambas revisiones | **Pendiente de medir; ejecutar `herramientas/validar_juan_intermedio.py`** |
| Máximo de parámetros | Requiere verificar con mismo procedimiento AST en ambas revisiones | **Pendiente de medir; ejecutar `herramientas/validar_juan_intermedio.py`** |
| Duplicación | Cuatro métodos de filtrado repetidos (S07) | Consolidación incluida en PR #20, revisión final pendiente |
| Pruebas | T01–T19 documentadas como pruebas de caracterización; evidencia inicial del equipo | **Pendiente de comprobar con evidencia de ejecución sobre `main` actual** |

Para que el resultado sea comparable, el reporte final debe utilizar el mismo alcance y versión de Pylint, o aclarar diferencias de versión. No se debe afirmar que el análisis de 7,08/10 corresponde a la versión actual.

## Cierre y sign-off (completar después de la integración)

- [ ] PR #21, #22 y #23 fusionados tras revisión y correcciones.
- [ ] Revisión técnica de Juan sobre el área Fabri con comentarios en línea, respuestas y commits.
- [ ] Suite completa final en verde, evidencias de consola antes/después y cambios intencionales aprobados.
- [ ] Pylint final y comparación de métricas.
- [ ] Sin observaciones Altas abiertas; pendientes aceptados y justificados.
- [ ] Revisión del PR de documentación de code review por Gabriel.
- [ ] Capturas de comentarios y correcciones en `docs/evidencias/review/`.
- [ ] `docs/refactorings.md`, `docs/pruebas.md`, registro de IA y tags completos.

**Conclusión:** la documentación de code review de Juan está lista para revisión por Gabriel como PR independiente. La aprobación integral del proyecto sigue condicionada a la integración de Fabri, las métricas finales y las evidencias de revisión. Esta sección debe actualizarse a la revisión final, no usarse como aceptación anticipada.

## Aportes propios incorporados en este PR independiente

- Checklist profesional de 16 criterios: `docs/checklist-code-review.md`.
- Registro técnico de observaciones y criterios de cierre: este documento.
- Tres fichas de refactoring fusionado de Juan: `docs/juan/refactorings-S07-S09.md` (PR #20).
- Decisiones y alternativas de Juan: `docs/juan/decisiones-S07-S09.md`.
- Pruebas y análisis intermedios: se anexan **solo si se ejecutan realmente** sobre el commit de este PR y se registra la salida.

Esto **no** es una aprobación de los PR #21–#23 ni un sign-off grupal. Cada integrante sigue siendo responsable de sus cambios y evidencias.
