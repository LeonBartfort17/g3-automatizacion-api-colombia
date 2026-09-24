"""
Casos de prueba sobre GET /Department (Alta prioridad).

Estos son ejemplos de "prueba funcional automatizada": no solo revisan que
responda 200, sino que la estructura y el contenido tengan sentido.

IMPORTANTE PARA EL EQUIPO:
Los nombres de campo (id, name, ...) son los que documenta la API pública.
Verifiquen contra la respuesta real (o el Swagger) antes de dar por buena
la prueba, y ajusten si algún campo cambió de nombre.
"""


def test_department_devuelve_lista_no_vacia(api_session, base_url, timeout):
    response = api_session.get(f"{base_url}/Department", timeout=timeout)
    departamentos = response.json()

    assert isinstance(departamentos, list)
    assert len(departamentos) > 0


def test_department_cada_item_tiene_campos_obligatorios(api_session, base_url, timeout):
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

    OJO: a diferencia de lo que se asumía antes, este endpoint devuelve
    una LISTA de departamentos (puede matchear varios por nombre parcial),
    no un objeto único. Confirmado en ejecución real el 22/09/2026.
    """
    response = api_session.get(f"{base_url}/Department/name/Huila", timeout=timeout)

    assert response.status_code == 200
    departamentos = response.json()
    assert isinstance(departamentos, list) and len(departamentos) > 0
    assert any("huila" in d["name"].lower() for d in departamentos)
