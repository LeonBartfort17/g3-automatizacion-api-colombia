"""
Caso de prueba: AU-001 (ajustar el prefijo según se confirme con G1/profesor,
ver nota en el README sobre el conflicto AU-XXX vs Automatización/Autenticación)

Objetivo: validar el "contrato" básico de los endpoints de Alta prioridad:
- Responden 200 OK
- Responden JSON
- El body no viene vacío

Esta es la primera capa de automatización (rápida y barata). Los tests más
específicos de estructura de cada recurso van en archivos separados
(ver test_department.py, test_president.py, test_country.py).
"""

import pytest

from config import ENDPOINTS_ALTA_PRIORIDAD, RUTAS_NAME_CON_BUG_500_CONFIRMADO


def _con_marca_si_bug_conocido(categoria, path):
    """Si el endpoint es un '/name/{algo}' de una categoría con el bug 500
    ya confirmado (ver config.py), lo marca como xfail en vez de fail."""
    ruta_generica = f"/{categoria}/name/{{name}}"
    es_bug_conocido = "/name/" in path and ruta_generica in RUTAS_NAME_CON_BUG_500_CONFIRMADO

    if es_bug_conocido:
        return pytest.param(
            categoria, path,
            marks=pytest.mark.xfail(
                reason=f"Bug confirmado 22/09/2026: {ruta_generica} devuelve 500 (ver HZ-G3-002 ampliado)",
                strict=False,
            ),
        )
    return pytest.param(categoria, path)


CASOS = [_con_marca_si_bug_conocido(cat, path) for cat, path in ENDPOINTS_ALTA_PRIORIDAD]


@pytest.mark.parametrize("categoria,path", CASOS)
def test_endpoint_alta_prioridad_responde_200_json(api_session, base_url, timeout, categoria, path):
    response = api_session.get(f"{base_url}{path}", timeout=timeout)

    assert response.status_code == 200, (
        f"[{categoria}] se esperaba 200 OK en {path}, llegó {response.status_code}"
    )
    assert "application/json" in response.headers.get("Content-Type", ""), (
        f"[{categoria}] la respuesta de {path} no vino en JSON"
    )

    body = response.json()
    assert body, f"[{categoria}] la respuesta de {path} vino vacía"
