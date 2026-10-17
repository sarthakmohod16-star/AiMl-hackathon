"""Unit and integration tests for Historical Data Uploads and Validation."""

import io
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.upload import UploadRecord


def make_sample_csv_bytes(rows=None) -> bytes:
    """Helper creating standard CSV bytes."""
    default_rows = [
        "date,revenue,operating_expenses,customers,cogs",
        "2025-01,150000,90000,450,40000",
        "2025-02,165000,92000,480,44000",
        "2025-03,180000,95000,520,48000",
    ]
    csv_text = "\n".join(rows or default_rows)
    return csv_text.encode("utf-8")


def make_sample_excel_bytes() -> bytes:
    """Helper generating an in-memory .xlsx file."""
    df = pd.DataFrame([
        {"period": "2025-01", "sales": 120000.0, "expenses": 75000.0, "footfall": 320},
        {"period": "2025-02", "sales": 135000.0, "expenses": 78000.0, "footfall": 360},
    ])
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    return out.getvalue()


def test_upload_valid_csv(client: TestClient, db_session: Session):
    """POST /api/uploads/business-history with valid CSV should return 201 and persist metadata."""
    content = make_sample_csv_bytes()
    files = {"file": ("cafe_history_q1.csv", content, "text/csv")}

    res = client.post("/api/uploads/business-history", files=files)
    assert res.status_code == 201

    data = res.json()
    assert "upload_id" in data
    assert data["filename"] == "cafe_history_q1.csv"
    assert data["status"] == "valid"
    assert data["summary"]["total_rows"] == 3
    assert data["summary"]["valid_rows"] == 3
    assert data["summary"]["invalid_rows"] == 0
    assert data["summary"]["total_revenue"] == 495000.0
    assert data["summary"]["date_start"] == "2025-01"
    assert data["summary"]["date_end"] == "2025-03"
    assert len(data["preview"]) == 3
    assert len(data["errors"]) == 0

    # Verify directly in SQLite test database
    record = db_session.scalar(select(UploadRecord).where(UploadRecord.id == data["upload_id"]))
    assert record is not None
    assert record.filename == "cafe_history_q1.csv"
    assert record.status == "valid"
    assert record.valid_rows == 3


def test_upload_valid_excel(client: TestClient):
    """POST /api/uploads/business-history with Excel (.xlsx) file should parse and map aliased headers."""
    content = make_sample_excel_bytes()
    files = {
        "file": (
            "financial_statements.xlsx",
            content,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }

    res = client.post("/api/uploads/business-history", files=files)
    assert res.status_code == 201

    data = res.json()
    assert data["status"] == "valid"
    assert data["summary"]["valid_rows"] == 2
    assert data["summary"]["total_revenue"] == 255000.0


def test_get_upload_by_id(client: TestClient):
    """GET /api/uploads/{id} returns full stored metadata, statistics, and preview."""
    content = make_sample_csv_bytes()
    upload_res = client.post(
        "/api/uploads/business-history",
        files={"file": ("history.csv", content, "text/csv")},
    )
    assert upload_res.status_code == 201
    upload_id = upload_res.json()["upload_id"]

    res = client.get(f"/api/uploads/{upload_id}")
    assert res.status_code == 200

    data = res.json()
    assert data["upload_id"] == upload_id
    assert data["summary"]["valid_rows"] == 3
    assert len(data["preview"]) == 3


def test_get_upload_not_found(client: TestClient):
    """GET /api/uploads/{id} with unknown ID returns standardized 404."""
    unknown_id = "00000000-0000-0000-0000-000000000000"
    res = client.get(f"/api/uploads/{unknown_id}")
    assert res.status_code == 404

    data = res.json()
    assert data["error"]["code"] == "NOT_FOUND"
    assert unknown_id in data["error"]["message"]


def test_upload_missing_required_columns(client: TestClient):
    """Missing required columns must return 400 with informative message."""
    invalid_csv = "date,customer_notes\n2025-01,great month\n".encode("utf-8")
    files = {"file": ("incomplete.csv", invalid_csv, "text/csv")}

    res = client.post("/api/uploads/business-history", files=files)
    assert res.status_code == 400

    data = res.json()
    assert data["error"]["code"] == "BAD_REQUEST"
    assert "missing required columns" in data["error"]["message"].lower()


def test_upload_empty_file_rejected(client: TestClient):
    """Empty 0-byte file must return 400."""
    files = {"file": ("empty.csv", b"", "text/csv")}
    res = client.post("/api/uploads/business-history", files=files)
    assert res.status_code == 400

    data = res.json()
    assert "empty" in data["error"]["message"].lower()


def test_upload_unsupported_file_extension(client: TestClient):
    """Unsupported extension like .pdf or .txt must be rejected."""
    files = {"file": ("annual_report.pdf", b"%PDF-1.4...", "application/pdf")}
    res = client.post("/api/uploads/business-history", files=files)
    assert res.status_code == 400

    data = res.json()
    assert "unsupported file format" in data["error"]["message"].lower()


def test_upload_row_validation_errors(client: TestClient):
    """Malformed rows (negative revenue, duplicate date, invalid dates) return warning status and row logs."""
    rows = [
        "date,revenue,operating_expenses",
        "2025-01,100000,60000",        # Row 2: Valid
        "2025-02,-15000,50000",        # Row 3: Negative revenue
        "invalid-date,120000,55000",    # Row 4: Bad date format
        "2025-01,110000,58000",        # Row 5: Duplicate date
    ]
    content = "\n".join(rows).encode("utf-8")
    files = {"file": ("dirty_data.csv", content, "text/csv")}

    res = client.post("/api/uploads/business-history", files=files)
    assert res.status_code == 201

    data = res.json()
    assert data["status"] == "warning"
    assert data["summary"]["total_rows"] == 4
    assert data["summary"]["valid_rows"] == 1
    assert data["summary"]["invalid_rows"] == 3
    assert len(data["errors"]) >= 3

    # Verify line numbers
    error_rows = [err["row"] for err in data["errors"]]
    assert 3 in error_rows  # Row 3 negative revenue
    assert 4 in error_rows  # Row 4 invalid date
    assert 5 in error_rows  # Row 5 duplicate date


def test_upload_file_size_exceeded(client: TestClient):
    """File exceeding max_upload_size_bytes must return 413."""
    # Test setting a tiny max size through the test client
    huge_csv = make_sample_csv_bytes()

    from app.services.upload_service import UploadService, UploadProcessingError
    with pytest.raises(UploadProcessingError) as exc_info:
        UploadService.validate_file_metadata("large.csv", huge_csv, max_bytes=10)
    assert exc_info.value.status_code == 413
