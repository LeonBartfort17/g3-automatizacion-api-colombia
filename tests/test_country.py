"""
Caso de prueba sobre GET /Country/Colombia (Alta prioridad).

Este endpoint es un buen candidato para el trabajo de la Semana 6
(Validación de Datos): compara el valor devuelto por la API contra una
fuente oficial (ej. DANE) y documenta la fuente y fecha de consulta,
tal como exige el Plan de Pruebas (sección "Datos de prueba").
"""


def test_country_colombia_responde_ok(api_session, base_url, timeout):
    response = api_session.get(f"{base_url}/Country/Colombia", timeout=timeout)
    assert response.status_code == 200


def test_country_colombia_tiene_campos_esperados(api_session, base_url, timeout):
    response = api_session.get(f"{base_url}/Country/Colombia", timeout=timeout)
    pais = response.json()

    # Nombres de campo verificados contra el esquema real en
    # docs.api-colombia.com (ojo: es "stateCapital", NO "capital").
    campos_esperados = {"name", "stateCapital", "population", "isoCode"}
    faltantes = campos_esperados - pais.keys()
    assert not faltantes, f"Faltan campos en la respuesta de Country/Colombia: {faltantes}"


def test_country_colombia_capital_coincide_con_fuente_oficial(api_session, base_url, timeout):
    """
    Ejemplo de caso de "Validación de Datos" (Semana 6, OE2).

    Fuente oficial de referencia: DANE / Presidencia de la República.
    Fecha de consulta: registrar aquí la fecha real en la que se comparó,
    ej. "Consultado el 20/09/2026".

    Este test se deja explícito y simple para que el equipo vea el patrón:
    valor_api vs valor_fuente_oficial, con el nombre de la fuente y la
    fecha documentados en el propio test, no solo en la cabeza de quien
    lo escribió.
    """
    response = api_session.get(f"{base_url}/Country/Colombia", timeout=timeout)
    pais = response.json()

    capital_segun_fuente_oficial = "Bogotá"  # Fuente: DANE. Fecha de consulta: <completar>

    assert pais["stateCapital"].strip().lower() == capital_segun_fuente_oficial.lower(), (
        f"La API dice stateCapital='{pais['stateCapital']}', "
        f"la fuente oficial dice '{capital_segun_fuente_oficial}'"
    )
