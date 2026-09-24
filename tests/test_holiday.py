"""
Caso de prueba sobre GET /Holiday/year/{year} (Alta prioridad).

HALLAZGO IMPORTANTE (encontrado leyendo el código fuente real del
repositorio de GitHub, no está documentado en Swagger ni en la web de
docs): a partir del año 2026, por la "Ley 2578 de 2026", el 9 de julio
(día de Chiquinquirá) se agregó como feriado nacional nuevo. Si cae
entre semana se traslada al lunes siguiente; si cae sábado o domingo se
queda en la fecha original.

Esto significa que:
- Holiday/year/2025 (y años anteriores) → 18 feriados
- Holiday/year/2026 (y años posteriores) → 19 feriados, con "Día de
  Chiquinquirá" incluido

Es un caso perfecto para el reporte de hallazgos si alguien más del
equipo (o los profesores) esperaban 18 feriados en 2026 sin saber de
esta ley — no sería un bug de la API, sería un comportamiento correcto
que hay que documentar como parte de "Observaciones", no reportar como
HZ.
"""


def test_holidays_2026_incluye_18_mas_uno_de_la_ley_2578(api_session, base_url, timeout):
    response = api_session.get(f"{base_url}/Holiday/year/2026", timeout=timeout)
    assert response.status_code == 200

    holidays = response.json()
    nombres = [h["name"] for h in holidays]

    assert len(holidays) == 19, (
        f"Se esperaban 19 feriados en 2026 (18 tradicionales + Ley 2578), "
        f"llegaron {len(holidays)}"
    )
    assert any("Chiquinquir" in n for n in nombres), (
        "No se encontró el feriado de Chiquinquirá (Ley 2578 de 2026) en la respuesta"
    )


def test_holidays_2025_no_incluye_el_feriado_nuevo(api_session, base_url, timeout):
    """Control: antes de 2026 ese feriado no debería existir."""
    response = api_session.get(f"{base_url}/Holiday/year/2025", timeout=timeout)
    assert response.status_code == 200

    holidays = response.json()
    nombres = [h["name"] for h in holidays]

    assert len(holidays) == 18
    assert not any("Chiquinquir" in n for n in nombres)
