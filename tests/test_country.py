"""
Casos de prueba sobre GET /Country/Colombia (Alta prioridad).

⚠️ Campo correcto: "stateCapital", NO "capital" (esquema real confirmado en
docs.api-colombia.com y en el modelo C# api/Models/Country.cs del repo).

Este endpoint es un buen candidato para el trabajo de la Semana 6
(Validación de Datos): compara el valor devuelto por la API contra una
fuente oficial (ej. DANE) y documenta la fuente y fecha de consulta,
tal como exige el Plan de Pruebas (sección "Datos de prueba").
"""

import pytest

from utils.asserts import assert_campos, assert_json_ok

ENDPOINT = "/Country/Colombia"

# Esquema completo del recurso Country (docs.api-colombia.com / README del repo).
CAMPOS_COUNTRY = {
    "id", "name", "description", "stateCapital", "surface", "population",
    "languages", "timeZone", "currency", "currencyCode", "isoCode",
    "internetDomain", "phonePrefix", "radioPrefix", "aircraftPrefix",
}


@pytest.fixture(scope="module")
def pais(api_get):
    """Body de /Country/Colombia (1 sola request para todo el módulo)."""
    return assert_json_ok(api_get(ENDPOINT))


def test_country_colombia_responde_ok(api_get):
    response = api_get(ENDPOINT)
    assert_json_ok(response, 200)


def test_country_colombia_tiene_campos_esperados(pais):
    # Nombres de campo verificados contra el esquema real (ojo: es "stateCapital", NO "capital").
    assert_campos(pais, CAMPOS_COUNTRY, "Country/Colombia")


def test_country_colombia_usa_statecapital_y_no_capital(pais):
    """Regresión del error de esquema: 'capital' NO existe, el campo real es 'stateCapital'."""
    assert "stateCapital" in pais, "Falta el campo 'stateCapital' en Country/Colombia"
    assert "capital" not in pais, (
        "Apareció un campo 'capital' que no existe en el esquema documentado; "
        "el campo correcto es 'stateCapital'"
    )
    assert isinstance(pais["stateCapital"], str) and pais["stateCapital"].strip()


def test_country_colombia_tipos_de_dato(pais):
    assert isinstance(pais["id"], int)
    assert isinstance(pais["name"], str)
    assert isinstance(pais["stateCapital"], str)
    assert isinstance(pais["population"], int) and not isinstance(pais["population"], bool)
    assert isinstance(pais["surface"], (int, float)) and not isinstance(pais["surface"], bool)
    assert isinstance(pais["languages"], list) and pais["languages"], "languages debe ser lista no vacía"
    assert all(isinstance(idioma, str) and idioma.strip() for idioma in pais["languages"])


def test_country_colombia_valores_de_identidad(pais):
    """Datos de identidad estables y públicamente conocidos de Colombia."""
    assert pais["name"] == "Colombia"
    assert pais["isoCode"] == "CO"
    assert pais["currencyCode"] == "COP"
    assert pais["phonePrefix"] == "+57"
    assert pais["internetDomain"] == ".co"


def test_country_colombia_valores_en_rango_plausible(pais):
    """
    Sanidad de magnitudes (no valores exactos, que cambian con cada censo):
    Colombia tiene ~1.14 millones de km² y ~50 millones de habitantes.
    """
    assert 1_100_000 <= pais["surface"] <= 1_200_000, f"surface fuera de rango: {pais['surface']}"
    assert 40_000_000 <= pais["population"] <= 60_000_000, f"population fuera de rango: {pais['population']}"


def test_country_colombia_capital_coincide_con_fuente_oficial(pais):
    """
    Ejemplo de caso de "Validación de Datos" (Semana 6, OE2).

    Fuente oficial de referencia: DANE / Presidencia de la República.
    Fecha de consulta: registrar aquí la fecha real en la que se comparó,
    ej. "Consultado el 20/09/2026".

    Este test se deja explícito y simple para que el equipo vea el patrón:
    valor_api vs valor_fuente_oficial, con el nombre de la fuente y la
    fecha documentados en el propio test, no solo en la cabeza de quien
    lo escribió.
    """
    capital_segun_fuente_oficial = "Bogotá"  # Fuente: DANE. Fecha de consulta: <completar>

    assert pais["stateCapital"].strip().lower() == capital_segun_fuente_oficial.lower(), (
        f"La API dice stateCapital='{pais['stateCapital']}', "
        f"la fuente oficial dice '{capital_segun_fuente_oficial}'"
    )
