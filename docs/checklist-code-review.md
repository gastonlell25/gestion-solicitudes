# Checklist de code review — Sistema de Gestión de Solicitudes Académicas

**Materia:** Metodología de Sistemas II · **Coordinación:** Juan Cruz Leal  
**Versión:** 2026-11-06 · **Estado:** documento de revisión listo para PR; aceptación integral de Fase 5 pendiente.  
**Aplicación:** cada integrante revisa un área ajena. Rotación acordada: Gastón → Gabriel → Juan → Fabri → Gastón (Juan revisa el área de Fabri).

## Criterios verificables

La severidad es una referencia para clasificar observaciones, no implica que todas las reglas sean absolutas. Para cada criterio se registra cumplimiento, archivo y línea, observación, corrección y commit en `docs/code-review.md`.

| ID | Categoría | Qué verificar | Criterio de aceptación | Severidad orientativa |
|---|---|---|---|---|
| CC-01 | Nombres | Clases, métodos y variables describen su intención. | No quedan identificadores crípticos en flujos modificados; las excepciones se explican. | Media |
| CC-02 | Nombres | Estados, tipos y prioridades usan vocabulario consistente. | Representación centralizada en enums/reglas de conversión, sin variantes incompatibles. | Media |
| CC-03 | Funciones | Cada operación tiene una responsabilidad clara. | La lógica de consola, persistencia y dominio no se mezcla sin necesidad. | Alta |
| CC-04 | Funciones | Métodos legibles y de tamaño controlado. | Referencia: unas 20 líneas por función; cualquier excepción se justifica por cohesión. | Media |
| CC-05 | Funciones | Firmas de parámetros entendibles. | Referencia: hasta 3 parámetros funcionales; listas largas justificadas o agrupadas en objeto. | Media |
| CC-06 | Clases / SRP | Consola, modelo, reportes y persistencia mantienen límites claros. | Un cambio en el formato de archivo no obliga a modificar reglas del dominio. | Alta |
| CC-07 | SOLID / DIP e ISP | La persistencia puede sustituirse sin modificar el gestor. | Interfaz específica, inyección de dependencia y contrato de errores coherente. | Alta |
| CC-08 | SOLID / OCP y LSP | Transiciones de estado consistentes y extensibles. | Las reglas están centralizadas y un estado válido respeta el contrato de uso. | Alta |
| CC-09 | Errores | No se silencian errores de archivo ni excepciones sin motivo. | Sin `except:` vacíos en el flujo final; fallos tipificados y comunicados. | Alta |
| CC-10 | Errores | Errores de persistencia no simulan operaciones exitosas. | Archivos dañados no se sobrescriben en silencio y fallos de guardado no se anuncian como éxito. | Alta |
| CC-11 | Duplicación | No se repiten recorridos o reglas que deban mantenerse juntas. | Filtros y reporte reutilizan lógica; no hay fragmentos equivalentes dispersos. | Media |
| CC-12 | Constantes | Plazos, estados y tipos no son literales ambiguos. | Valores del dominio identificables y cambios localizados. | Media |
| CC-13 | Pruebas | Los casos de caracterización T01–T19 están documentados y aislados. | Tests repetibles con fecha fija y datos temporales; correspondencia con `docs/pruebas.md`. | Alta |
| CC-14 | Pruebas | No hay regresiones tras los refactorings. | Suite completa ejecutada en el último commit integrado, 100 % aprobada; diferencias intencionales documentadas. | Alta |
| CC-15 | Documentación | README, decisiones, refactorings, métricas y evidencias corresponden al código. | Enlaces válidos, fichas de cambios, capturas antes/después, registro IA y guía de ejecución. | Media |
| CC-16 | Git / revisión | PRs revisados y tags correspondientes a la versión real. | Revisión con al menos 2 comentarios técnicos reales en línea por PR según guion, respuestas y correcciones; tags en commits correctos. | Alta |

## Criterios de aceptación para cerrar la Fase 5

1. **Pruebas:** suite completa en verde sobre el último `main` integrado; guardar comando, entorno y captura del resultado.
2. **Calidad:** sin observaciones **Altas** abiertas. Toda excepción exige justificación acordada por el grupo en `docs/code-review.md`.
3. **Revisión:** comentarios concretos, con archivo/línea y sugerencia, más respuestas y commits de corrección cuando corresponda. Una revisión aprobatoria sin comentarios técnicos **no sustituye** el requisito del guion.
4. **Trazabilidad:** fichas para cada refactoring; evidencia antes/después real y decisión grupal sobre los cambios intencionales de comportamiento.
5. **Análisis estático:** guardar reporte de Pylint final con versión y comando equivalentes al análisis inicial; comparar métricas y registrar diferencias sin suponer que más advertencias significa necesariamente peor diseño.
6. **Cierre:** registrar quién revisó, fecha, commit evaluado, pendientes y aceptación final; **no marcar como aprobado mientras haya PRs encadenados sin integrar**.

**Alcance académico:** la regla de tamaño de métodos es orientativa, no una afirmación de que todos los métodos necesariamente deban tener 20 líneas. Para la defensa interesa explicar el motivo de cada decisión.
