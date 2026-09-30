# G3 — Automatización Alta Prioridad — Consolidado (24/24)

Este paquete reúne el trabajo de los 4 integrantes de G3 sobre los 24
endpoints de Alta prioridad, ya unificado, revisado y corregido para que
corra como una sola suite.

## Qué se hizo en esta consolidación


 **Se reemplazó la versión vieja de `test_contrato_alta_prioridad.py`**
   por la versión corregida (con `xfail` para el bug conocido de los
   500), que venía desactualizada en el zip.

 **Se verificó que no hubiera IDs de caso de prueba (`FN-XXX`)
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
  test_contrato_alta_prioridad.py      
  test_country.py                      
  test_president.py                    
  test_constitution.py                
  test_holiday.py                      
  test_touristicattraction.py         
  test_department.py                   
  test_region.py                      
  test_city.py                         
  test_airport.py                      
  test_urbancenter.py                  
  test_postalcode.py                   
  test_map.py                          
utils/
 

## Pendiente antes de dar la tarea por cerrada

- Correr `pytest -v` con internet real para confirmar cuántas de las 119
  pasan de verdad (solo se validó que "recolectan" sin errores de sintaxis).
- Subir este consolidado al repositorio de GitHub, reemplazando lo que
  haya ahí (puede que genere conflictos de merge si alguien más subió
  cambios mientras tanto — revisar antes de hacer push forzado).
