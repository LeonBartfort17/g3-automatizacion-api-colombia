"""
Casos de prueba sobre Department (Alta prioridad).

Cubre los 5 endpoints Alta de Department:
GET /Department, /Department/{id}, /Department/{id}/cities,
/Department/name/{name}, /Department/search/{keyword}

Estos son ejemplos de "prueba funcional automatizada": no solo revisan que
responda 200, sino que la estructura y el contenido tengan sentido.

IMPORTANTE PARA EL EQUIPO:
Los nombres de campo (id, name, ...) son los que documenta la API pública.
Verifiquen contra la respuesta real (o el Swagger) antes de dar por buena
la prueba, y ajusten si algún campo cambió de nombre.

Dato real verificado (dump SQL oficial): Huila = Department id 18,
Neiva = City id 657 (capital de Huila). 33 departamentos en total.
"""

DEPARTAMENTO_HUILA_ID = 18


def test_department_devuelve_lista_no_vacia(api_session, base_url, timeout):
    """Caso: FN-009"""
    response = api_session.get(f"{base_url}/Department", timeout=timeout)
    departamentos = response.json()

    assert isinstance(departamentos, list)
    assert len(departamentos) > 0


def test_department_cada_item_tiene_campos_obligatorios(api_session, base_url, timeout):
    """Caso: FN-009 (comparte ID con el GET /Department de lista)"""
    response = api_session.get(f"{base_url}/Department", timeout=timeout)
    departamentos = response.json()

    campos_obligatorios = {"id", "name"}
    for depto in departamentos:
        faltantes = campos_obligatorios - depto.keys()
        assert not faltantes, f"Departamento {depto.get('name', '???')} no tiene: {faltantes}"


def test_department_by_name_huila_existe(api_session, base_url, timeout):
    """
    Caso representativo: buscar un departamento conocido (Huila) por nombre
    y confirmar que la API lo devuelve. Este tipo de caso sirve de puente
    hacia la validación de datos de la Semana 6 (comparación con fuentes
    oficiales): aquí solo se prueba el contrato, allá se compara el valor.

    OJO: la API devuelve un array (de 1 elemento), no un objeto, según
    docs.api-colombia.com; por eso el assert recorre la lista.

    Caso: FN-012
    """
    response = api_session.get(f"{base_url}/Department/name/Huila", timeout=timeout)

    assert response.status_code == 200
    deptos = response.json()
    assert isinstance(deptos, list)
    assert any("huila" in d["name"].lower() for d in deptos)


def test_department_by_id_devuelve_huila(api_session, base_url, timeout):
    """
    GET /Department/{id} usando el id 18, verificado como Huila contra el
    dump oficial (no un id "adivinado"). Confirma id y name consistentes.

    Caso: FN-010
    """
    response = api_session.get(f"{base_url}/Department/{DEPARTAMENTO_HUILA_ID}", timeout=timeout)

    assert response.status_code == 200
    depto = response.json()
    assert depto["id"] == DEPARTAMENTO_HUILA_ID
    assert "huila" in depto["name"].lower()


def test_department_id_cities_incluye_neiva(api_session, base_url, timeout):
    """
    GET /Department/{id}/cities para Huila (18). Neiva (id 657, capital de
    Huila) es un dato verificado contra el dump oficial y sirve de ancla
    para no depender solo de "la lista no está vacía".

    Caso: FN-011
    """
    response = api_session.get(
        f"{base_url}/Department/{DEPARTAMENTO_HUILA_ID}/cities", timeout=timeout
    )

    assert response.status_code == 200
    ciudades = response.json()
    assert isinstance(ciudades, list)
    assert len(ciudades) > 0

    nombres = {c["name"].lower() for c in ciudades}
    assert "neiva" in nombres


def test_department_search_huila_incluye_huila(api_session, base_url, timeout):
    """
    GET /Department/search/{keyword}.

    OJO — hallazgo importante para el equipo: el keyword mínimo son 4
    caracteres. "hui" (3 letras, como estaba puesto en config.py) devuelve
    404, no una lista vacía. Verificado en vivo contra la API el 20/09.

    Además, la búsqueda NO es solo por nombre: compara contra texto que
    incluye la descripción de cada departamento, así que buscar "huila"
    también trae a Cauca, Cundinamarca, Caquetá, Tolima y Meta (todos
    mencionan a Huila como vecino en su descripción). Por eso el assert
    correcto es "Huila está entre los resultados", no "hay un solo
    resultado".

    Caso: FN-013
    """
    response = api_session.get(f"{base_url}/Department/search/huila", timeout=timeout)

    assert response.status_code == 200
    resultados = response.json()
    assert isinstance(resultados, list)

    ids = {d["id"] for d in resultados}
    assert DEPARTAMENTO_HUILA_ID in ids
