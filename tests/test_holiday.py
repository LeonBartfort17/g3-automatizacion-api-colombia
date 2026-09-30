"""
Casos de prueba sobre GET /Holiday/year/{year} (Alta prioridad).

HALLAZGO IMPORTANTE (código fuente real, api/Routes/HolidayRoutes.cs, y
confirmado en el texto de la Ley 2578 de 2026, art. 6): a partir de 2026 el
9 de julio (Día de Nuestra Señora del Rosario de Chiquinquirá) es festivo
nacional.

    Holiday/year/2025 (y años anteriores) -> 18 feriados
    Holiday/year/2026 (y posteriores)     -> 19 feriados (18 + Chiquinquirá)

⚠️ Si alguien reporta "18" como conteo esperado para 2026, está equivocado:
el 19 es el comportamiento CORRECTO y no debe reportarse como HZ.

Nota sobre la fecha de Chiquinquirá: la ley remite a la Ley 51 de 1983 (Emiliani)
"para determinar el día de disfrute", y hay debate jurídico sobre si se traslada
al lunes. La API la traslada al lunes siguiente (9/jul/2026 es jueves ->
13/jul/2026). Por eso el conteo (19) se valida de forma estricta, pero la
fecha de ese festivo se acepta en {9, 13} de julio.

⚠️ Rate limit: Holiday, City y Department comparten 60 req/min por IP. Este
módulo hace pocas requests y reutiliza fixtures; la fixture `api_get` reintenta
ante 429. Coordinar horarios con G4 (k6) al ejecutar.
"""

from datetime import date

import pytest

from utils.asserts import assert_campos, assert_json_ok, assert_status

# 18 festivos tradicionales de 2026 según el calendario oficial colombiano
# (Ley 51 de 1983 "Emiliani" + Semana Santa). Fuente independiente de la API.
FESTIVOS_TRADICIONALES_2026 = {
    "2026-01-01",  # Año Nuevo
    "2026-01-12",  # Reyes Magos
    "2026-03-23",  # San José
    "2026-04-02",  # Jueves Santo
    "2026-04-03",  # Viernes Santo
    "2026-05-01",  # Día del Trabajo
    "2026-05-18",  # Ascensión del Señor
    "2026-06-08",  # Corpus Christi
    "2026-06-15",  # Sagrado Corazón
    "2026-06-29",  # San Pedro y San Pablo
    "2026-07-20",  # Independencia
    "2026-08-07",  # Batalla de Boyacá
    "2026-08-17",  # Asunción de la Virgen
    "2026-10-12",  # Día de la Raza
    "2026-11-02",  # Todos los Santos
    "2026-11-16",  # Independencia de Cartagena
    "2026-12-08",  # Inmaculada Concepción
    "2026-12-25",  # Navidad
}
assert len(FESTIVOS_TRADICIONALES_2026) == 18

# Fechas aceptadas para el festivo de la Ley 2578 en 2026 (ver nota arriba).
FECHAS_CHIQUINQUIRA_2026 = {"2026-07-09", "2026-07-13"}


def _es_chiquinquira(holiday):
    return "chiquinquir" in holiday["name"].lower()


def _fechas(holidays):
    return [h["date"][:10] for h in holidays]


@pytest.fixture(scope="module")
def festivos_2026(api_get):
    """Body de /Holiday/year/2026 (1 sola request para todo el módulo)."""
    return assert_json_ok(api_get("/Holiday/year/2026"))


# --------------------------------------------------------------------------
# 2026: 19 feriados (18 + Ley 2578)
# --------------------------------------------------------------------------

def test_holidays_2026_incluye_18_mas_uno_de_la_ley_2578(festivos_2026):
    nombres = [h["name"] for h in festivos_2026]

    assert len(festivos_2026) == 19, (
        f"Se esperaban 19 feriados en 2026 (18 tradicionales + Ley 2578), "
        f"llegaron {len(festivos_2026)}"
    )
    assert any("Chiquinquir" in n for n in nombres), (
        "No se encontró el feriado de Chiquinquirá (Ley 2578 de 2026) en la respuesta"
    )


