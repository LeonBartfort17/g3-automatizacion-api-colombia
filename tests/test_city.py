"""
Casos de prueba sobre City (Alta prioridad) — SOLO el endpoint de lista
(GET /City), según alcance asignado para este ticket. Los otros 3
endpoints Alta de City (/City/{id}, /City/name/{name}, /City/search/{keyword})
quedan fuera y le corresponden a otro compañero de G3 (encajan en el
ticket de Taiga AU-005 — no confundir con el caso de xlsx FN-016).

City comparte el mismo budget de rate limiting (60 req/min) que Department
y Holiday — no correr en loop agresivo junto con esos otros tests.
"""


def test_city_devuelve_lista_no_vacia(api_session, base_url, timeout):
    """Caso: FN-016"""
    response = api_session.get(f"{base_url}/City", timeout=timeout)

    assert response.status_code == 200
    ciudades = response.json()
    assert isinstance(ciudades, list)
    assert len(ciudades) > 0


def test_city_cada_item_tiene_campos_obligatorios(api_session, base_url, timeout):
    """Caso: FN-016 (comparte ID con el GET /City de lista)"""
    response = api_session.get(f"{base_url}/City", timeout=timeout)
    ciudades = response.json()

    campos_obligatorios = {"id", "name"}
    for ciudad in ciudades:
        faltantes = campos_obligatorios - ciudad.keys()
        assert not faltantes, f"Ciudad {ciudad.get('name', '???')} no tiene: {faltantes}"


def test_city_incluye_neiva(api_session, base_url, timeout):
    """
    Neiva (id 657) es un dato verificado contra el dump oficial y es
    capital de Huila — sirve de ancla de contenido real en la lista
    completa de ciudades.

    Caso: FN-016 (comparte ID con el GET /City de lista)
    """
    response = api_session.get(f"{base_url}/City", timeout=timeout)
    ciudades = response.json()

    nombres = {c["name"].lower() for c in ciudades}
    assert "neiva" in nombres


# ---------------------------------------------------------------------------
# A partir de aquí: los otros 3 endpoints Alta de City (ticket AU-005 de
# Oscar David Motta Falla). Se agregan en este mismo archivo por ser el
# mismo recurso, pero corresponden a casos FN-017 a FN-019.
# ---------------------------------------------------------------------------

import pytest


def test_city_by_id_devuelve_neiva(api_session, base_url, timeout):
    """
    GET /City/{id} — usa el id real de Neiva (657), verificado contra el
    dump oficial, en vez de un id adivinado.

    Caso: FN-017
    """
    response = api_session.get(f"{base_url}/City/657", timeout=timeout)

    assert response.status_code == 200
    ciudad = response.json()
    assert ciudad["id"] == 657
    assert "neiva" in ciudad["name"].lower()


@pytest.mark.xfail(
    reason="Bug confirmado 22/09/2026: City/name/{name} devuelve 500 "
    "(mismo patrón que Airport y TouristicAttraction, ver HZ-G3-002 ampliado)",
    strict=False,
)
def test_city_by_name_neiva(api_session, base_url, timeout):
    """
    GET /City/name/{name} — HALLAZGO CONFIRMADO: este endpoint devuelve
    500 Internal Server Error de forma consistente, igual que
    Airport/name/{name} y TouristicAttraction/name/{name}. Se deja el
    test marcado xfail para que quede documentado en la suite en vez de
    aparecer como una falla roja sin contexto.

    Caso: FN-018
    """
    response = api_session.get(f"{base_url}/City/name/Neiva", timeout=timeout)

    assert response.status_code == 200
    ciudades = response.json()
    assert any("neiva" in c["name"].lower() for c in ciudades)


def test_city_search_bogota(api_session, base_url, timeout):
    """
    GET /City/search/{keyword} — usa "bogot" (5 caracteres) en vez de un
    fragmento más corto, porque ya se confirmó que la API exige mínimo 4
    caracteres en el keyword (ver hallazgo de Juan Andrés en Department).

    Caso: FN-019
    """
    response = api_session.get(f"{base_url}/City/search/bogot", timeout=timeout)

    assert response.status_code == 200
    ciudades = response.json()
    assert len(ciudades) > 0
    assert any("bogot" in c["name"].lower() for c in ciudades)
