"""Historical Business Data Upload and Validation Schemas."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class UploadStatus(str, Enum):
    """Validation status for uploaded business historical records."""

    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"


class UploadRowError(BaseModel):
    """Specific row-level validation failure detail."""

    row: int = Field(..., description="1-indexed row number where the error occurred")
    column: Optional[str] = Field(default=None, description="Column header related to error")
    message: str = Field(..., description="Explanation of validation failure")


class UploadSummaryMetrics(BaseModel):
    """Computed summary metrics from valid historical rows."""

    total_rows: int = Field(..., ge=0, description="Total rows detected in data file")
    valid_rows: int = Field(..., ge=0, description="Number of rows passing all validations")
    invalid_rows: int = Field(..., ge=0, description="Number of rows failing validation")
    date_start: Optional[str] = Field(default=None, description="Earliest recorded date in data (ISO format)")
    date_end: Optional[str] = Field(default=None, description="Latest recorded date in data (ISO format)")
    total_revenue: Optional[float] = Field(default=None, description="Cumulative revenue across valid periods (INR)")
    average_monthly_revenue: Optional[float] = Field(
        default=None, description="Mean revenue per period across valid rows (INR)"
    )
    currency: str = Field(default="INR", description="Currency applied to monetary values")


class UploadDetailResponse(BaseModel):
    """Full detail response describing upload processing, status, errors, and preview."""

    upload_id: str = Field(..., description="Unique persistent identifier for this upload")
    filename: str = Field(..., description="Sanitized client filename")
    file_size_bytes: int = Field(..., ge=0, description="File size in bytes")
    status: UploadStatus = Field(..., description="Overall dataset validation outcome ('valid', 'invalid', 'warning')")
    summary: UploadSummaryMetrics = Field(..., description="Statistical summary of parsed data")
    errors: List[UploadRowError] = Field(default_factory=list, description="List of row-specific validation errors")
    preview: List[Dict[str, Any]] = Field(
        default_factory=list, description="Small preview of the first parsed rows (up to 10 rows)"
    )
    message: str = Field(..., description="Human-readable summary of upload outcome")
    created_at: datetime = Field(..., description="UTC creation timestamp")
