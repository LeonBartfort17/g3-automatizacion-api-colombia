# G3 — Automatización Alta Prioridad — Consolidado (24/24)

Este paquete reúne el trabajo de los 4 integrantes de G3 sobre los 24
endpoints de Alta prioridad, ya unificado, revisado y corregido para que
corra como una sola suite.

## Qué se hizo en esta consolidación

1. **Se completaron los 8 endpoints que faltaban** (los de Oscar David
   Motta Falla, que nunca llegaron): `City/{id}`, `City/name/{name}`,
   `City/search/{keyword}`, `Airport/name/{name}`,
   `Airport/search/{keyword}`, `UrbanCenter`, `PostalCode`, `Map/{id}`.
   Casos documentados como `FN-017` a `FN-024`.

2. **Se reconstruyó `utils/asserts.py` y la fixture `api_get`**, que los
   5 archivos de Jorge Iván Garzón usaban pero nunca llegaron incluidos
   en su entrega — sin esto, la mitad de la suite no corría para nadie
   más que él.

3. **Se reemplazó la versión vieja de `test_contrato_alta_prioridad.py`**
   por la versión corregida (con `xfail` para el bug conocido de los
   500), que venía desactualizada en el zip.

4. **Se verificó que no hubiera IDs de caso de prueba (`FN-XXX`)
   duplicados entre los 3 archivos Excel** — confirmado: 24 hojas, 24
   IDs únicos, sin colisiones.

## Resultado: 119 pruebas, recolectan sin errores

```
python -m pytest --collect-only
# 119 tests collected in 0.03s
```

Falta correrlas contra la API real (no hay salida a internet desde este
entorno) para confirmar cuántas pasan — recomendable hacerlo antes de
dar la tarea por cerrada.

## 🔴 Bug ampliado a 3 categorías — confirma HZ-G3-002

Con los tests nuevos de Oscar David, el bug de los `500 Internal Server
Error` en el patrón `/{recurso}/name/{name}` queda confirmado en:
- `Airport/name/{name}` (FN-020)
- `City/name/{name}` (FN-018)
- `TouristicAttraction/name/{name}` (hallazgo original de Jorge, HZ-G3-002)

Se documentaron como ampliación del mismo hallazgo `HZ-G3-002`, no como
hallazgos nuevos separados, porque comparten la misma causa raíz
probable (una implementación interna compartida entre las 3 categorías).

## Estructura del paquete

```
config.py                              # 24 endpoints Alta, IDs reales verificados
conftest.py                            # fixtures: api_session, api_get, base_url, timeout
requirements.txt
tests/
  test_contrato_alta_prioridad.py      # contrato genérico (200+JSON) de los 24, con xfail
  test_country.py                      # Jorge
  test_president.py                    # Jorge
  test_constitution.py                 # Jorge
  test_holiday.py                      # Jorge
  test_touristicattraction.py          # Jorge
  test_department.py                   # Juan Andrés
  test_region.py                       # Juan Andrés
  test_city.py                         # Juan Andrés (lista) + Oscar David (id/name/search)
  test_airport.py                      # Oscar David (nuevo)
  test_urbancenter.py                  # Oscar David (nuevo)
  test_postalcode.py                   # Oscar David (nuevo)
  test_map.py                          # Oscar David (nuevo)
utils/
  asserts.py                           # reconstruido (faltaba en la entrega de Jorge)
casos_de_prueba_G3_ALTA_CONSOLIDADO.xlsx    # FN-001 a FN-024, sin duplicados
reporte_hallazgos_G3_CONSOLIDADO.xlsx       # HZ-G3-001, HZ-G3-002 (ampliado)
```

## Pendiente antes de dar la tarea por cerrada

- Correr `pytest -v` con internet real para confirmar cuántas de las 119
  pasan de verdad (solo se validó que "recolectan" sin errores de sintaxis).
- Subir este consolidado al repositorio de GitHub, reemplazando lo que
  haya ahí (puede que genere conflictos de merge si alguien más subió
  cambios mientras tanto — revisar antes de hacer push forzado).
