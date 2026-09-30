"""
Caso de prueba sobre GET /PostalCode (Alta prioridad).
(Ticket AU-005 de Oscar David Motta Falla)

Campos verificados contra el modelo real (api/Models/PostalCode.cs):
id, noId, cityId, postalZone, code, northLimit, southLimit, eastLimit,
westLimit, type, neighborhoodsContainedInPostalCode,
ruralAreasContainedInPostalCode.
"""


def test_postalcode_devuelve_lista_no_vacia(api_session, base_url, timeout):
    """Caso: FN-023"""
    response = api_session.get(f"{base_url}/PostalCode", timeout=timeout)

    assert response.status_code == 200
    codigos = response.json()
    assert isinstance(codigos, list)
    assert len(codigos) > 0


def test_postalcode_cada_item_tiene_campos_obligatorios(api_session, base_url, timeout):
    """
    Caso: FN-023 (comparte ID con el caso de lista)

    OJO: a diferencia de otros recursos, PostalCode NO tiene un campo
    "name" — su identificador visible es "code" (el código postal en sí).
    """
    response = api_session.get(f"{base_url}/PostalCode", timeout=timeout)
    codigos = response.json()

    campos_obligatorios = {"id", "cityId", "code", "postalZone"}
    for cp in codigos:
        faltantes = campos_obligatorios - cp.keys()
        assert not faltantes, f"Código postal {cp.get('code', '???')} no tiene: {faltantes}"


def test_postalcode_code_no_vacio(api_session, base_url, timeout):
    """
    Caso: FN-023 (comparte ID con el caso de lista)
    """
    response = api_session.get(f"{base_url}/PostalCode", timeout=timeout)
    codigos = response.json()

    for cp in codigos:
        assert cp["code"], f"Registro id={cp.get('id')} tiene 'code' vacío"
