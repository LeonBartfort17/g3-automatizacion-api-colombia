"""
Casos de prueba sobre GET /President y GET /President/year/{year} (Alta prioridad).

Datos reales confirmados: la API tiene 52 presidentes.

Comportamiento del endpoint /President/year/{year} (leído en el código fuente,
api/Routes/PresidentRoutes.cs):
- Devuelve una LISTA (no un objeto): todos los presidentes cuyo periodo
  toca ese año. En años de transición (ej. 2022: Duque termina y Petro
  empieza el 07/08/2022) devuelven 2 presidentes — es correcto, no un bug.
- year <= 0  -> 400 Bad Request
- año sin ningún presidente -> 404 Not Found
"""

from datetime import date

import pytest

from utils.asserts import assert_campos, assert_json_ok, assert_status

TOTAL_PRESIDENTES = 52

CAMPOS_PRESIDENTE = {
    "id", "image", "name", "lastName", "startPeriodDate", "endPeriodDate",
    "politicalParty", "description", "cityId",
}


def _fecha(valor):
    """'1943-10-19' o '1943-10-19T00:00:00' -> date."""
    return date.fromisoformat(valor[:10])


@pytest.fixture(scope="module")
def presidentes(api_get):
    """Lista completa de /President (1 sola request para todo el módulo)."""
    return assert_json_ok(api_get("/President"))


# --------------------------------------------------------------------------
# GET /President
# --------------------------------------------------------------------------

def test_president_responde_ok(api_get):
    lista = assert_json_ok(api_get("/President"))
    assert isinstance(lista, list)


def test_president_devuelve_52_presidentes(presidentes):
    assert len(presidentes) == TOTAL_PRESIDENTES, (
        f"Se esperaban {TOTAL_PRESIDENTES} presidentes, llegaron {len(presidentes)}"
    )


def test_president_ids_unicos(presidentes):
    ids = [p["id"] for p in presidentes]
    assert all(isinstance(i, int) for i in ids)
    assert len(set(ids)) == len(ids), "Hay ids de presidente repetidos"


def test_president_cada_item_tiene_campos_obligatorios(presidentes):
    for p in presidentes:
        assert_campos(p, CAMPOS_PRESIDENTE, f"President id={p.get('id')}")


def test_president_nombre_apellido_y_partido_no_vacios(presidentes):
    for p in presidentes:
        assert isinstance(p["name"], str) and p["name"].strip(), f"id={p['id']} sin name"
        assert isinstance(p["lastName"], str) and p["lastName"].strip(), f"id={p['id']} sin lastName"
        assert isinstance(p["politicalParty"], str) and p["politicalParty"].strip(), (
            f"id={p['id']} ({p['name']} {p['lastName']}) sin politicalParty"
        )


def test_president_fechas_tienen_formato_iso_valido(presidentes):
    for p in presidentes:
        _fecha(p["startPeriodDate"])  # lanza ValueError si el formato es inválido
        if p["endPeriodDate"] is not None:
            _fecha(p["endPeriodDate"])


@pytest.mark.xfail(
    reason=(
        "Defecto de datos conocido (candidato a hallazgo HZ): President id=27 "
        "(Darío Echandía Olaya) tiene endPeriodDate 1943-05-16 ANTERIOR a "
        "startPeriodDate 1943-10-19 (fechas invertidas). Pasará a XPASS cuando se corrija."
    ),
    strict=False,
)
def test_president_fecha_fin_no_es_anterior_a_fecha_inicio(presidentes):
    invalidos = [
        f"id={p['id']} {p['name']} {p['lastName']}: inicio={p['startPeriodDate'][:10]} fin={p['endPeriodDate'][:10]}"
        for p in presidentes
        if p["endPeriodDate"] is not None and _fecha(p["endPeriodDate"]) < _fecha(p["startPeriodDate"])
    ]
    assert not invalidos, "Presidentes con fin < inicio:\n" + "\n".join(invalidos)


# --------------------------------------------------------------------------
# GET /President/year/{year}
# --------------------------------------------------------------------------

def test_president_year_2020_es_ivan_duque(api_get):
    lista = assert_json_ok(api_get("/President/year/2020"))

    assert isinstance(lista, list)
    assert len(lista) == 1, f"En 2020 se esperaba 1 presidente, llegaron {len(lista)}"
    duque = lista[0]
    assert_campos(duque, CAMPOS_PRESIDENTE, "President/year/2020")
    assert "duque" in duque["lastName"].lower(), f"Se esperaba Duque, llegó {duque['name']} {duque['lastName']}"


def test_president_year_incluye_ciudad_de_nacimiento(api_get):
    """El endpoint por año hace Include(City): 'city' debe venir poblado y ser coherente con cityId."""
    duque = assert_json_ok(api_get("/President/year/2020"))[0]

    assert isinstance(duque.get("city"), dict), "El presidente no trae el objeto 'city'"
    assert duque["city"]["id"] == duque["cityId"]


def test_president_year_2022_devuelve_transicion_duque_y_petro(api_get):
    """7/08/2022: termina Duque y empieza Petro -> ambos 'gobernaron' en 2022."""
    lista = assert_json_ok(api_get("/President/year/2022"))

    apellidos = " | ".join(p["lastName"].lower() for p in lista)
    assert len(lista) == 2, f"En 2022 se esperaban 2 presidentes, llegaron {len(lista)}: {apellidos}"
    assert "duque" in apellidos and "petro" in apellidos


def test_president_year_2024_es_gustavo_petro(api_get):
    lista = assert_json_ok(api_get("/President/year/2024"))

    assert len(lista) == 1
    assert "petro" in lista[0]["lastName"].lower()


def test_president_year_1886_es_el_primer_presidente(api_get):
    lista = assert_json_ok(api_get("/President/year/1886"))

    assert len(lista) == 1
    assert "campo serrano" in lista[0]["lastName"].lower()


@pytest.mark.parametrize("year", [1990, 2000, 2010, 2020])
def test_president_year_todos_los_resultados_cubren_el_anio(api_get, year):
    """Invariante: todo presidente devuelto debe tener un periodo que toque `year`."""
    lista = assert_json_ok(api_get(f"/President/year/{year}"))

    assert lista, f"No llegó ningún presidente para {year}"
    for p in lista:
        inicio = _fecha(p["startPeriodDate"]).year
        fin = _fecha(p["endPeriodDate"]).year if p["endPeriodDate"] else date.today().year
        assert inicio <= year <= fin, (
            f"{p['name']} {p['lastName']} ({inicio}-{fin}) no corresponde al año {year}"
        )


@pytest.mark.parametrize("year", [1800, 2999])
def test_president_year_sin_presidente_devuelve_404(api_get, year):
    assert_status(api_get(f"/President/year/{year}"), 404, "Año sin presidente.")


@pytest.mark.parametrize("year", [0, -1])
def test_president_year_invalido_devuelve_400(api_get, year):
    assert_status(api_get(f"/President/year/{year}"), 400, "Año inválido (<= 0).")
