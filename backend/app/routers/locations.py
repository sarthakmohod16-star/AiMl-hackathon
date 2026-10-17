"""Locations API router for geocoding and proximity competition analysis."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.location import (
    LocationAnalyzeRequest,
    LocationAnalyzeResponse,
    LocationSearchRequest,
    LocationSearchResponse,
)
from app.services.location_service import (
    LocationProviderRateLimitError,
    LocationProviderTimeoutError,
    LocationProviderUnavailableError,
    LocationService,
    LocationServiceError,
)

logger = logging.getLogger("biztwin.locations")

router = APIRouter(prefix="/locations", tags=["Locations"])


def get_location_service() -> LocationService:
    """Dependency provider yielding a LocationService instance."""
    return LocationService()


@router.post(
    "/search",
    response_model=LocationSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Geocode address query into candidate coordinates",
    description=(
        "Converts an address or landmark query into validated geographic coordinates "
        "using OpenStreetMap Nominatim. Returns candidate locations with bounding boxes and attribution."
    ),
)
async def search_location(
    payload: LocationSearchRequest,
    service: LocationService = Depends(get_location_service),
) -> LocationSearchResponse:
    """Geocode search query string to geographic coordinates."""
    try:
        return await service.geocode_address(payload.query)
    except LocationProviderTimeoutError as e:
        logger.warning("Geocoding timeout for query: %s", payload.query)
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=e.message,
        )
    except LocationProviderRateLimitError as e:
        logger.warning("Geocoding rate limit exceeded for query: %s", payload.query)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=e.message,
        )
    except LocationProviderUnavailableError as e:
        logger.error("Geocoding provider unavailable for query: %s", payload.query)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=e.message,
        )
    except LocationServiceError as e:
        logger.error("Geocoding service error for query: %s: %s", payload.query, e)
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
        )


@router.post(
    "/analyze",
    response_model=LocationAnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze nearby commercial competition density",
    description=(
        "Discovers mapped commercial points of interest around target coordinates within radius meters. "
        "Calculates distances via Haversine formula and classifies competitors into direct, indirect, or unknown."
    ),
)
async def analyze_location(
    payload: LocationAnalyzeRequest,
    service: LocationService = Depends(get_location_service),
) -> LocationAnalyzeResponse:
    """Analyze proximity competition density and points of interest."""
    try:
        return await service.analyze_location(payload)
    except LocationProviderTimeoutError as e:
        logger.warning("Location analyze timeout for coords: %s, %s", payload.latitude, payload.longitude)
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=e.message,
        )
    except LocationProviderRateLimitError as e:
        logger.warning("Location analyze rate limit for coords: %s, %s", payload.latitude, payload.longitude)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=e.message,
        )
    except LocationProviderUnavailableError as e:
        logger.error("Location analyze provider unavailable for coords: %s, %s", payload.latitude, payload.longitude)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=e.message,
        )
    except LocationServiceError as e:
        logger.error("Location analyze service error: %s", e)
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
        )
