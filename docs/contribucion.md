# Participación del equipo

Generado el 2026-11-06 a partir de `git log`/`git shortlog -sn` sobre `main` y de la lista de PRs de GitHub (`gh pr list --state all`). Se vuelve a generar antes del tag final.

| Integrante | Área | Refactorings | PRs abiertos | PRs revisados en GitHub | Apartados del informe | Commits en `main` |
|---|---|---|---|---|---|---|
| Gastón Lell | Registro y consola | Extract Method, Introduce Parameter Object, Extract Class (SolicitudService), Rename | 8 (#1, #2, #8, #11, #14, #15, #16, #25) | 3 (#9, #10, #17) | 1, 2, 3, 4, 5, 6, 7, 10 (grupal) y unificación | 13 |
| Gabriel Lovera | Estados, tipos y prioridades | Replace Conditional with Polymorphism, Replace Magic String with Enum (×2) | 6 (#9, #10, #17, #18, #26, #27) | 4 (#7, #13, #14, #15) | 5, 6, 7, 8 y 10 | 17 |
| Juan Cruz Leal | Filtros y reporte | Move Method, consolidar filtros, Extract Class (ReporteService) | 5 (#7, #13, #19, #20, #24) | 6 (#3, #4, #5, #6, #12, #27) | 5, 6, 7, 8 (métricas), 9 y 10 | 4 |
| Adriel López (Fabri) | Persistencia y manejo de errores | Extract Class (repositorio), Introduce Interface, Replace Error Code with Exception (×2), Remove Dead Code | 11 (#3, #4, #5, #6, #12, #21, #22, #23, #28, #29, #30) | 5 (#1, #2, #8, #11, #25) | 5, 6, 7, 8, 9, 10 y 11 | 13 |

**Cómo leer los commits:** varios PRs se mergearon con *squash*, que junta todos los commits de la rama en uno solo. Por eso la cantidad en `main` es menor que la cantidad de commits hechos en cada rama.

## `git shortlog -sn main`

```
        13	gastonlell25
        12	Gabriel
         7	Adriel Lopez
         6	Fabri404
         5	Gabriel Lovera
         4	Juan Cruz Leal
```
