"""
Utilidades compartidas de aserciones para la suite de automatización G3.

Este módulo faltaba en la entrega original — se reconstruyó a partir del
USO real que le daban los tests de Jorge Iván Garzón (test_country.py,
test_president.py, test_constitution.py, test_holiday.py,
test_touristicattraction.py), para que la suite completa pueda correr.
"""

import unicodedata


def assert_json_ok(response, status=200):
    """
    Verifica que la respuesta tenga el status code esperado (200 por
    defecto) y que venga en JSON. Devuelve el body ya parseado, para
    poder encadenar: datos = assert_json_ok(api_get("/algo"))
    """
    assert response.status_code == status, (
        f"Se esperaba status {status}, llegó {response.status_code}: "
        f"{response.text[:300]}"
    )
    content_type = response.headers.get("Content-Type", "")
    assert "application/json" in content_type, (
        f"Se esperaba JSON, el Content-Type fue '{content_type}'"
    )
    return response.json()


def assert_status(response, status_esperado, mensaje=""):
    """
    Verifica que la respuesta tenga exactamente el status code indicado,
    sin exigir que venga en JSON (útil para 400/404 que a veces no
    traen body).
    """
    assert response.status_code == status_esperado, (
        f"{mensaje} Se esperaba {status_esperado}, llegó {response.status_code}"
    )


def assert_campos(objeto, campos_esperados, etiqueta=""):
    """
    Verifica que un diccionario tenga todos los campos de un set dado.
    """
    faltantes = campos_esperados - objeto.keys()
    assert not faltantes, f"{etiqueta}: faltan los campos {faltantes}"


def sin_tildes(texto):
    """
    Quita tildes/diacríticos y pasa a minúsculas, para comparaciones que
    no dependan de acentuación (la API de Colombia no siempre es
    consistente con las tildes en sus datos).
    """
    normalizado = unicodedata.normalize("NFD", texto)
    sin_acentos = "".join(c for c in normalizado if unicodedata.category(c) != "Mn")
    return sin_acentos.lower()
