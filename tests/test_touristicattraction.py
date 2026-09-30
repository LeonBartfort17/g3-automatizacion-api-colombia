"""
Casos de prueba sobre GET /TouristicAttraction, /TouristicAttraction/name/{name}
y /TouristicAttraction/search/{keyword} (Alta prioridad).

Comportamiento real (api/Routes/TouristicAttactionRoutes.cs y api/Utils/Functions.cs):

- /name/{name}: coincidencia PARCIAL (Contains), sin distinguir mayúsculas,
  pero NO ignora tildes. Devuelve LISTA.
- /search/{keyword}: busca en todos los campos de texto (nombre, descripción,
  latitud, longitud; excluye imágenes), ignora mayúsculas y tildes. Devuelve LISTA.
  ⚠️ Con keyword de 3 letras o menos SOLO hay coincidencia exacta del campo
  completo (no parcial); el parcial exige más de 3 caracteres.
- Cuando no hay coincidencias, name y search responden 200 con lista vacía []
  (NO 404, a diferencia de President o Department). Se documenta como
  comportamiento actual; es una inconsistencia de contrato a considerar
  como hallazgo de severidad Baja.
"""

import pytest

from utils.asserts import assert_campos, assert_json_ok, sin_tildes

ENDPOINT = "/TouristicAttraction"

CAMPOS_ATRACTIVO = {"id", "name", "description", "images", "latitude", "longitude", "cityId"}

# Límites geográficos amplios de Colombia (incluye San Andrés y Leticia).
LAT_MIN, LAT_MAX = -5.0, 14.0
LON_MIN, LON_MAX = -82.5, -66.0


@pytest.fixture(scope="module")
def atractivos(api_get):
    """Lista completa de /TouristicAttraction (1 sola request para todo el módulo)."""
    return assert_json_ok(api_get(ENDPOINT))


# --------------------------------------------------------------------------
# GET /TouristicAttraction
# --------------------------------------------------------------------------

def test_touristicattraction_devuelve_lista_no_vacia(api_get):
    lista = assert_json_ok(api_get(ENDPOINT))

    assert isinstance(lista, list)
    assert len(lista) > 0


def test_touristicattraction_cada_item_tiene_campos_obligatorios(atractivos):
    for a in atractivos:
        assert_campos(a, CAMPOS_ATRACTIVO, f"TouristicAttraction id={a.get('id')}")
        assert isinstance(a["id"], int)
        assert isinstance(a["name"], str) and a["name"].strip(), f"id={a['id']} sin name"
        assert isinstance(a["description"], str) and a["description"].strip(), f"id={a['id']} sin description"
        assert isinstance(a["images"], list), f"id={a['id']}: images debe ser lista"
        assert isinstance(a["cityId"], int) and a["cityId"] >= 1


def test_touristicattraction_ids_unicos(atractivos):
    ids = [a["id"] for a in atractivos]
    assert len(set(ids)) == len(ids), "Hay ids de atractivo repetidos"


def test_touristicattraction_coordenadas_dentro_de_colombia(atractivos):
    """Validación de datos: latitud/longitud (vienen como string) parseables y dentro de Colombia."""
    fuera = []
    for a in atractivos:
        try:
            lat, lon = float(a["latitude"]), float(a["longitude"])
        except (TypeError, ValueError):
            fuera.append(f"id={a['id']} {a['name']}: coordenadas no numéricas ({a['latitude']!r}, {a['longitude']!r})")
            continue
        if not (LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX):
            fuera.append(f"id={a['id']} {a['name']}: ({lat}, {lon}) fuera de Colombia")

    assert not fuera, "Atractivos con coordenadas inválidas:\n" + "\n".join(fuera)


# --------------------------------------------------------------------------
# GET /TouristicAttraction/name/{name}
# --------------------------------------------------------------------------

