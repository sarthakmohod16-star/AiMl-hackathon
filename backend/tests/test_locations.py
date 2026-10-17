"""Unit and integration tests for Location Intelligence Service and Endpoints."""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.schemas.location import CompetitorClassification, GeocodedLocation
from app.services.location_service import (
    BaseLocationProvider,
    LocationProviderRateLimitError,
    LocationProviderTimeoutError,
    LocationProviderUnavailableError,
    LocationService,
    classify_competitor,
    haversine_distance,
)
from app.routers.locations import get_location_service


# 1. Unit Tests for Mathematics and Classification
def test_haversine_distance_same_point():
    """Distance between identical coordinates must be exactly 0.0 meters."""
    dist = haversine_distance(12.9716, 77.5946, 12.9716, 77.5946)
    assert dist == 0.0


def test_haversine_distance_known_points():
    """Verify known geographic distance between Indiranagar and MG Road, Bengaluru (~4.3 km)."""
    # Indiranagar: 12.9784, 77.6408
    # MG Road: 12.9756, 77.6066
    dist = haversine_distance(12.9784, 77.6408, 12.9756, 77.6066)
    assert 3500.0 < dist < 4200.0  # Approx 3.7 - 4.0 km straight-line


def test_competitor_classification_rules():
    """Test DIRECT, INDIRECT, and UNKNOWN classification boundaries."""
    # Direct matches
    assert classify_competitor("Cafe", "Blue Tokai Coffee Roasters", "cafe") == CompetitorClassification.DIRECT
    assert classify_competitor("Cafe", "Third Wave Espresso", "coffee_shop") == CompetitorClassification.DIRECT
    assert classify_competitor("Gym", "Cult.fit Fitness Center", "fitness_centre") == CompetitorClassification.DIRECT

    # Indirect matches
    assert classify_competitor("Cafe", "French Loaf Artisan Bakery", "bakery") == CompetitorClassification.INDIRECT
    assert classify_competitor("Cafe", "Burger King", "fast_food") == CompetitorClassification.INDIRECT
    assert classify_competitor("Gym", "Zumba & Salsa Dance Studio", "dance_studio") == CompetitorClassification.INDIRECT

    # Unknown matches (unrelated commercial POIs)
    assert classify_competitor("Cafe", "Apex Electrical Hardware", "hardware") == CompetitorClassification.UNKNOWN
    assert classify_competitor("Gym", "City Care Dental Clinic", "dentist") == CompetitorClassification.UNKNOWN


# 2. Mock Provider Setup for Router Tests
class MockLocationProvider(BaseLocationProvider):
    """Test mock provider returning deterministic data without network calls."""

    async def search_address(self, query: str):
        if "empty" in query.lower():
            return []
        return [
            GeocodedLocation(
                display_name="100 Feet Road, Indiranagar, Bengaluru, Karnataka, 560038, India",
                latitude=12.9716,
                longitude=77.5946,
                bounding_box=[12.9700, 12.9730, 77.5930, 77.5960],
                place_id="osm-place-101",
                osm_type="way",
                category="highway",
            ),
            GeocodedLocation(
                display_name="100 Feet Road, HAL 2nd Stage, Bengaluru, Karnataka, India",
                latitude=12.9680,
                longitude=77.6350,
                bounding_box=None,
                place_id="osm-place-102",
                osm_type="node",
                category="place",
            ),
        ]

    async def find_nearby_places(self, latitude: float, longitude: float, radius_meters: float):
        if radius_meters < 200:
            return []
        return [
            {
                "id": "node-1",
                "name": "Third Wave Coffee",
                "category": "cafe",
                "latitude": 12.9720,  # ~60m away
                "longitude": 77.5950,
            },
            {
                "id": "node-2",
                "name": "Glen's Bakehouse",
                "category": "bakery",
                "latitude": 12.9730,  # ~160m away
                "longitude": 77.5955,
            },
            {
                "id": "node-3",
                "name": "Sri Krishna Hardware",
                "category": "hardware",
                "latitude": 12.9740,  # ~300m away
                "longitude": 77.5960,
            },
            # Duplicate item to verify deduplication
            {
                "id": "node-4",
                "name": "Third Wave Coffee",
                "category": "cafe",
                "latitude": 12.9720,
                "longitude": 77.5950,
            },
        ]


@pytest.fixture
def mock_location_client(client: TestClient):
    """Override get_location_service dependency with test mock provider."""
    mock_service = LocationService(provider=MockLocationProvider())
    from app.main import app

    app.dependency_overrides[get_location_service] = lambda: mock_service
    yield client
    app.dependency_overrides.pop(get_location_service, None)


# 3. Router Integration Tests
def test_location_search_success(mock_location_client: TestClient):
    """POST /api/locations/search should return geocoded coordinates with attribution."""
    res = mock_location_client.post("/api/locations/search", json={"query": "100 Feet Road Bengaluru"})
    assert res.status_code == 200

    data = res.json()
    assert data["query"] == "100 Feet Road Bengaluru"
    assert data["count"] == 2
    assert len(data["results"]) == 2
    assert data["results"][0]["latitude"] == 12.9716
    assert data["results"][0]["longitude"] == 77.5946
    assert "OpenStreetMap" in data["attribution"]


