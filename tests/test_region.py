"""
Casos de prueba sobre Region (Alta prioridad).

Cubre los 2 endpoints Alta de Region: GET /Region y GET /Region/{id}/departments
(Region/{id} sin /departments es Media prioridad y queda fuera de este alcance).

Dato real verificado en vivo (20/09/2026): la API expone 6 regiones
(Caribe=1, Pacífico=2, Orinoquía=3, Amazonía=4, Andina=5, Insular=6).
Huila pertenece a la región Andina (regionId 5).

OJO: en GET /Region el campo "departments" de cada región viene en null
(no se popula ahí) — los departamentos solo se obtienen consultando
/Region/{id}/departments por separado. No asumir lo contrario.
"""

REGION_CARIBE_ID = 1


def test_region_devuelve_lista_no_vacia(api_session, base_url, timeout):
    """Caso: FN-014"""
    response = api_session.get(f"{base_url}/Region", timeout=timeout)

    assert response.status_code == 200
    regiones = response.json()
    assert isinstance(regiones, list)
    assert len(regiones) > 0


def test_region_cada_item_tiene_campos_obligatorios(api_session, base_url, timeout):
    """Caso: FN-014 (comparte ID con el GET /Region de lista)"""
    response = api_session.get(f"{base_url}/Region", timeout=timeout)
    regiones = response.json()

    campos_obligatorios = {"id", "name"}
    for region in regiones:
        faltantes = campos_obligatorios - region.keys()
        assert not faltantes, f"Región {region.get('name', '???')} no tiene: {faltantes}"


def test_region_incluye_las_seis_regiones_conocidas(api_session, base_url, timeout):
    """
    Las 6 regiones naturales de Colombia son un dato estable (no cambia
    como cambiaría, por ejemplo, un conteo de ciudades). Sirve como ancla
    de contenido real, no solo de estructura.

    Caso: FN-014 (comparte ID con el GET /Region de lista)
    """
    response = api_session.get(f"{base_url}/Region", timeout=timeout)
    regiones = response.json()

    nombres = {r["name"].lower() for r in regiones}
    esperadas = {"caribe", "pacífico", "orinoquía", "amazonía", "andina", "insular"}
    assert esperadas.issubset(nombres)


def test_region_id_departments_caribe_incluye_atlantico(api_session, base_url, timeout):
    """
    GET /Region/{id}/departments para la región Caribe (id 1). Atlántico es
    un departamento verificado en vivo dentro de esa región y sirve de
    ancla, en vez de solo comprobar que la lista no está vacía.

    Caso: FN-015
    """
    response = api_session.get(
        f"{base_url}/Region/{REGION_CARIBE_ID}/departments", timeout=timeout
    )

    assert response.status_code == 200
    departamentos = response.json()
    assert isinstance(departamentos, list)
    assert len(departamentos) > 0

    nombres = {d["name"].lower() for d in departamentos}
    assert "atlántico" in nombres
