"""
Caso de prueba sobre GET /Map/{id} (Alta prioridad).
(Ticket AU-005 de Oscar David Motta Falla)

Campos verificados contra el modelo real (api/Models/Map.cs): id, name,
description, departmentId, urlImages, urlSource.

Dato verificado contra el dump oficial: Map tiene ids del 1 al 10 (no hay
id=0 ni ids mayores a 10) — se usa id=1 con confianza, no es un valor
adivinado.
"""


def test_map_by_id_responde_ok(api_session, base_url, timeout):
    """Caso: FN-024"""
    response = api_session.get(f"{base_url}/Map/1", timeout=timeout)
    assert response.status_code == 200


def test_map_tiene_campos_esperados(api_session, base_url, timeout):
    """Caso: FN-024 (comparte ID con el caso anterior)"""
    response = api_session.get(f"{base_url}/Map/1", timeout=timeout)
    mapa = response.json()

    campos_esperados = {"id", "name", "urlImages"}
    faltantes = campos_esperados - mapa.keys()
    assert not faltantes, f"Faltan campos en Map/1: {faltantes}"


def test_map_id_inexistente_no_revienta(api_session, base_url, timeout):
    """
    Map solo tiene ids del 1 al 10. Se prueba un id fuera de rango (999)
    para confirmar que responde con un error controlado (404) y no con
    un 500 — a diferencia del bug conocido en los endpoints /name/{name}.

    Caso: FN-024 (comparte ID con el caso anterior — flujo alternativo)
    """
    response = api_session.get(f"{base_url}/Map/999", timeout=timeout)
    assert response.status_code in (404, 204), (
        f"Se esperaba un error controlado para Map/999, llegó {response.status_code}"
    )