def test_location_search_no_results(mock_location_client: TestClient):
    """POST /api/locations/search with non-matching query returns empty list with message."""
    res = mock_location_client.post("/api/locations/search", json={"query": "empty desert island xyz"})
    assert res.status_code == 200

    data = res.json()
    assert data["count"] == 0
    assert data["results"] == []
    assert "no matching locations found" in data["message"].lower()


def test_location_search_blank_query_fails(mock_location_client: TestClient):
    """Query of whitespace or length < 2 must return 422 validation error."""
    res = mock_location_client.post("/api/locations/search", json={"query": " "})
    assert res.status_code == 422

    data = res.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_location_analyze_success(mock_location_client: TestClient):
    """POST /api/locations/analyze should find nearby places, compute distances, and classify competitors."""
    payload = {
        "address": "Indiranagar 100ft Road",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "radius_meters": 1000.0,
        "target_category": "Cafe",
    }
    res = mock_location_client.post("/api/locations/analyze", json=payload)
    assert res.status_code == 200

    data = res.json()
    assert data["target_category"] == "Cafe"
    assert data["total_nearby_found"] == 3  # 4 minus 1 duplicate = 3
    assert data["direct_competitors_count"] == 1  # Third Wave Coffee
    assert data["indirect_competitors_count"] == 1  # Glen's Bakehouse
    assert data["unknown_count"] == 1  # Sri Krishna Hardware

    # Check sorting: closest first
    distances = [p["distance_meters"] for p in data["nearby_businesses"]]
    assert distances == sorted(distances)

    # Check disclosures and attribution
    assert len(data["limitations"]) > 0
    assert "OpenStreetMap" in data["attribution"]


def test_location_analyze_empty_radius(mock_location_client: TestClient):
    """POST /api/locations/analyze with tiny radius returns empty list without error."""
    payload = {
        "latitude": 12.9716,
        "longitude": 77.5946,
        "radius_meters": 150.0,  # Below mock threshold
        "target_category": "Bakery",
    }
    res = mock_location_client.post("/api/locations/analyze", json=payload)
    assert res.status_code == 200

    data = res.json()
    assert data["total_nearby_found"] == 0
    assert data["nearby_businesses"] == []
    assert data["direct_competitors_count"] == 0


def test_location_analyze_invalid_coordinates(mock_location_client: TestClient):
    """Latitude > 90 must fail validation with 422."""
    payload = {
        "latitude": 105.0,
        "longitude": 77.5946,
        "target_category": "Cafe",
    }
    res = mock_location_client.post("/api/locations/analyze", json=payload)
    assert res.status_code == 422

    data = res.json()
    fields = [d["field"] for d in data["error"]["details"]]
    assert "latitude" in fields


# 4. Error and Failure Handling Tests
def test_location_search_timeout_error(client: TestClient):
    """Provider timeout must return standardized 504 Gateway Timeout."""
    timeout_provider = AsyncMock(spec=BaseLocationProvider)
    timeout_provider.search_address.side_effect = LocationProviderTimeoutError("Nominatim timeout.")

    from app.main import app
    app.dependency_overrides[get_location_service] = lambda: LocationService(provider=timeout_provider)

    res = client.post("/api/locations/search", json={"query": "MG Road Bengaluru"})
    assert res.status_code == 504

    data = res.json()
    assert data["error"]["code"] == "HTTP_504"
    assert "timeout" in data["error"]["message"].lower()

    app.dependency_overrides.pop(get_location_service, None)


def test_location_analyze_rate_limit_error(client: TestClient):
    """Provider rate limit must return standardized 429 Too Many Requests."""
    rate_limit_provider = AsyncMock(spec=BaseLocationProvider)
    rate_limit_provider.find_nearby_places.side_effect = LocationProviderRateLimitError("Overpass rate limit.")

    from app.main import app
    app.dependency_overrides[get_location_service] = lambda: LocationService(provider=rate_limit_provider)

    res = client.post(
        "/api/locations/analyze",
        json={"latitude": 12.9716, "longitude": 77.5946, "target_category": "Cafe"},
    )
    assert res.status_code == 429

    data = res.json()
    assert data["error"]["code"] == "HTTP_429"
    assert "rate limit" in data["error"]["message"].lower()

    app.dependency_overrides.pop(get_location_service, None)


def test_location_provider_unavailable_error(client: TestClient):
    """Provider 500 error must return standardized 503 Service Unavailable."""
    down_provider = AsyncMock(spec=BaseLocationProvider)
    down_provider.search_address.side_effect = LocationProviderUnavailableError("OSM server is temporarily unavailable.")

    from app.main import app
    app.dependency_overrides[get_location_service] = lambda: LocationService(provider=down_provider)

    res = client.post("/api/locations/search", json={"query": "Brigade Road Bengaluru"})
    assert res.status_code == 503

    data = res.json()
    assert data["error"]["code"] == "HTTP_503"
    assert "unavailable" in data["error"]["message"].lower()

    app.dependency_overrides.pop(get_location_service, None)
