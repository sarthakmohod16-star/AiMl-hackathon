"""SQLAlchemy ORM model for Analysis records."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Float,
    Index,
    JSON,
    String,
    Text,
)
from app.database import Base


class AnalysisStatus(str, Enum):
    """Lifecycle statuses for feasibility analysis jobs."""

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AnalysisRecord(Base):
    """Persistence model for feasibility analyses and lifecycle statuses."""

    __tablename__ = "analyses"

    # Primary Key - Stable UUID
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
        doc="Unique analysis identifier (UUID4)",
    )

    # Lifecycle & Timestamps
    status = Column(
        String(20),
        nullable=False,
        default=AnalysisStatus.PENDING.value,
        index=True,
        doc="Current analysis job lifecycle status",
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        doc="UTC record creation timestamp",
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        doc="UTC record last updated timestamp",
    )

    # Business Profile
    business_mode = Column(
        String(20),
        nullable=False,
        doc="Business mode: 'new' or 'existing'",
    )
    business_name = Column(
        String(120),
        nullable=False,
        index=True,
        doc="Name of business or venture",
    )
    business_category = Column(
        String(80),
        nullable=False,
        index=True,
        doc="Industry or commercial category",
    )
    business_description = Column(
        Text,
        nullable=True,
        doc="Optional business description",
    )

    # Location Information
    address = Column(
        String(255),
        nullable=False,
        doc="Physical address or area description",
    )
    latitude = Column(
        Float,
        nullable=False,
        doc="Geographic latitude in decimal degrees",
    )
    longitude = Column(
        Float,
        nullable=False,
        doc="Geographic longitude in decimal degrees",
    )
    radius_meters = Column(
        Float,
        nullable=False,
        default=1000.0,
        doc="Target search radius in meters",
    )

    # Financial & Currency
    currency = Column(
        String(3),
        nullable=False,
        default="INR",
        doc="ISO 4217 currency code (e.g. INR)",
    )

    # Input Payload Archive
    input_data = Column(
        JSON,
        nullable=False,
        doc="Complete normalized input parameters snapshot",
    )

    # Optional Error Details for Failed Analyses
    error_message = Column(
        Text,
        nullable=True,
        doc="Human-readable reason for analysis failure, if applicable",
    )

    # Computed Results, Financial Projections, and Scenario Simulations
    results_data = Column(
        JSON,
        nullable=True,
        doc="Computed feasibility metrics, financial trajectory, and Monte Carlo scenarios",
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')",
            name="check_analysis_valid_status",
        ),
        Index("idx_analyses_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<AnalysisRecord id={self.id} status={self.status} business={self.business_name}>"
