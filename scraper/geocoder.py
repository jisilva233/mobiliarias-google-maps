"""
Geocoding de endereços usando Nominatim (OpenStreetMap) — gratuito, sem API key.
Rate limit: 1 request/segundo (respeitado automaticamente).
"""

import logging
import time
from typing import Optional, Tuple

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

logger = logging.getLogger(__name__)

_geolocator = Nominatim(user_agent="real-estate-maps-app/1.0")
_DELAY = 1.1  # segundos entre requests (respeita rate limit Nominatim)


def geocode_address(endereco: str, cidade: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Retorna (latitude, longitude) para um endereço.
    Tenta primeiro endereço completo, depois só cidade como fallback.
    """
    if not endereco and not cidade:
        return None, None

    queries = []
    if endereco:
        queries.append(f"{endereco}, {cidade}, Brasil")
    queries.append(f"{cidade}, Brasil")

    for query in queries:
        try:
            time.sleep(_DELAY)
            location = _geolocator.geocode(query, timeout=10, language="pt")
            if location:
                logger.debug("Geocoded '%s' -> (%.4f, %.4f)", query, location.latitude, location.longitude)
                return location.latitude, location.longitude
        except (GeocoderTimedOut, GeocoderServiceError) as exc:
            logger.warning("Geocoding falhou para '%s': %s", query, exc)
        except Exception as exc:
            logger.warning("Erro inesperado no geocoding: %s", exc)

    logger.debug("Sem coordenadas para: %s", endereco)
    return None, None


def geocode_agencies(agencies: list, cidade: str) -> list:
    """
    Adiciona lat/lon a uma lista de Agency.
    Retorna lista atualizada.
    """
    total = len(agencies)
    geocoded = 0

    for i, agency in enumerate(agencies, 1):
        logger.info("Geocoding %d/%d: %s", i, total, agency.nome)
        lat, lon = geocode_address(agency.endereco, cidade)
        agency.latitude = lat
        agency.longitude = lon
        if lat:
            geocoded += 1

    logger.info("Geocoding: %d/%d com coordenadas", geocoded, total)
    return agencies
