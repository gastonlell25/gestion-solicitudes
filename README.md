# Sistema de Gestión de Solicitudes Académicas

Trabajo Práctico Integrador — Metodología de Sistemas II (UTN TUPaD).

Aplicación de consola que permite a estudiantes registrar solicitudes académicas
(certificados, cambios de comisión, revisiones de nota, equivalencias, etc.),
clasificarlas por tipo, prioridad y estado, asignarlas a un responsable de área,
consultarlas y obtener un reporte resumido.

## Requisitos

- Python 3.10 o superior (probado con Python 3.12).
- No requiere dependencias externas.

## Instalación y uso

```bash
git clone <url-del-repositorio>
cd tpi-gestion-solicitudes
python3 src/main.py
```

En Windows: `python src\main.py`.

El sistema muestra un menú numérico:

```
==============================================
 SISTEMA DE GESTION DE SOLICITUDES ACADEMICAS
==============================================
1. Registrar solicitud
2. Cambiar estado de una solicitud
3. Asignar responsable
4. Buscar / filtrar solicitudes
5. Reporte basico
6. Listar todas las solicitudes
0. Salir
Opcion:
```

### Variables de entorno opcionales

| Variable        | Uso                                                                                   |
|-----------------|---------------------------------------------------------------------------------------|
| `FECHA_HOY`     | Fija la fecha actual del sistema (formato `AAAA-MM-DD`). Útil para obtener salidas reproducibles. |
| `ARCHIVO_DATOS` | Ruta alternativa del archivo de datos (por defecto `data/solicitudes.json`).          |

Ejemplo de ejecución reproducible sin modificar los datos originales:

```bash
cp data/solicitudes.json /tmp/datos.json
FECHA_HOY=2026-10-30 ARCHIVO_DATOS=/tmp/datos.json python3 src/main.py
```

## Funcionalidades

1. **Registrar solicitud**: pide el legajo del estudiante (si no existe, solicita sus datos),
   el tipo, la descripción y la prioridad. Si no se indica prioridad se asigna una por defecto
   según el tipo. Toda solicitud nueva se crea en estado `PENDIENTE`.
2. **Cambiar estado**: permite mover una solicitud entre `PENDIENTE`, `EN_REVISION`, `APROBADA`,
   `RECHAZADA` y `CERRADA`, respetando las reglas:
   - una solicitud `CERRADA` no puede cambiar de estado;
   - una solicitud `APROBADA` o `RECHAZADA` solo puede pasar a `CERRADA`.
3. **Asignar responsable**: asigna la solicitud a un responsable de Alumnado,
   Secretaría Académica o Bedelía (no se permite sobre solicitudes cerradas).
4. **Buscar / filtrar**: por estado, tipo, prioridad o legajo.
5. **Reporte básico**: cantidad de solicitudes por estado, por tipo, pendientes de prioridad
   alta y solicitudes vencidas.
6. **Listar todas las solicitudes**, indicando los días transcurridos desde su creación
   y si están vencidas.

Una solicitud pendiente o en revisión se considera **vencida** cuando supera el plazo
de su prioridad: 3 días (ALTA), 7 días (MEDIA) o 15 días (BAJA).

## Persistencia

Los datos se guardan en `data/solicitudes.json` después de cada operación que modifica
información, y se cargan al iniciar el programa. Si el archivo no existe, se regenera
con los datos de ejemplo (5 estudiantes, 3 responsables y 10 solicitudes).
Todos los datos de ejemplo son **ficticios**.

## Estructura del proyecto

```
src/
  main.py                  punto de entrada
  gestor_solicitudes.py    lógica principal del sistema
  archivo_json.py          lectura/escritura del archivo de datos
  modelos/
    estudiante.py
    responsable.py
    solicitud.py
data/
  solicitudes.json         datos persistidos
docs/                      documentación del TPI
```

## Pruebas

El sistema cuenta con tests de caracterización escritos antes del refactoring, para
verificar que el comportamiento externo no cambie entre la versión inicial y la versión
final. Son tests de punta a punta: ejecutan `src/main.py` simulando la entrada del menú
por consola y comparan la salida, usando siempre una copia temporal del archivo de datos
(nunca `data/solicitudes.json`).

Instalación (se recomienda un entorno virtual):

```bash
python -m venv .venv
source .venv/bin/activate      # En Windows: .venv\Scripts\Activate.ps1
pip install pytest
```

Comando único para correr toda la suite:

```bash
python -m pytest tests/ -v
```

El detalle de los 19 casos de prueba (operación, entrada, resultado esperado y resultado
obtenido en cada versión) está en [`docs/pruebas.md`](docs/pruebas.md).

## Tecnologías

- Python 3, solo librería estándar (`json`, `os`, `datetime`).
- Persistencia en archivo JSON.
- Pruebas: pytest (ver sección "Pruebas" arriba).
