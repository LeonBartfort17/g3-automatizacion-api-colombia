"""
Casos de prueba sobre GET /ConstitutionArticle/{id} (Alta prioridad).

Datos reales confirmados: la API tiene 380 artículos de la Constitución,
con ids del 1 al 380 (el id coincide con el número de artículo).

Comportamiento (api/Routes/ConstitutionArticleRoutes.cs):
- id <= 0            -> 400 Bad Request
- id inexistente     -> 404 Not Found
"""

import pytest

from utils.asserts import assert_campos, assert_json_ok, assert_status

TOTAL_ARTICULOS = 380

CAMPOS_ARTICULO = {
    "id", "titleNumber", "title", "chapterNumber", "chapter", "articleNumber", "content",
}


def _validar_estructura(articulo):
    assert_campos(articulo, CAMPOS_ARTICULO, f"ConstitutionArticle id={articulo.get('id')}")
    for campo in ("id", "titleNumber", "chapterNumber", "articleNumber"):
        assert isinstance(articulo[campo], int) and articulo[campo] >= 1, (
            f"{campo} debe ser entero >= 1, llegó {articulo[campo]!r}"
        )
    for campo in ("title", "chapter", "content"):
        assert isinstance(articulo[campo], str) and articulo[campo].strip(), f"{campo} vacío"


def test_constitution_article_1_responde_ok(api_get):
    articulo = assert_json_ok(api_get("/ConstitutionArticle/1"))

    assert isinstance(articulo, dict)
    _validar_estructura(articulo)
    assert articulo["id"] == 1
    assert articulo["articleNumber"] == 1


def test_constitution_article_1_coincide_con_la_constitucion_de_1991(api_get):
    """
    Validación de datos contra fuente oficial: el Artículo 1 de la Constitución
    Política de 1991 (Título I, "De los principios fundamentales") comienza con
    "Colombia es un Estado social de derecho, organizado en forma de República unitaria...".
    Fuente: Constitución Política de Colombia, Art. 1. Fecha de consulta: <completar>.
    """
    articulo = assert_json_ok(api_get("/ConstitutionArticle/1"))

    assert articulo["titleNumber"] == 1
    assert articulo["title"].strip().upper() == "DE LOS PRINCIPIOS FUNDAMENTALES"
    assert articulo["content"].startswith("Colombia es un Estado social de derecho")
    assert "república unitaria" in articulo["content"].lower()


def test_constitution_article_380_es_el_ultimo(api_get):
    articulo = assert_json_ok(api_get("/ConstitutionArticle/380"))

    _validar_estructura(articulo)
    assert articulo["id"] == 380
    assert articulo["articleNumber"] == 380
    # Art. 380: "Queda derogada la Constitución hasta ahora vigente con todas sus reformas..."
    assert "derogada la constitución" in articulo["content"].lower()


@pytest.mark.parametrize("id_articulo", [1, 2, 50, 100, 211, 250, 300, 379, 380])
def test_constitution_article_ids_del_rango_existen_y_son_consistentes(api_get, id_articulo):
    articulo = assert_json_ok(api_get(f"/ConstitutionArticle/{id_articulo}"))

    _validar_estructura(articulo)
    assert articulo["id"] == id_articulo
    assert articulo["articleNumber"] == id_articulo, "el id debe coincidir con el número de artículo"


@pytest.mark.parametrize("id_articulo", [381, 9999])
def test_constitution_article_fuera_de_rango_devuelve_404(api_get, id_articulo):
    assert_status(api_get(f"/ConstitutionArticle/{id_articulo}"), 404, "Id fuera del rango 1-380.")


@pytest.mark.parametrize("id_articulo", [0, -1])
def test_constitution_article_id_invalido_devuelve_400(api_get, id_articulo):
    assert_status(api_get(f"/ConstitutionArticle/{id_articulo}"), 400, "Id inválido (<= 0).")


def test_constitution_total_380_articulos_con_ids_1_a_380(api_get):
    """
    Test de APOYO (usa GET /ConstitutionArticle, el listado, no uno de los 8
    endpoints objetivo): con UNA sola request confirma el dato real
    "380 artículos, ids 1 a 380" en vez de hacer 380 requests por id.
    """
    lista = assert_json_ok(api_get("/ConstitutionArticle"))

    ids = sorted(a["id"] for a in lista)
    assert len(lista) == TOTAL_ARTICULOS, f"Se esperaban {TOTAL_ARTICULOS} artículos, llegaron {len(lista)}"
    assert ids == list(range(1, TOTAL_ARTICULOS + 1)), "Los ids no son la secuencia continua 1..380"