def test_holidays_2026_responde_ok_y_estructura(festivos_2026):
    assert isinstance(festivos_2026, list)
    for h in festivos_2026:
        assert_campos(h, {"date", "name"}, "Holiday")
        assert isinstance(h["name"], str) and h["name"].strip()
        date.fromisoformat(h["date"][:10])  # ValueError si el formato es inválido


def test_holidays_2026_incluye_los_18_tradicionales_segun_calendario_oficial(festivos_2026):
    fechas_api = set(_fechas(festivos_2026))

    faltantes = FESTIVOS_TRADICIONALES_2026 - fechas_api
    assert not faltantes, f"Faltan festivos oficiales 2026 en la API: {sorted(faltantes)}"


def test_holidays_2026_el_unico_festivo_extra_es_chiquinquira(festivos_2026):
    extras = [h for h in festivos_2026 if h["date"][:10] not in FESTIVOS_TRADICIONALES_2026]

    assert len(extras) == 1, f"Se esperaba 1 festivo adicional a los 18 tradicionales, hay {len(extras)}: {extras}"
    assert _es_chiquinquira(extras[0]), f"El festivo adicional no es Chiquinquirá: {extras[0]}"
    assert extras[0]["date"][:10] in FECHAS_CHIQUINQUIRA_2026, (
        f"Fecha de Chiquinquirá inesperada: {extras[0]['date'][:10]}"
    )


def test_holidays_2026_fechas_unicas_ordenadas_y_del_anio(festivos_2026):
    fechas = _fechas(festivos_2026)

    assert len(set(fechas)) == len(fechas), "Hay fechas de festivo repetidas"
    assert fechas == sorted(fechas), "Los festivos no vienen ordenados por fecha"
    assert all(f.startswith("2026-") for f in fechas), "Hay festivos fuera de 2026"


# --------------------------------------------------------------------------
# Control: antes y después de la ley
# --------------------------------------------------------------------------

def test_holidays_2025_no_incluye_el_feriado_nuevo(api_get):
    """Control: antes de 2026 ese feriado no debería existir (18 festivos)."""
    holidays = assert_json_ok(api_get("/Holiday/year/2025"))
    nombres = [h["name"] for h in holidays]

    assert len(holidays) == 18
    assert not any("Chiquinquir" in n for n in nombres)


def test_holidays_2027_mantiene_19_con_chiquinquira(api_get):
    """La ley es permanente ('de cada año'): 2027 también debe tener 19 con Chiquinquirá."""
    holidays = assert_json_ok(api_get("/Holiday/year/2027"))

    assert len(holidays) == 19
    assert sum(_es_chiquinquira(h) for h in holidays) == 1


def test_holidays_2026_include_sunday_agrega_domingos_religiosos(api_get):
    """Parámetro opcional includeSunday=true: suma Domingo de Ramos y Domingo de Pascua (19 + 2 = 21)."""
    holidays = assert_json_ok(api_get("/Holiday/year/2026", params={"includeSunday": "true"}))
    fechas = set(_fechas(holidays))

    assert len(holidays) == 21, f"Con includeSunday se esperaban 21 festivos, llegaron {len(holidays)}"
    assert {"2026-03-29", "2026-04-05"} <= fechas, "Faltan Domingo de Ramos (29/mar) o Pascua (5/abr)"


# --------------------------------------------------------------------------
# Casos negativos
# --------------------------------------------------------------------------

@pytest.mark.parametrize("year", [0, 10000])
def test_holidays_year_fuera_de_rango_devuelve_400(api_get, year):
    assert_status(api_get(f"/Holiday/year/{year}"), 400, "Año fuera del rango 1-9999.")
