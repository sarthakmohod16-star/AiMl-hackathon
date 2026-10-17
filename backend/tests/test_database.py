"""Tests for SQLite and SQLAlchemy persistence, models, transactions, and session management."""

import os
from pathlib import Path
import pytest
from sqlalchemy import inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import Base, get_db
from app.models.analysis import AnalysisRecord, AnalysisStatus


def test_table_creation(db_session: Session):
    """Verify that 'analyses' table is properly created with required columns."""
    inspector = inspect(db_session.bind)
    tables = inspector.get_table_names()
    assert "analyses" in tables

    columns = {col["name"] for col in inspector.get_columns("analyses")}
    expected_columns = {
        "id",
        "status",
        "created_at",
        "updated_at",
        "business_mode",
        "business_name",
        "business_category",
        "business_description",
        "address",
        "latitude",
        "longitude",
        "radius_meters",
        "currency",
        "input_data",
        "error_message",
        "results_data",
    }
    assert expected_columns.issubset(columns)


def test_insert_and_query_analysis_record(db_session: Session):
    """Verify creating, inserting, querying, and verifying JSON inputs on AnalysisRecord."""
    record = AnalysisRecord(
        business_mode="new",
        business_name="Green Leaf Organic Store",
        business_category="Grocery & Retail",
        business_description="Organic produce, bulk pantry goods, and cold-pressed oils.",
        address="Koramangala 4th Block, Bengaluru",
        latitude=12.9352,
        longitude=77.6245,
        radius_meters=1200.0,
        currency="INR",
        input_data={
            "business": {"mode": "new", "name": "Green Leaf"},
            "financial": {"rent_per_month": 45000.0, "average_customer_spend": 350.0},
        },
        status=AnalysisStatus.PENDING.value,
    )

    db_session.add(record)
    db_session.commit()

    retrieved = db_session.scalar(select(AnalysisRecord).where(AnalysisRecord.id == record.id))
    assert retrieved is not None
    assert retrieved.id == record.id
    assert retrieved.business_name == "Green Leaf Organic Store"
    assert retrieved.business_mode == "new"
    assert retrieved.status == AnalysisStatus.PENDING.value
    assert retrieved.currency == "INR"
    assert retrieved.created_at is not None
    assert retrieved.updated_at is not None
    assert retrieved.input_data["financial"]["rent_per_month"] == 45000.0
    assert retrieved.error_message is None


def test_valid_statuses_lifecycle(db_session: Session):
    """Verify updating record through all valid lifecycle statuses."""
    record = AnalysisRecord(
        business_mode="existing",
        business_name="Urban Fitness Studio",
        business_category="Fitness & Wellness",
        address="Indiranagar, Bengaluru",
        latitude=12.9780,
        longitude=77.6400,
        currency="INR",
        input_data={"mode": "existing"},
        status=AnalysisStatus.PENDING.value,
    )
    db_session.add(record)
    db_session.commit()

    # Transition to PROCESSING
    record.status = AnalysisStatus.PROCESSING.value
    db_session.commit()
    db_session.refresh(record)
    assert record.status == AnalysisStatus.PROCESSING.value

    # Transition to COMPLETED
    record.status = AnalysisStatus.COMPLETED.value
    db_session.commit()
    db_session.refresh(record)
    assert record.status == AnalysisStatus.COMPLETED.value

    # Transition to FAILED with error summary
    record.status = AnalysisStatus.FAILED.value
    record.error_message = "External provider rate limit exceeded."
    db_session.commit()
    db_session.refresh(record)
    assert record.status == AnalysisStatus.FAILED.value
    assert record.error_message == "External provider rate limit exceeded."


def test_invalid_status_check_constraint(db_session: Session):
    """CheckConstraint must reject invalid statuses."""
    record = AnalysisRecord(
        business_mode="new",
        business_name="Test Store",
        business_category="Retail",
        address="Sample Street",
        latitude=12.0,
        longitude=77.0,
        currency="INR",
        input_data={},
        status="INVALID_STATUS_VALUE",
    )
    db_session.add(record)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_transaction_rollback_on_failure(db_session: Session):
    """Verify that an uncommitted or failed transaction properly rolls back without leaving dirty state."""
    initial_count = len(db_session.scalars(select(AnalysisRecord)).all())

    # Create record but do not commit, then rollback
    record = AnalysisRecord(
        business_mode="new",
        business_name="Temporary Bakery",
        business_category="Bakery",
        address="MG Road",
        latitude=12.97,
        longitude=77.60,
        currency="INR",
        input_data={},
    )
    db_session.add(record)
    db_session.flush()  # Flushed to transaction
    db_session.rollback()

    final_count = len(db_session.scalars(select(AnalysisRecord)).all())
    assert final_count == initial_count


def test_session_cleanup_via_dependency():
    """Verify that get_db guarantees closing the session upon generator completion."""
    from unittest.mock import MagicMock

    gen = get_db()
    session = next(gen)
    assert isinstance(session, Session)

    # Attach spy to session.close
    close_spy = MagicMock(wraps=session.close)
    session.close = close_spy

    # Advance generator to simulate request completion
    with pytest.raises(StopIteration):
        next(gen)

    # Session.close() must have been called
    assert close_spy.called is True
    assert close_spy.call_count == 1


def test_local_development_database_not_touched(db_session: Session):
    """Verify test execution strictly uses in-memory SQLite and never touches biztwin.db on disk."""
    # Assert database session is bound to in-memory SQLite
    assert db_session.bind.engine.url.database == ":memory:"
    assert db_session.bind.engine.url.drivername == "sqlite"

    # Verify that the development database file was not created or modified during test run
    dev_db_path = Path(__file__).resolve().parent.parent / "biztwin.db"
    assert not dev_db_path.exists(), "Local development database 'biztwin.db' was created during tests!"
