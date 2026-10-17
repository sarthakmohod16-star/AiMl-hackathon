"""Location, Geocoding, and Nearby Intelligence Schemas."""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class CompetitorClassification(str, Enum):
    """Classification of nearby commercial POIs relative to target venture."""

    DIRECT = "direct"
    INDIRECT = "indirect"
    UNKNOWN = "unknown"


class LocationInput(BaseModel):
    """Selected location and search radius parameters for feasibility analysis."""

    address: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Street address, area name, or location identifier",
        examples=["Indiranagar, 100ft Road, Bengaluru, Karnataka"],
    )
    latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="Geographic latitude in decimal degrees (-90.0 to +90.0)",
        examples=[12.9716],
    )
    longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="Geographic longitude in decimal degrees (-180.0 to +180.0)",
        examples=[77.5946],
    )
    radius_meters: float = Field(
        default=1000.0,
        ge=100.0,
        le=50000.0,
        description="Analysis radius around the point in meters (100m to 50,000m / 50km)",
        examples=[1500.0],
    )

    @field_validator("address")
    @classmethod
    def clean_address(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Address cannot be empty or whitespace only.")
        return cleaned


class LocationSearchRequest(BaseModel):
    """Geocoding search query payload."""

    query: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Search address, landmark, locality, or city",
        examples=["Indiranagar 100ft Road Bengaluru"],
    )

    @field_validator("query")
    @classmethod
    def clean_query(cls, v: str) -> str:
        cleaned = v.strip()
        if len(cleaned) < 2:
            raise ValueError("Search query must be at least 2 characters long after trimming.")
        return cleaned


class GeocodedLocation(BaseModel):
    """Normalized geocoded point result."""

    display_name: str = Field(..., description="Formatted full address display name")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees")
    bounding_box: Optional[List[float]] = Field(
        default=None,
        description="Bounding coordinates [min_lat, max_lat, min_lon, max_lon] if available",
    )
    place_id: Optional[str] = Field(default=None, description="External provider place ID")
    osm_type: Optional[str] = Field(default=None, description="OSM entity type (node, way, relation)")
    category: Optional[str] = Field(default=None, description="Geocoded location category")


class LocationSearchResponse(BaseModel):
    """Search results response from geocoding provider."""

    query: str = Field(..., description="Original search query string")
    count: int = Field(..., ge=0, description="Number of matching locations found")
    results: List[GeocodedLocation] = Field(default_factory=list, description="List of geocoded candidate locations")
    attribution: str = Field(
        default="Data © OpenStreetMap contributors, ODbL 1.0",
        description="Mandatory data source attribution",
    )
    message: Optional[str] = Field(default=None, description="Informational message")


class LocationAnalyzeRequest(BaseModel):
    """Payload to discover and classify nearby commercial points of interest."""

    address: Optional[str] = Field(default=None, max_length=255, description="Optional textual address")
    latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="Search center latitude in decimal degrees",
        examples=[12.9716],
    )
    longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="Search center longitude in decimal degrees",
        examples=[77.5946],
    )
    radius_meters: float = Field(
        default=1000.0,
        ge=100.0,
        le=50000.0,
        description="Search radius around the point in meters (100 to 50,000)",
        examples=[1000.0],
    )
    target_category: str = Field(
        ...,
        min_length=1,
        max_length=80,
        description="Primary commercial category of the planned venture (e.g., Cafe, Pharmacy, Bakery)",
        examples=["Cafe"],
    )
    business_name: Optional[str] = Field(
        default=None,
        max_length=120,
        description="Planned business name to distinguish self-competition",
    )

    @field_validator("target_category")
    @classmethod
    def clean_target_category(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Target category cannot be empty.")
        return cleaned


class NearbyPlace(BaseModel):
    """Normalized commercial place / point of interest in proximity."""

    id: Optional[str] = Field(default=None, description="Provider POI identifier")
    name: str = Field(..., description="Business or place name")
    category: Optional[str] = Field(default=None, description="Mapped commercial tag/category")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="POI latitude")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="POI longitude")
    distance_meters: float = Field(..., ge=0.0, description="Great-circle distance in meters using Haversine formula")
    classification: CompetitorClassification = Field(
        ...,
        description="Competition classification ('direct', 'indirect', or 'unknown')",
    )
    source: str = Field(default="OpenStreetMap / Overpass", description="Data provider source")


class LocationAnalyzeResponse(BaseModel):
    """Proximity intelligence and commercial density response."""

    center_latitude: float = Field(..., description="Latitude of analysis center")
    center_longitude: float = Field(..., description="Longitude of analysis center")
    radius_meters: float = Field(..., description="Analysis radius in meters")
    target_category: str = Field(..., description="Target business category")
    total_nearby_found: int = Field(..., ge=0, description="Total mapped businesses found within radius")
    direct_competitors_count: int = Field(..., ge=0, description="Count of direct competitors")
    indirect_competitors_count: int = Field(..., ge=0, description="Count of indirect/adjacent competitors")
    unknown_count: int = Field(..., ge=0, description="Count of unclassified nearby commercial POIs")
    nearby_businesses: List[NearbyPlace] = Field(
        default_factory=list,
        description="List of nearby commercial POIs ordered by distance (closest first)",
    )
    attribution: str = Field(
        default="Data © OpenStreetMap contributors, ODbL 1.0 (via Overpass API)",
        description="Mandatory provider attribution",
    )
    limitations: List[str] = Field(
        default_factory=lambda: [
            "Mapped places depend on OpenStreetMap volunteer community data and may be incomplete or outdated.",
            "Map tags do not prove that a competitor is currently operational, profitable, or trading.",
            "Footfall, revenue, customer volume, and market share are strictly NOT inferred from map pins.",
        ],
        description="Limitations and disclosure statements",
    )
