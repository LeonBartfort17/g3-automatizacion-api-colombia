"""
Casos de prueba sobre Airport (Alta prioridad): name/{name} y search/{keyword}.
(Ticket AU-005 de Oscar David Motta Falla)

Datos reales verificados contra el dump oficial: "El Dorado" = Airport id 3
(nombre real completo: "Aeropuerto Internacional El Dorado").
"""

import pytest


@pytest.mark.xfail(
    reason="Bug confirmado 22/09/2026: Airport/name/{name} devuelve 500 "
    "(mismo patrón que City y TouristicAttraction, ver HZ-G3-002 ampliado)",
    strict=False,
)
def test_airport_by_name_dorado(api_session, base_url, timeout):
    """
    GET /Airport/name/{name} — HALLAZGO CONFIRMADO: 500 Internal Server
    Error de forma consistente. Es el mismo patrón de bug que City y
    TouristicAttraction (ver HZ-G3-002 ampliado). Se usa "Dorado" (sin
    tilde, sustring de "El Dorado") por la regla ya conocida de que el
    Contains() de la API no ignora tildes.

    Caso: FN-020
    """
    response = api_session.get(f"{base_url}/Airport/name/Dorado", timeout=timeout)

    assert response.status_code == 200
    aeropuertos = response.json()
    assert any("dorado" in a["name"].lower() for a in aeropuertos)


def test_airport_search_dorado(api_session, base_url, timeout):
    """
    GET /Airport/search/{keyword} — a diferencia de name/{name}, este SÍ
    responde bien. Confirma que el bug de los 500 está específicamente en
    la ruta name/{name}, no en toda la categoría Airport.

    Caso: FN-021
    """
    response = api_session.get(f"{base_url}/Airport/search/dorado", timeout=timeout)

    assert response.status_code == 200
    aeropuertos = response.json()
    assert len(aeropuertos) > 0
    assert any("dorado" in a["name"].lower() for a in aeropuertos)


def test_airport_search_campos_obligatorios(api_session, base_url, timeout):
    """
    Campos verificados contra el modelo real (api/Models/Airport.cs):
    id, name, iataCode, oaciCode, latitude, longitude.

    Caso: FN-021 (comparte ID con el caso anterior)
    """
    response = api_session.get(f"{base_url}/Airport/search/dorado", timeout=timeout)
    aeropuertos = response.json()

    campos_obligatorios = {"id", "name", "iataCode", "latitude", "longitude"}
    for aeropuerto in aeropuertos:
        faltantes = campos_obligatorios - aeropuerto.keys()
        assert not faltantes, f"Aeropuerto {aeropuerto.get('name', '???')} no tiene: {faltantes}"
