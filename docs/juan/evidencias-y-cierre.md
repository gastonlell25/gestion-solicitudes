# Evidencias y cierre de Juan — estado intermedio

**Proyecto:** Sistema de Gestión de Solicitudes Académicas · **Responsable:** Juan Cruz Leal.

El PR #20 de S07–S09 y el PR #13 de T10–T15 están integrados en `main`. Este documento detalla cómo se completan las evidencias del área **sin modificar el trabajo de los compañeros**. No supone que estén fusionados los PR #21, #22 y #23 de Fabri.

## Capturas y comparación funcional

| Operación | Captura anterior existente en `main` | Captura posterior a realizar | Comprobación |
|---|---|---|---|
| Filtrar estado PENDIENTE | `docs/evidencias/antes/antes_juan_estado.png` | `docs/evidencias/despues/despues_juan_estado.png` | Cinco solicitudes: IDs 1, 3, 6, 8 y 10 (T10) |
| Filtrar tipo CERTIFICADO | `docs/evidencias/antes/antes_juan_tipo.png` | `docs/evidencias/despues/despues_juan_tipo.png` | Tres solicitudes: IDs 1, 5 y 10 (T11) |
| Filtrar prioridad ALTA | `docs/evidencias/antes/antes_juan_prioridad.png` | `docs/evidencias/despues/despues_juan_prioridad.png` | Cuatro solicitudes: IDs 2, 3, 6 y 8 (T12) |
| Filtrar legajo 10001 | `docs/evidencias/antes/antes_juan_legajo.png` | `docs/evidencias/despues/despues_juan_legajo.png` | Dos solicitudes: IDs 1 y 6 (T13) |
| Buscar sin coincidencias | `docs/evidencias/antes/antes_juan_sin_resultados.png` | `docs/evidencias/despues/despues_juan_sin_resultados.png` | Mensaje sin solicitudes (T14) |
| Reporte general | `docs/evidencias/antes/antes_juan_reporte.png` | `docs/evidencias/despues/despues_juan_reporte.png` | Totales de T15, incluidos pendientes de prioridad alta y vencidas |

Las capturas **después** se deben realizar realmente sobre el commit del PR. No sustituirlas por capturas del estado inicial ni fabricarlas. Usar siempre `FECHA_HOY=2026-10-30` y una copia temporal de los datos de ejemplo para resultados repetibles.

## Pruebas y métricas

- Tests de Juan: `python -m pytest tests/test_juan_filtros_reportes.py tests/test_juan_modelo_reporte.py -v`.
- Suite completa: `python -m pytest tests/ -v` (el número puede superar los 19 casos originales, porque otros compañeros añadieron pruebas unitarias).
- Análisis Pylint anterior (archivo ya en `main`): `docs/evidencias/analisis/antes_juan_pylint_reporte.txt`, **7,08/10 y 161 observaciones**; la versión registrada fue Pylint 4.1.3 en Python 3.14. El alcance y las versiones deben compararse cuidadosamente.
- Análisis **intermedio**, a ejecutar: `herramientas/validar_juan_intermedio.py` en este paquete, que genera informes en `docs/evidencias/analisis/` con el prefijo `intermedio_juan_`.
- Las métricas **finales** y la captura de suite definitiva se repiten después del merge de #21–#23 y las correcciones de code review.

## Para el informe y video

- Apartado 5: tres smells S07–S09 y comparación con las capturas de la versión inicial.
- Apartado 6: SRP, DRY, cohesión, delegación del dominio y decisiones alternativas.
- Apartado 7: fichas J-01, J-02 y J-03 de `docs/juan/refactorings-S07-S09.md`, con hashes reales y capturas del diff del PR #20.
- Apartado 8: T10–T15, tests del modelo y reporte, comparativa inicial/intermedia/final.
- Apartado 9: checklist de 16 criterios, observaciones del área Fabri, comentarios reales de GitHub, respuestas y correcciones cuando existan.
- Apartado 10: aprendizajes, límites y mejoras futuras, sin decir que el código quedó aceptado mientras existan hallazgos pendientes.
- Anexo: registrar el uso de ChatGPT y exportar evidencia PDF conforme al acuerdo del equipo. El registro central de IA se consolida luego en `docs/registro-ia.md` para no pisar cambios de Fabri.

**Nota de integración:** estas fichas se redactan como archivos propios de Juan, de forma deliberada. El equipo puede enlazarlas desde los documentos globales y unificar el informe al final, evitando conflictos con `docs/refactorings.md` y `docs/decisiones-tecnicas.md` de los PR de Fabri.
