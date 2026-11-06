<!-- INICIO FICHAS JUAN S07-S09 -->

## J-01 - Consolidación de filtros (Juan)

**Smell:** S07 (duplicación de filtros). **Técnica:** Extract/Consolidate Method con función de selección compartida. **Reglas:** DRY, Clean Code y cohesión.

**Ubicación:** `src/gestor_solicitudes.py`, `_filtrar` y métodos `filtrar_por_estado/tipo/prioridad/legajo`.

**Antes:** cuatro métodos recorrían `self.lst` y construían manualmente `res`, con normalizaciones levemente diferentes.

```python
res = []
for i in range(len(self.lst)):
    if self.lst[i].estado.upper() == x:
        res.append(self.lst[i])
return res
```

**Después:**

```python
def _filtrar(self, obtener_valor, valor):
    return [solicitud for solicitud in self.lst
            if obtener_valor(solicitud) == valor]

def filtrar_por_estado(self, x):
    return self._filtrar(lambda s: s.estado.upper(), x.upper().strip().replace(" ", "_"))
```

Los otros tres filtros delegan de la misma manera y mantienen sus normalizaciones previas. **Por qué mejora:** un solo recorrido y menos riesgo de diferencias al modificar la implementación. **No se cambió** la interfaz usada por el menú.

**Commit de Juan:** [`446d280`](https://github.com/gastonlell25/gestion-solicitudes/commit/446d28053f80c31192ee85f38ba464e1357fde80). **Verificación:** T10–T14 en `tests/test_juan_filtros_reportes.py`, más pruebas adicionales de los criterios. **Evidencia anterior:** `docs/evidencias/antes/codigo_juan_S07.png`; **diferencias reales:** [PR #20, Files changed](https://github.com/gastonlell25/gestion-solicitudes/pull/20/files). **Captura posterior:** pendiente de incorporar desde GitHub.

---

## J-02 - Move Method: antigüedad y vencimiento a Solicitud (Juan)

**Smells:** S08 (Feature Envy) y S09 (modelo anémico). **Técnica:** Move Method. **Principios:** SRP, encapsulación y cohesión del modelo.

**Ubicación:** `src/modelos/solicitud.py` (nuevos `dias_desde_creacion` y `esta_vencida`) y `src/gestor_solicitudes.py` (métodos puente que conservan las llamadas actuales).

**Antes:** el gestor leía atributos de `Solicitud` y construía objetos `datetime.date` para decidir los plazos.

```python
def esta_vencida(self, s):
    if s.estado != "PENDIENTE" and s.estado != "EN_REVISION":
        return False
    d = self.dias_desde_creacion(s)
    if s.prioridad == "ALTA" and d > 3:
        return True
    # ... plazos MEDIA y BAJA
```

**Después:**

```python
# Solicitud
def esta_vencida(self, fecha_referencia):
    if self.estado not in ("PENDIENTE", "EN_REVISION"):
        return False
    dias = self.dias_desde_creacion(fecha_referencia)
    plazos = {"ALTA": 3, "MEDIA": 7, "BAJA": 15}
    return self.prioridad in plazos and dias > plazos[self.prioridad]
```

**Decisión:** la fecha se pasa explícitamente para hacer los cálculos verificables y no introducir dependencias ocultas de la hora actual. La entidad conoce sus reglas de vencimiento; el gestor conserva funciones puente (`s.dias_desde_creacion(self.hoy())`, `s.esta_vencida(self.hoy())`) para preservar compatibilidad.

**Commit de Juan:** [`89d860a`](https://github.com/gastonlell25/gestion-solicitudes/commit/89d860a57b7559bcc419a4302e9bb51dd654715d). **Verificación:** pruebas con diferentes fechas/plazos en `tests/test_juan_modelo_reporte.py`, junto con T15 y recorrido del listado. **Evidencia anterior:** `docs/evidencias/antes/codigo_juan_S08.png` y `codigo_juan_S09.png`. **Captura posterior:** pendiente.

---

## J-03 - Extract Class: ReporteService (Juan)

**Smells:** S09 (concentración de lógica en gestor) y responsabilidades múltiples. **Técnica:** Extract Class. **Principio:** SRP y separación de la construcción del reporte de la interacción con consola.

**Ubicación:** `src/servicios/reporte_service.py`; en `GestorSolicitudes.reporte()` permanece solo la impresión.

**Antes:** `reporte()` recorría `self.lst`, contaba estados y tipos y realizaba todos los `print()`.

**Después:**

```python
# gestor_solicitudes.py
def reporte(self):
    print(ReporteService.generar(self.lst, self.hoy()))

# reporte_service.py
@classmethod
def generar(cls, solicitudes, fecha_referencia):
    conteo_estados = Counter(s.estado for s in solicitudes)
    conteo_tipos = Counter(s.tipo for s in solicitudes)
    # El resultado conserva exactamente el formato de texto original.
```

**Por qué mejora:** el cálculo se puede probar sin capturar impresión por consola y se evita volver a recorrer las solicitudes para cada indicador. **Decisión de alcance:** `ReporteService` produce el mismo reporte textual para conservar los contratos de T15; no agrega una interfaz gráfica ni cambia persistencia.

**Commit de Juan:** [`28e55a2`](https://github.com/gastonlell25/gestion-solicitudes/commit/28e55a2b0c7f25f6e0d1f9930a72d73640acf542). **Verificación:** `tests/test_juan_modelo_reporte.py` y T15. **Diferencias:** [PR #20](https://github.com/gastonlell25/gestion-solicitudes/pull/20/files). **Captura posterior y test suite integrado final:** pendientes para la Fase 4/5.

<!-- FIN FICHAS JUAN S07-S09 -->
