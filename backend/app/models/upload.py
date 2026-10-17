"""SQLAlchemy ORM model for Historical Data Uploads."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, JSON, String
from app.database import Base


class UploadRecord(Base):
    """Persistence model tracking historical business record uploads and validations."""

    __tablename__ = "uploads"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
        doc="Unique upload identifier (UUID4)",
    )
    filename = Column(
        String(255),
        nullable=False,
        doc="Sanitized original filename",
    )
    file_size_bytes = Column(
        Integer,
        nullable=False,
        doc="Byte size of uploaded file",
    )
    status = Column(
        String(20),
        nullable=False,
        default="valid",
        index=True,
        doc="Validation status ('valid', 'invalid', 'warning')",
    )
    total_rows = Column(
        Integer,
        nullable=False,
        default=0,
        doc="Total rows detected in uploaded dataset",
    )
    valid_rows = Column(
        Integer,
        nullable=False,
        default=0,
        doc="Count of compliant, validated data rows",
    )
    invalid_rows = Column(
        Integer,
        nullable=False,
        default=0,
        doc="Count of rows containing validation errors",
    )
    summary_data = Column(
        JSON,
        nullable=False,
        default=dict,
        doc="Aggregated statistical summary across valid periods",
    )
    errors_data = Column(
        JSON,
        nullable=False,
        default=list,
        doc="Detailed row-by-row error logs",
    )
    preview_data = Column(
        JSON,
        nullable=False,
        default=list,
        doc="First parsed rows sample (max 10 rows)",
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        doc="UTC record creation timestamp",
    )

    def __repr__(self) -> str:
        return f"<UploadRecord id={self.id} filename={self.filename} status={self.status}>"
