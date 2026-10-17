"""Tests for Health check and standard error responses."""

from fastapi.testclient import TestClient


def test_health_endpoint_success(client: TestClient):
    """GET /api/health should return 200 with service information and timestamp."""
    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "BizTwin API"
    assert "version" in data
    assert "timestamp" in data
    assert "environment" in data
    assert "X-Request-ID" in response.headers


def test_request_id_propagation(client: TestClient):
    """Providing an X-Request-ID header should be preserved and echoed back."""
    custom_id = "test-request-id-12345"
    response = client.get("/api/health", headers={"X-Request-ID": custom_id})
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == custom_id


def test_not_found_standard_error(client: TestClient):
    """Non-existent endpoints should return standardized error structure."""
    response = client.get("/api/does-not-exist")
    assert response.status_code == 404

    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"
    assert "message" in data["error"]
    assert "request_id" in data["error"]
