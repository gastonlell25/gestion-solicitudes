# Capturas del "antes" — Fabri

Capturas de la consola sobre el estado inicial del sistema. Para que la comparación con el "después" (Fase 4) sea
directa, las capturas `despues_fabri_*.png` se sacan **con estas mismas entradas** y el mismo nombre de archivo,
cambiando solo el prefijo.

**Preparación (igual para todas):** se trabaja sobre una copia de los datos para no modificar `data/solicitudes.json`
y se fija la fecha para que los días transcurridos y los vencimientos den siempre lo mismo.

```bash
DATOS=$(mktemp --suffix=.json) && cp data/solicitudes.json $DATOS
FECHA_HOY=2026-10-30 ARCHIVO_DATOS=$DATOS python3 src/main.py
```

| Captura | Qué se prueba | Entradas (en orden, `⏎` = Enter vacío) |
|---|---|---|
| [antes_fabri_registrar-valida.png](antes_fabri_registrar-valida.png) | Registrar una solicitud válida de un estudiante existente con la prioridad por defecto | `1`, `10001`, `1`, `Certificado de alumno regular para tramite de beca`, `⏎`, `0` |
| [antes_fabri_registrar-datos-faltantes.png](antes_fabri_registrar-datos-faltantes.png) | Registrar sin legajo y luego sin descripción: el sistema rechaza ambos | `1`, `⏎`, `1`, `10002`, `1`, `⏎`, `0` |
| [antes_fabri_listar-todas.png](antes_fabri_listar-todas.png) | Listar las 10 solicitudes de ejemplo con días y vencimiento | `6`, `0` |
| [antes_fabri_asignar-responsable-valido.png](antes_fabri_asignar-responsable-valido.png) | Asignar la solicitud #1 al responsable 1 (Alumnado) | `3`, `1`, `1`, `0` |
| [antes_fabri_asignar-responsable-inexistente.png](antes_fabri_asignar-responsable-inexistente.png) | Asignar la solicitud #1 a un responsable que no existe (ID 9) | `3`, `1`, `9`, `0` |
| [antes_fabri_persistencia.png](antes_fabri_persistencia.png) | Persistencia: se registra la #11 y se le asigna responsable, se cierra el programa, se vuelve a abrir con el mismo archivo y la #11 sigue con su responsable | Sesión 1: `1`, `10003`, `4`, `Equivalencia de Fisica I aprobada en otra facultad`, `⏎`, `3`, `11`, `2`, `0` — Sesión 2: `6`, `0` |
