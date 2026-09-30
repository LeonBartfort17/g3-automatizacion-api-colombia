"""
Fixtures compartidas por todos los tests.

Usar una sola sesión de requests (en vez de requests.get suelto en cada
prueba) reutiliza la conexión TCP y permite, si más adelante lo necesitan,
agregar headers o autenticación en un solo lugar.
"""

import pytest
import requests

from config import BASE_URL, REQUEST_TIMEOUT


@pytest.fixture(scope="session")
def api_session():
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    yield session
    session.close()


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def timeout():
    return REQUEST_TIMEOUT


@pytest.fixture(scope="session")
def api_get(api_session, base_url, timeout):
    """
    Fixture de conveniencia: devuelve una función que arma la URL
    completa a partir de un path relativo y hace el GET, usando la misma
    sesión/timeout compartidos. Permite escribir api_get("/City/1") en
    vez de repetir base_url y timeout en cada test.

    Se reconstruyó porque los tests de Jorge Iván Garzón la usaban pero
    no llegó incluida en su entrega original.
    """
    def _get(path, params=None):
        return api_session.get(f"{base_url}{path}", params=params, timeout=timeout)
    return _get
