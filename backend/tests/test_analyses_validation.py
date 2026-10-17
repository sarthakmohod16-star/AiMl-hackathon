"""Unit tests for Analysis Schemas and Validation Endpoint."""

from fastapi.testclient import TestClient


def make_valid_payload():
    """Helper returning a standard, valid analysis request payload."""
    return {
        "business": {
            "mode": "new",
            "name": "Kaveri Specialty Coffee",
            "category": "Cafe & Eatery",
            "description": "Artisan cafe serving specialty brews and fresh bakery items.",
        },
        "location": {
            "address": "100 Feet Road, Indiranagar, Bengaluru, Karnataka",
            "latitude": 12.9716,
            "longitude": 77.5946,
            "radius_meters": 1500.0,
        },
        "financial": {
            "currency": "INR",
            "initial_investment": 1500000.0,
            "working_capital": 400000.0,
            "average_customer_spend": 280.0,
            "expected_customers_per_day": 95,
            "operating_days_per_month": 30,
            "rent_per_month": 75000.0,
            "salaries_per_month": 90000.0,
            "inventory_or_cogs_per_month": 130000.0,
            "utilities_per_month": 18000.0,
            "other_expenses_per_month": 25000.0,
        },
        "projection": {
            "period_months": 24,
            "simulation_count": 1000,
            "scenario_set": ["conservative", "base", "aggressive"],
        },
    }


def test_validate_valid_new_business(client: TestClient):
    """POST /api/analyses/validate with valid new business payload should return 200."""
    payload = make_valid_payload()
    response = client.post("/api/analyses/validate", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["valid"] is True
    assert "successfully validated" in data["message"].lower()
    assert data["normalized_input"]["business"]["name"] == "Kaveri Specialty Coffee"
    assert data["normalized_input"]["financial"]["currency"] == "INR"
    assert len(data["limitations"]) > 0


def test_validate_existing_business_warning_without_history(client: TestClient):
    """Existing business mode without historical data reference should validate with a warning."""
    payload = make_valid_payload()
    payload["business"]["mode"] = "existing"
    payload["business"]["historical_data_id"] = None

    response = client.post("/api/analyses/validate", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["valid"] is True
    assert any("existing business mode selected without verified historical data" in w.lower() for w in data["warnings"])


def test_validate_existing_business_with_history(client: TestClient):
    """Existing business mode with historical data id should have no missing-history warning."""
    payload = make_valid_payload()
    payload["business"]["mode"] = "existing"
    payload["business"]["historical_data_id"] = "upload-hist-987"

    response = client.post("/api/analyses/validate", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["valid"] is True
    assert not any("historical data" in w.lower() for w in data["warnings"])


def test_validate_defaults_applied(client: TestClient):
    """Optional fields should take their documented defaults when omitted."""
    payload = make_valid_payload()
    del payload["location"]["radius_meters"]
    del payload["financial"]["currency"]
    del payload["financial"]["operating_days_per_month"]
    del payload["projection"]

    response = client.post("/api/analyses/validate", json=payload)
    assert response.status_code == 200

    norm = response.json()["normalized_input"]
    assert norm["location"]["radius_meters"] == 1000.0
    assert norm["financial"]["currency"] == "INR"
    assert norm["financial"]["operating_days_per_month"] == 30
    assert norm["projection"]["period_months"] == 12
    assert norm["projection"]["simulation_count"] == 1000


def test_validate_negative_rent_fails(client: TestClient):
    """Negative rent amount must return 422 with field-level error details."""
    payload = make_valid_payload()
    payload["financial"]["rent_per_month"] = -500.0

    response = client.post("/api/analyses/validate", json=payload)
    assert response.status_code == 422

    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    fields = [d["field"] for d in data["error"]["details"]]
    assert "financial.rent_per_month" in fields


def test_validate_invalid_coordinates(client: TestClient):
    """Latitude > 90 and longitude < -180 must fail validation."""
    payload = make_valid_payload()
    payload["location"]["latitude"] = 95.5
    payload["location"]["longitude"] = -195.0

    response = client.post("/api/analyses/validate", json=payload)
    assert response.status_code == 422

    data = response.json()
    fields = [d["field"] for d in data["error"]["details"]]
    assert "location.latitude" in fields
    assert "location.longitude" in fields


def test_validate_unsupported_business_mode(client: TestClient):
    """Unsupported business mode enum must return 422."""
    payload = make_valid_payload()
    payload["business"]["mode"] = "franchise_unsupported"

    response = client.post("/api/analyses/validate", json=payload)
    assert response.status_code == 422

    data = response.json()
    fields = [d["field"] for d in data["error"]["details"]]
    assert "business.mode" in fields


def test_validate_non_positive_customer_spend(client: TestClient):
    """Average customer spend of 0 or negative must fail validation."""
    payload = make_valid_payload()
    payload["financial"]["average_customer_spend"] = 0.0

    response = client.post("/api/analyses/validate", json=payload)
    assert response.status_code == 422

    data = response.json()
    fields = [d["field"] for d in data["error"]["details"]]
    assert "financial.average_customer_spend" in fields


def test_validate_invalid_projection_settings(client: TestClient):
    """Period months outside 1-60 and simulations outside 100-5000 must fail."""
    payload = make_valid_payload()
    payload["projection"]["period_months"] = 72
    payload["projection"]["simulation_count"] = 50

    response = client.post("/api/analyses/validate", json=payload)
    assert response.status_code == 422

    data = response.json()
    fields = [d["field"] for d in data["error"]["details"]]
    assert "projection.period_months" in fields
    assert "projection.simulation_count" in fields


def test_validate_unsupported_currency(client: TestClient):
    """Non-INR currency must be rejected."""
    payload = make_valid_payload()
    payload["financial"]["currency"] = "USD"

    response = client.post("/api/analyses/validate", json=payload)
    assert response.status_code == 422

    data = response.json()
    fields = [d["field"] for d in data["error"]["details"]]
    assert "financial.currency" in fields


def test_validate_missing_and_null_fields(client: TestClient):
    """Required fields passed as None or omitted must not silently turn into zero."""
    payload = make_valid_payload()
    payload["financial"]["salaries_per_month"] = None

    response = client.post("/api/analyses/validate", json=payload)
    assert response.status_code == 422

    data = response.json()
    fields = [d["field"] for d in data["error"]["details"]]
    assert "financial.salaries_per_month" in fields


def test_validate_blank_whitespace_name(client: TestClient):
    """Business name consisting only of whitespace should be rejected."""
    payload = make_valid_payload()
    payload["business"]["name"] = "    "

    response = client.post("/api/analyses/validate", json=payload)
    assert response.status_code == 422

    data = response.json()
    fields = [d["field"] for d in data["error"]["details"]]
    assert "business.name" in fields


def test_validate_zero_expected_customers_warning(client: TestClient):
    """Zero customers per day is syntactically allowed (ge=0) but returns a warning."""
    payload = make_valid_payload()
    payload["financial"]["expected_customers_per_day"] = 0

    response = client.post("/api/analyses/validate", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["valid"] is True
    assert any("customer count is 0" in w.lower() for w in data["warnings"])
