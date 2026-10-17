"""Provider-independent Location Intelligence and Competition Discovery Service."""

import logging
import math
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set, Tuple

import httpx

from app.config import Settings, get_settings
from app.schemas.location import (
    CompetitorClassification,
    GeocodedLocation,
    LocationAnalyzeRequest,
    LocationAnalyzeResponse,
    LocationSearchResponse,
    NearbyPlace,
)

logger = logging.getLogger("biztwin.location_service")


# Custom Exception Hierarchy
class LocationServiceError(Exception):
    """Base exception for location intelligence errors."""

    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class LocationProviderTimeoutError(LocationServiceError):
    """Raised when an external location provider times out."""

    def __init__(self, message: str = "External location provider request timed out."):
        super().__init__(message, status_code=504)


class LocationProviderRateLimitError(LocationServiceError):
    """Raised when an external location provider returns 429 Too Many Requests."""

    def __init__(self, message: str = "External location provider rate limit exceeded. Please retry later."):
        super().__init__(message, status_code=429)


class LocationProviderUnavailableError(LocationServiceError):
    """Raised when an external location provider fails or returns a 5xx error."""

    def __init__(self, message: str = "External location provider is temporarily unavailable."):
        super().__init__(message, status_code=503)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance between two geographic coordinates in meters.

    Uses spherical Earth radius R = 6,371,000 meters.
    Formula:
        a = sin²(Δφ/2) + cos φ1 ⋅ cos φ2 ⋅ sin²(Δλ/2)
        c = 2 ⋅ atan2( √a, √(1−a) )
        d = R ⋅ c
    """
    R = 6371000.0  # Mean radius of Earth in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2)
    )
    # Clip to [0, 1] to prevent floating point inaccuracies causing domain error in sqrt
    a = min(1.0, max(0.0, a))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 1)


# Explicit Taxonomy Mapping for Competitor Classification
CATEGORY_TAXONOMY: Dict[str, Dict[str, Set[str]]] = {
    "cafe": {
        "direct": {"cafe", "coffee", "roastery", "espresso", "cappuccino", "brew", "tearoom", "tea_room"},
        "indirect": {"bakery", "restaurant", "fast_food", "bistro", "ice_cream", "juice_bar", "dessert", "bar", "pub"},
    },
    "coffee": {
        "direct": {"cafe", "coffee", "roastery", "espresso", "cappuccino", "brew"},
        "indirect": {"bakery", "restaurant", "fast_food", "dessert"},
    },
    "bakery": {
        "direct": {"bakery", "pastry", "patisserie", "confectionery", "bakehouse"},
        "indirect": {"cafe", "coffee", "supermarket", "deli", "dessert"},
    },
    "gym": {
        "direct": {"gym", "fitness", "workout", "crossfit", "pilates", "yoga", "health_club", "bodybuilding"},
        "indirect": {"sports_centre", "swimming_pool", "martial_arts", "dance_studio", "spa", "physiotherapy"},
    },
    "fitness": {
        "direct": {"gym", "fitness", "workout", "crossfit", "pilates", "yoga", "health_club"},
        "indirect": {"sports_centre", "dance", "spa"},
    },
    "pharmacy": {
        "direct": {"pharmacy", "chemist", "drugstore", "apothecary", "medical_store"},
        "indirect": {"hospital", "clinic", "doctors", "optician", "dentist", "health", "herbalist"},
    },
    "grocery": {
        "direct": {"supermarket", "grocery", "convenience", "hypermarket", "provision_store", "general_store"},
        "indirect": {"greengrocer", "butcher", "bakery", "deli", "department_store", "organic"},
    },
    "supermarket": {
        "direct": {"supermarket", "grocery", "hypermarket"},
        "indirect": {"convenience", "greengrocer", "department_store"},
    },
    "restaurant": {
        "direct": {"restaurant", "diner", "bistro", "eatery", "trattoria"},
        "indirect": {"cafe", "fast_food", "food_court", "bar", "pub", "pizzeria"},
    },
}


def classify_competitor(
    target_category: str,
    place_name: str,
    place_category: Optional[str] = None,
) -> CompetitorClassification:
    """Classify a commercial place as DIRECT, INDIRECT, or UNKNOWN relative to target category.

    Strict rule: If no explicit taxonomy rule or strong direct match exists, return UNKNOWN.
    Never fabricates competitor relationships.
    """
    clean_target = target_category.strip().lower()
    clean_name = place_name.strip().lower()
    clean_cat = (place_category or "").strip().lower()

    # Direct match on name or category string
    if clean_target in clean_name or clean_target in clean_cat:
        return CompetitorClassification.DIRECT

    # Check taxonomy rules
    matched_taxonomy = None
    for key, rules in CATEGORY_TAXONOMY.items():
        if key in clean_target:
            matched_taxonomy = rules
            break

    if matched_taxonomy:
        # Check direct keywords
        for direct_term in matched_taxonomy["direct"]:
            if direct_term in clean_cat or direct_term in clean_name:
                return CompetitorClassification.DIRECT

        # Check indirect keywords
        for indirect_term in matched_taxonomy["indirect"]:
            if indirect_term in clean_cat or indirect_term in clean_name:
                return CompetitorClassification.INDIRECT

    # If place category exists and matches any target tokens
    target_tokens = set(clean_target.replace("&", " ").replace("/", " ").split())
    cat_tokens = set(clean_cat.replace("&", " ").replace("/", " ").replace("_", " ").split())
    name_tokens = set(clean_name.replace("&", " ").replace("/", " ").split())

    if target_tokens & cat_tokens:
        return CompetitorClassification.DIRECT
    if target_tokens & name_tokens:
        return CompetitorClassification.DIRECT

    # Default to UNKNOWN when no explicit relationship is verified
    return CompetitorClassification.UNKNOWN


class BaseLocationProvider(ABC):
    """Abstract interface for location search and proximity intelligence providers."""

    @abstractmethod
    async def search_address(self, query: str) -> List[GeocodedLocation]:
        """Geocode query string into candidate coordinates."""
        pass

    @abstractmethod
    async def find_nearby_places(
        self, latitude: float, longitude: float, radius_meters: float
    ) -> List[Dict[str, Any]]:
        """Discover commercial POIs within radius meters."""
        pass


class OSMLocationProvider(BaseLocationProvider):
    """OpenStreetMap provider implementation using Nominatim and Overpass API."""

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.user_agent = self.settings.osm_user_agent
        self.timeout = self.settings.location_request_timeout_seconds
        self.nominatim_url = self.settings.nominatim_base_url.rstrip("/")
        self.overpass_url = self.settings.overpass_base_url.rstrip("/")

    def _get_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": self.user_agent,
            "Accept": "application/json",
        }

    async def search_address(self, query: str) -> List[GeocodedLocation]:
        """Geocode an address query using OpenStreetMap Nominatim."""
        url = f"{self.nominatim_url}/search"
        params = {
            "q": query,
            "format": "jsonv2",
            "limit": 10,
            "addressdetails": 1,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=self._get_headers())

            if response.status_code == 429:
                logger.warning("Nominatim rate limit encountered for query: %s", query)
                raise LocationProviderRateLimitError("Nominatim geocoding rate limit reached.")

            if response.status_code >= 500:
                logger.error("Nominatim server returned %s for query: %s", response.status_code, query)
                raise LocationProviderUnavailableError("Nominatim geocoding service temporarily unavailable.")

            response.raise_for_status()
            data = response.json()

        except httpx.TimeoutException:
            logger.warning("Nominatim request timed out for query: %s", query)
            raise LocationProviderTimeoutError("Nominatim geocoding request timed out.")
        except (LocationServiceError, httpx.HTTPStatusError):
            raise
        except Exception as e:
            logger.exception("Unexpected error calling Nominatim: %s", e)
            raise LocationServiceError(f"Nominatim provider request failed: {str(e)}")

        results: List[GeocodedLocation] = []
        if not isinstance(data, list):
            return results

        for item in data:
            try:
                lat = float(item["lat"])
                lon = float(item["lon"])
                bbox = None
                if "boundingbox" in item and isinstance(item["boundingbox"], list) and len(item["boundingbox"]) == 4:
                    bbox = [float(x) for x in item["boundingbox"]]

                results.append(
                    GeocodedLocation(
                        display_name=item.get("display_name", ""),
                        latitude=lat,
                        longitude=lon,
                        bounding_box=bbox,
                        place_id=str(item.get("place_id", "")) if item.get("place_id") else None,
                        osm_type=item.get("osm_type"),
                        category=item.get("category") or item.get("type"),
                    )
                )
            except (KeyError, ValueError, TypeError) as err:
                logger.debug("Skipping malformed Nominatim entry: %s, error: %s", item, err)
                continue

        return results

    async def find_nearby_places(
        self, latitude: float, longitude: float, radius_meters: float
    ) -> List[Dict[str, Any]]:
        """Find nearby mapped commercial POIs via Overpass API within radius meters."""
        # Overpass QL querying amenity and shop nodes around coordinate
        query = f"""
        [out:json][timeout:8];
        (
          node["amenity"](around:{int(radius_meters)},{latitude},{longitude});
          node["shop"](around:{int(radius_meters)},{latitude},{longitude});
        );
        out body 100;
        """

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.overpass_url,
                    data={"data": query},
                    headers=self._get_headers(),
                )

            if response.status_code == 429:
                logger.warning("Overpass API rate limit reached for coords: %s, %s", latitude, longitude)
                raise LocationProviderRateLimitError("Overpass nearby places rate limit reached.")

            if response.status_code >= 500:
                logger.error("Overpass server returned %s", response.status_code)
                raise LocationProviderUnavailableError("Overpass API service temporarily unavailable.")

            response.raise_for_status()
            data = response.json()

        except httpx.TimeoutException:
            logger.warning("Overpass request timed out for coords: %s, %s", latitude, longitude)
            raise LocationProviderTimeoutError("Overpass nearby places request timed out.")
        except (LocationServiceError, httpx.HTTPStatusError):
            raise
        except Exception as e:
            logger.exception("Unexpected error calling Overpass API: %s", e)
            raise LocationServiceError(f"Overpass provider request failed: {str(e)}")

        elements = data.get("elements", [])
        places: List[Dict[str, Any]] = []

        seen: Set[Tuple[str, float, float]] = set()

        for el in elements:
            tags = el.get("tags", {})
            name = tags.get("name")
            if not name:
                continue

            lat = el.get("lat")
            lon = el.get("lon")
            if lat is None or lon is None:
                continue

            try:
                lat = float(lat)
                lon = float(lon)
            except (ValueError, TypeError):
                continue

            # Deduplication key: normalized name + rounded coords (3 decimals ~100m)
            dedup_key = (name.strip().lower(), round(lat, 3), round(lon, 3))
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            category = tags.get("amenity") or tags.get("shop") or tags.get("cuisine")
            places.append({
                "id": str(el.get("id")),
                "name": name.strip(),
                "category": category.strip() if category else None,
                "latitude": lat,
                "longitude": lon,
            })

        return places


class LocationService:
    """Service coordinator for location searches and proximity intelligence."""

    def __init__(self, provider: Optional[BaseLocationProvider] = None):
        self.provider = provider or OSMLocationProvider()

    async def geocode_address(self, query: str) -> LocationSearchResponse:
        """Search and geocode an address query into standardized candidate coordinates."""
        clean_query = query.strip()
        candidates = await self.provider.search_address(clean_query)

        message = None
        if not candidates:
            message = "No matching locations found for the specified query."

        return LocationSearchResponse(
            query=clean_query,
            count=len(candidates),
            results=candidates,
            attribution="Data © OpenStreetMap contributors, ODbL 1.0",
            message=message,
        )

    async def analyze_location(self, request: LocationAnalyzeRequest) -> LocationAnalyzeResponse:
        """Discover nearby mapped businesses, calculate Haversine distances, and classify competitors."""
        raw_places = await self.provider.find_nearby_places(
            latitude=request.latitude,
            longitude=request.longitude,
            radius_meters=request.radius_meters,
        )

        nearby_businesses: List[NearbyPlace] = []
        direct_count = 0
        indirect_count = 0
        unknown_count = 0

        # Provider-independent deduplication by normalized name and rounded coordinates
        seen: Set[Tuple[str, float, float]] = set()

        for p in raw_places:
            p_name = p.get("name", "").strip()
            if not p_name:
                continue

            dedup_key = (p_name.lower(), round(p["latitude"], 3), round(p["longitude"], 3))
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            dist = haversine_distance(
                request.latitude,
                request.longitude,
                p["latitude"],
                p["longitude"],
            )

            # Check if within radius
            if dist > request.radius_meters:
                continue

            classification = classify_competitor(
                target_category=request.target_category,
                place_name=p["name"],
                place_category=p.get("category"),
            )

            if classification == CompetitorClassification.DIRECT:
                direct_count += 1
            elif classification == CompetitorClassification.INDIRECT:
                indirect_count += 1
            else:
                unknown_count += 1

            nearby_businesses.append(
                NearbyPlace(
                    id=p.get("id"),
                    name=p["name"],
                    category=p.get("category"),
                    latitude=p["latitude"],
                    longitude=p["longitude"],
                    distance_meters=dist,
                    classification=classification,
                    source="OpenStreetMap / Overpass",
                )
            )

        # Sort by proximity: closest first
        nearby_businesses.sort(key=lambda x: x.distance_meters)

        return LocationAnalyzeResponse(
            center_latitude=request.latitude,
            center_longitude=request.longitude,
            radius_meters=request.radius_meters,
            target_category=request.target_category,
            total_nearby_found=len(nearby_businesses),
            direct_competitors_count=direct_count,
            indirect_competitors_count=indirect_count,
            unknown_count=unknown_count,
            nearby_businesses=nearby_businesses,
            attribution="Data © OpenStreetMap contributors, ODbL 1.0 (via Overpass API)",
            limitations=[
                "Mapped places depend on OpenStreetMap volunteer community data and may be incomplete or outdated.",
                "Map tags do not prove that a competitor is currently operational, profitable, or trading.",
                "Footfall, revenue, customer volume, and market share are strictly NOT inferred from map pins.",
            ],
        )
