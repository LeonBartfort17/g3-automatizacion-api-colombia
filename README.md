# Automatización API Colombia — G3

Entorno base de automatización para el grupo **G3 (Automatización y Datos)**.
Entregable de la Semana 5 – Preparación (16/09 al 18/09).

## 1. Instalación

```bash
python -m venv venv
source venv/bin/activate      # En Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

No es obligatorio tocar el `.env`, ya trae la URL base correcta
(`https://api-colombia.com/api/v1`). Si alguna vez cambia, se edita ahí y
no en cada test.

## 2. Ejecutar las pruebas

```bash
python -m pytest -v
```

Para ejecutar solo un archivo:

```bash
python -m pytest tests/test_department.py -v
```

## 3. Estructura del proyecto

```
automatizacion-api-colombia/
├── config.py                          # URL base, timeout, lista de endpoints Alta prioridad
├── conftest.py                        # Fixtures compartidas (sesión HTTP, base_url, timeout)
├── requirements.txt
├── .env.example
└── tests/
    ├── test_contrato_alta_prioridad.py  # Prueba genérica de contrato (200 + JSON) para TODOS los Alta
    ├── test_country.py                  # Ejemplo específico + ejemplo de validación de datos
    └── test_department.py               # Ejemplo específico de estructura y búsqueda por nombre
```

## 4. Endpoints Alta prioridad (ya completos en config.py)

`ENDPOINTS_ALTA_PRIORIDAD` en `config.py` ya trae los **24 endpoints de
Alta prioridad** completos, verificados contra la documentación oficial
real en [docs.api-colombia.com](https://docs.api-colombia.com/). Con eso
el test de contrato (`test_contrato_alta_prioridad.py`) los cubre a todos
automáticamente sin escribir nada más.

⚠️ Los endpoints con `{id}`, `{name}` o `{keyword}` usan valores de
ejemplo (id=1, "Bogota", "Huila", "Eldorado", etc.) solo para poder
correr el test. **Verifiquen que esos IDs/nombres existan de verdad en la
API antes de dar la prueba por buena** — si no, ajústenlos en `config.py`.

## 4.1. Corrección importante de esquema

El script anterior asumía que `Country/Colombia` tenía un campo
`"capital"`. El esquema real (confirmado en la documentación oficial) usa
`"stateCapital"`. Ya está corregido en `test_country.py`. Moraleja para
el equipo: **siempre verifiquen los nombres de campo contra
docs.api-colombia.com antes de escribir un assert**, no contra lo que
"suena lógico".

Para escribir una prueba **específica** de estructura (no solo contrato),
copien `test_department.py` o `test_country.py` como plantilla.

## 5. Para cuándo escriban casos de prueba en la plantilla oficial

Cada test automatizado debería tener su fila correspondiente en
`casodepruebaplantilla.xlsx`, con Endpoint, Método HTTP, Resultado esperado
y Estado. El ID de caso debe seguir la convención acordada.

**⚠️ Pendiente de confirmar con G1 / el profesor:** el *Plan de Pruebas*
dice que el prefijo `AU-XXX` es para **Automatización (G3)**, pero la
*Plantilla de Caso de Prueba* dice que `AU-XXX` es para
**Autenticación/Autorización**. Confirmen cuál aplica antes de numerar
casos, para no chocar con los de G2 al consolidar el reporte final.

## 6. Semana 6 — Validación de Datos

`test_country.py` incluye un ejemplo (`test_country_colombia_capital_...`)
de cómo documentar una comparación contra una fuente oficial: se deja
explícito el valor esperado, el nombre de la fuente y un lugar para la
fecha de consulta. Repliquen ese patrón para Department, President, City,
etc., usando siempre fuentes oficiales (DANE, Presidencia de la República,
Wikipedia solo si no hay algo más oficial) y registrando la fecha de
consulta en cada test, tal como exige el Plan de Pruebas.

## 8. Hallazgos del código fuente real (repo de GitHub)

Con acceso al código fuente real (`api-colombia-main.zip`, repo oficial en
GitHub) se pudieron confirmar y descubrir cosas que ningún documento del
curso tenía:

1. **Todos los campos de los modelos quedaron 100% confirmados** contra
   las clases C# reales (`api/Models/*.cs`), no contra suposiciones. Los
   nombres exactos ya están reflejados en `config.py` y en los tests.

2. **IDs y nombres reales verificados contra el dump de base de datos**
   (`dump-apicolombia-*.sql`, que sí trae datos, no solo el esquema):
   Huila = Department id **18**, Neiva = City id **657**, Bogotá D.C. =
   City id **167**, "El Dorado" = Airport id **3**. Ya no hay valores
   adivinados en `config.py`.

   ⚠️ Ojo: ese dump es la **propia base de datos de la API**, no una
   fuente externa independiente. Sirve para conseguir IDs/nombres reales
   con los que probar (Semana 5), pero **no sirve como "fuente oficial"**
   para la Validación de Datos de la Semana 6 — para eso sigue haciendo
   falta comparar contra DANE u otra fuente externa real, porque
   comparar la API contra su propia base de datos no prueba nada sobre
   la calidad del dato en sí.

3. **Rate limiting real y documentado** (`docs/rate-limiting.md` del
   repo): los grupos **Holiday, City y Department comparten un mismo
   límite de 60 requests/minuto por IP**. El resto de endpoints no tiene
   límite. Esto es crítico para coordinarse con G4 (pruebas de carga) —
   si ambos grupos prueban esos tres recursos al mismo tiempo, van a
   generar `429 Too Many Requests` que no son fallas reales de la API,
   sino que se están pisando entre equipos. Recomendación: agenden
   ventanas de tiempo separadas para probar esos 3 grupos, o avisen a G4.

4. **Feriado nuevo desde 2026** (Ley 2578 de 2026, encontrado en el
   código de `HolidayRoutes.cs`): el 9 de julio (Día de Chiquinquirá) es
   feriado nacional nuevo a partir de este año. `Holiday/year/2026` debe
   traer **19** feriados en vez de los 18 tradicionales. Ya hay un test
   para esto en `test_holiday.py` — es un buen ejemplo de un caso que,
   si no se conociera, alguien podría reportar por error como un "bug"
   (conteo incorrecto de feriados) cuando en realidad es correcto.

## 7. Meta de la semana

Automatizar al menos el **60% de los casos funcionales de los endpoints
de Alta prioridad** (criterio de aceptación de G3 en el Plan de Pruebas).
Con 24 endpoints Alta, eso son al menos ~15 endpoints con prueba
automatizada para el cierre de la Semana 5.
