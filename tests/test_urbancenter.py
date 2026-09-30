"""
Caso de prueba sobre GET /UrbanCenter (Alta prioridad).
(Ticket AU-005 de Oscar David Motta Falla)

Campos verificados contra el modelo real (api/Models/UrbanCenter.cs):
id, cityId, code, name, type, longitude, latitude.
"""


def test_urbancenter_devuelve_lista_no_vacia(api_session, base_url, timeout):
    """Caso: FN-022"""
    response = api_session.get(f"{base_url}/UrbanCenter", timeout=timeout)

    assert response.status_code == 200
    centros = response.json()
    assert isinstance(centros, list)
    assert len(centros) > 0


def test_urbancenter_cada_item_tiene_campos_obligatorios(api_session, base_url, timeout):
    """Caso: FN-022 (comparte ID con el caso de lista)"""
    response = api_session.get(f"{base_url}/UrbanCenter", timeout=timeout)
    centros = response.json()

    campos_obligatorios = {"id", "cityId", "code", "name", "type", "latitude", "longitude"}
    for centro in centros:
        faltantes = campos_obligatorios - centro.keys()
        assert not faltantes, f"Centro urbano {centro.get('name', '???')} no tiene: {faltantes}"


def test_urbancenter_coordenadas_dentro_de_colombia(api_session, base_url, timeout):
    """
    Validación de rango geográfico: Colombia está aproximadamente entre
    latitud -4.2 a 13.5 y longitud -82 a -66.8.

    Caso: FN-022 (comparte ID con el caso de lista)
    """
    response = api_session.get(f"{base_url}/UrbanCenter", timeout=timeout)
    centros = response.json()

    for centro in centros:
        lat, lon = centro["latitude"], centro["longitude"]
        assert -4.2 <= lat <= 13.5, f"{centro['name']}: latitud fuera de rango ({lat})"
        assert -82 <= lon <= -66.8, f"{centro['name']}: longitud fuera de rango ({lon})"