def test_touristicattraction_name_leyva_devuelve_villa_de_leyva(api_get):
    lista = assert_json_ok(api_get(f"{ENDPOINT}/name/Leyva"))

    assert isinstance(lista, list) and lista, "name/Leyva no devolvió resultados"
    nombres = [a["name"] for a in lista]
    assert any("villa de leyva" in n.lower() for n in nombres), f"No apareció Villa de Leyva: {nombres}"
    for a in lista:
        assert_campos(a, CAMPOS_ATRACTIVO, "TouristicAttraction/name/Leyva")
        assert "leyva" in a["name"].lower(), f"'{a['name']}' no contiene 'leyva'"


def test_touristicattraction_name_es_insensible_a_mayusculas(api_get):
    minusculas = assert_json_ok(api_get(f"{ENDPOINT}/name/leyva"))
    mayusculas = assert_json_ok(api_get(f"{ENDPOINT}/name/LEYVA"))

    assert minusculas, "name/leyva no devolvió resultados"
    assert [a["id"] for a in minusculas] == [a["id"] for a in mayusculas]


def test_touristicattraction_name_con_espacios(api_get):
    """Nombre con espacios (requests los codifica como %20)."""
    lista = assert_json_ok(api_get(f"{ENDPOINT}/name/Villa de Leyva"))

    assert any(a["name"].lower() == "villa de leyva" for a in lista)


def test_touristicattraction_name_incluye_ciudad(api_get):
    """name/{name} hace Include(City): el objeto 'city' debe venir y ser coherente con cityId."""
    villa = assert_json_ok(api_get(f"{ENDPOINT}/name/Villa de Leyva"))[0]

    assert isinstance(villa.get("city"), dict), "El atractivo no trae el objeto 'city'"
    assert villa["city"]["id"] == villa["cityId"]


def test_touristicattraction_name_inexistente_devuelve_lista_vacia(api_get):
    """Comportamiento actual: 200 + [] (no 404). Ver nota del módulo."""
    lista = assert_json_ok(api_get(f"{ENDPOINT}/name/zzzxxxinexistente"))

    assert lista == []


# --------------------------------------------------------------------------
# GET /TouristicAttraction/search/{keyword}
# --------------------------------------------------------------------------

def test_touristicattraction_search_museo_devuelve_resultados_relevantes(api_get):
    lista = assert_json_ok(api_get(f"{ENDPOINT}/search/museo"))

    assert isinstance(lista, list) and lista, "search/museo no devolvió resultados"
    for a in lista:
        assert_campos(a, CAMPOS_ATRACTIVO, "TouristicAttraction/search/museo")
        texto = sin_tildes(f"{a['name']} {a['description']}")
        assert "museo" in texto, f"'{a['name']}' no contiene 'museo' en nombre ni descripción"
    assert any("museo del oro" in sin_tildes(a["name"]) for a in lista), "No apareció el Museo del Oro"


def test_touristicattraction_search_es_insensible_a_mayusculas(api_get):
    minusculas = assert_json_ok(api_get(f"{ENDPOINT}/search/museo"))
    mayusculas = assert_json_ok(api_get(f"{ENDPOINT}/search/MUSEO"))

    assert minusculas
    assert sorted(a["id"] for a in minusculas) == sorted(a["id"] for a in mayusculas)


def test_touristicattraction_search_keyword_corto_no_hace_coincidencia_parcial(api_get):
    """
    Regla de la API: con keyword de <= 3 caracteres solo cuenta la coincidencia
    EXACTA de un campo completo. 'oro' (3) no devuelve 'Museo del oro' aunque
    lo contenga. Por eso config.py NO debe usar '/search/oro' en el test de
    contrato (devuelve [] y falla el assert de body no vacío).
    """
    lista = assert_json_ok(api_get(f"{ENDPOINT}/search/oro"))

    assert lista == []


def test_touristicattraction_search_inexistente_devuelve_lista_vacia(api_get):
    """Comportamiento actual: 200 + [] (no 404). Ver nota del módulo."""
    lista = assert_json_ok(api_get(f"{ENDPOINT}/search/zzzxxxinexistente"))

    assert lista == []
