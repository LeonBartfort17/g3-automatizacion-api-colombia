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
