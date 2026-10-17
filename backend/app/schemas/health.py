"""Health Check Schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """API health check response model."""

    status: str = Field(default="healthy", description="Current service health status")
    service: str = Field(..., description="Service display name")
    version: str = Field(..., description="Application semantic version")
    timestamp: datetime = Field(..., description="Current UTC timestamp")
    environment: str = Field(..., description="Active runtime environment")
