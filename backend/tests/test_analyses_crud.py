"""Integration tests for Analysis CRUD and Dashboard Summary endpoints."""

from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.analysis import AnalysisRecord, AnalysisStatus
from tests.test_analyses_validation import make_valid_payload


def test_create_analysis_success(client: TestClient, db_session: Session):
    """POST /api/analyses should create record in PENDING status and return 201."""
    payload = make_valid_payload()
    response = client.post("/api/analyses", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert len(data["id"]) == 36  # UUID format
    assert data["status"] == "PENDING"
    assert data["business_name"] == payload["business"]["name"]
    assert data["business_mode"] == payload["business"]["mode"]
    assert data["currency"] == "INR"
    assert "simulation" in data["message"].lower()

    # Verify directly in database
    record = db_session.scalar(select(AnalysisRecord).where(AnalysisRecord.id == data["id"]))
    assert record is not None
    assert record.status == AnalysisStatus.PENDING.value
    assert record.business_name == payload["business"]["name"]
    assert record.input_data["financial"]["rent_per_month"] == payload["financial"]["rent_per_month"]


def test_create_analysis_validation_failure(client: TestClient):
    """POST /api/analyses with negative expenses must return 422 standard error."""
    payload = make_valid_payload()
    payload["financial"]["salaries_per_month"] = -50000.0

    response = client.post("/api/analyses", json=payload)
    assert response.status_code == 422

    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    fields = [d["field"] for d in data["error"]["details"]]
    assert "financial.salaries_per_month" in fields


def test_get_analysis_by_id_success(client: TestClient):
    """GET /api/analyses/{id} should return full details and input data."""
    payload = make_valid_payload()
    create_res = client.post("/api/analyses", json=payload)
    assert create_res.status_code == 201
    analysis_id = create_res.json()["id"]

    res = client.get(f"/api/analyses/{analysis_id}")
    assert res.status_code == 200

    detail = res.json()
    assert detail["id"] == analysis_id
    assert detail["status"] == "PENDING"
    assert detail["business_name"] == payload["business"]["name"]
    assert detail["address"] == payload["location"]["address"]
    assert detail["input_data"]["financial"]["rent_per_month"] == payload["financial"]["rent_per_month"]
    assert len(detail["limitations"]) > 0


def test_get_analysis_not_found(client: TestClient):
    """GET /api/analyses/{id} with unknown ID returns standardized 404."""
    unknown_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/analyses/{unknown_id}")
    assert response.status_code == 404

    data = response.json()
    assert data["error"]["code"] == "NOT_FOUND"
    assert unknown_id in data["error"]["message"]
    assert data["error"]["request_id"] is not None


def test_list_analyses_empty(client: TestClient):
    """GET /api/analyses on empty database or unmatched filters returns valid empty structure."""
    response = client.get("/api/analyses?status=FAILED")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []
    assert data["page"] == 1
    assert data["total_pages"] == 0


def test_list_analyses_pagination_and_filters(client: TestClient, db_session: Session):
    """Test listing records with pagination, status filter, and mode filter."""
    # Create 3 distinct records
    p1 = make_valid_payload()
    p1["business"]["name"] = "Bakery One"
    p1["business"]["mode"] = "new"

    p2 = make_valid_payload()
    p2["business"]["name"] = "Cafe Two"
    p2["business"]["mode"] = "new"

    p3 = make_valid_payload()
    p3["business"]["name"] = "Gym Three"
    p3["business"]["mode"] = "existing"

    r1 = client.post("/api/analyses", json=p1).json()["id"]
    r2 = client.post("/api/analyses", json=p2).json()["id"]
    r3 = client.post("/api/analyses", json=p3).json()["id"]

    # Mark r3 as COMPLETED in DB for filtering test
    rec3 = db_session.scalar(select(AnalysisRecord).where(AnalysisRecord.id == r3))
    rec3.status = AnalysisStatus.COMPLETED.value
    db_session.commit()

    # Pagination: page_size=2
    list_res = client.get("/api/analyses?page=1&page_size=2")
    assert list_res.status_code == 200
    pdata = list_res.json()
    assert pdata["total"] >= 3
    assert len(pdata["items"]) == 2
    assert pdata["page"] == 1
    assert pdata["page_size"] == 2

    # Filter by mode=existing
    existing_res = client.get("/api/analyses?mode=existing")
    assert existing_res.status_code == 200
    edata = existing_res.json()
    assert all(item["business_mode"] == "existing" for item in edata["items"])

    # Filter by status=COMPLETED
    completed_res = client.get("/api/analyses?status=COMPLETED")
    assert completed_res.status_code == 200
    cdata = completed_res.json()
    assert all(item["status"] == "COMPLETED" for item in cdata["items"])


def test_list_analyses_invalid_pagination_parameters(client: TestClient):
    """Invalid page (< 1) or page_size (> 100) must return 422."""
    res_page = client.get("/api/analyses?page=0")
    assert res_page.status_code == 422

    res_size = client.get("/api/analyses?page_size=500")
    assert res_size.status_code == 422


def test_dashboard_summary_aggregates(client: TestClient, db_session: Session):
    """GET /api/dashboard/summary should calculate accurate aggregate counts."""
    # Ensure known state by querying current count
    initial_total = client.get("/api/dashboard/summary").json()["total_analyses"]

    # Add 1 new PENDING and 1 existing FAILED
    p_new = make_valid_payload()
    p_new["business"]["name"] = "Dashboard Test Store"
    p_new["business"]["mode"] = "new"
    res1 = client.post("/api/analyses", json=p_new)
    assert res1.status_code == 201

    p_exist = make_valid_payload()
    p_exist["business"]["name"] = "Dashboard Branch Expansion"
    p_exist["business"]["mode"] = "existing"
    res2 = client.post("/api/analyses", json=p_exist)
    assert res2.status_code == 201
    id2 = res2.json()["id"]

    rec2 = db_session.scalar(select(AnalysisRecord).where(AnalysisRecord.id == id2))
    rec2.status = AnalysisStatus.FAILED.value
    rec2.error_message = "Test failure"
    db_session.commit()

    summary_res = client.get("/api/dashboard/summary")
    assert summary_res.status_code == 200

    data = summary_res.json()
    assert data["total_analyses"] == initial_total + 2
    assert "by_status" in data
    assert "PENDING" in data["by_status"]
    assert "FAILED" in data["by_status"]
    assert data["by_status"]["FAILED"] >= 1
    assert "by_mode" in data
    assert data["by_mode"]["new"] >= 1
    assert data["by_mode"]["existing"] >= 1
    assert len(data["recent_analyses"]) <= 5
    assert len(data["recent_analyses"]) > 0


def test_create_analysis_database_rollback_on_failure(client: TestClient):
    """Verify that if database commit fails, transaction is rolled back and returns 500 error."""
    payload = make_valid_payload()

    with patch.object(Session, "commit", side_effect=Exception("Simulated disk write failure")):
        response = client.post("/api/analyses", json=payload)
        assert response.status_code == 500
        data = response.json()
        assert data["error"]["code"] == "INTERNAL_SERVER_ERROR"
        assert "persistence failed" in data["error"]["message"].lower()
