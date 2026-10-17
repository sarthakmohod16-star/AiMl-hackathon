"""Health check router."""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from app.config import Settings, get_settings
from app.schemas.health import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse, summary="Service Health Check")
async def get_health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """Return current API status, service name, version, and server timestamp."""
    return HealthResponse(
        status="healthy",
        service=settings.app_name,
        version=settings.app_version,
        timestamp=datetime.now(timezone.utc),
        environment=settings.environment,
    )
