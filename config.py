"""
Configuración central del entorno de automatización.

Todo lo que dependa del entorno (URL base, timeouts, credenciales si algún
día se necesitan) vive aquí, en un solo lugar. Los scripts de prueba NUNCA
deben tener URLs escritas a mano — siempre deben importar BASE_URL desde
este archivo. Así, si la API cambia de dominio o versión, se corrige en
un solo sitio.
"""

import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://api-colombia.com/api/v1")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "15"))

# Endpoints de Alta prioridad (según "Priorización de Endpoints - API Colombia"),
# verificados contra la documentación oficial en docs.api-colombia.com.
# Referencia rápida para que el equipo sepa qué automatizar primero.
# Formato: (categoria, path)
ENDPOINTS_ALTA_PRIORIDAD = [
    ("Airport", "/Airport/name/Dorado"),
    ("Airport", "/Airport/search/dorado"),
    ("City", "/City"),
    ("City", "/City/1"),
    ("City", "/City/name/Neiva"),
    ("City", "/City/search/bogot"),
    ("ConstitutionArticle", "/ConstitutionArticle/1"),
    ("Country", "/Country/Colombia"),
    ("Department", "/Department"),
    ("Department", "/Department/1"),
    ("Department", "/Department/1/cities"),
    ("Department", "/Department/name/Huila"),
    ("Department", "/Department/search/huila"),
    ("Holiday", "/Holiday/year/2026"),
    ("Map", "/Map/1"),
    ("PostalCode", "/PostalCode"),
    ("President", "/President"),
    ("President", "/President/year/2020"),
    ("Region", "/Region"),
    ("Region", "/Region/1/departments"),
    ("TouristicAttraction", "/TouristicAttraction"),
    ("TouristicAttraction", "/TouristicAttraction/name/Leyva"),
    ("TouristicAttraction", "/TouristicAttraction/search/museo"),
    ("UrbanCenter", "/UrbanCenter"),
]

# NOTA: los endpoints "search/{keyword}" y "name/{name}" con keywords de
# 4+ caracteres (antes se usaban de 3 y algunos devolvían vacío/404 por
# esa regla de negocio real de la API, no por error de estos tests).

# ⚠️ HALLAZGO CONFIRMADO EN EJECUCIÓN REAL (22/09/2026): los endpoints
# Airport/name/{name}, City/name/{name} y TouristicAttraction/name/{name}
# devuelven 500 Internal Server Error de forma consistente. Esto amplía
# el hallazgo HZ-G3-002 de Jorge (que solo cubría TouristicAttraction):
# el mismo error afecta al menos 3 categorías distintas, lo que sugiere
# que comparten una misma implementación interna rota. Reportar como
# hallazgo de severidad Crítica cuanto antes, no esperar a la
# consolidación semanal.
RUTAS_NAME_CON_BUG_500_CONFIRMADO = [
    "/Airport/name/{name}",
    "/City/name/{name}",
    "/TouristicAttraction/name/{name}",
]

# Grupos con rate limiting compartido (ver docs/rate-limiting.md del repo
# oficial): Holiday, City y Department comparten el MISMO budget de
# 60 requests/minuto por IP. Si G3 corre sus pruebas al mismo tiempo que
# G4 golpea estos mismos endpoints con k6, van a chocar contra el límite
# y van a ver 429 en vez de fallas reales. Coordinar horarios con G4.
RATE_LIMITED_GROUPS = {"Holiday", "City", "Department"}
