"""Standardized API Error Schemas."""

from typing import Any, List, Optional
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Field-specific validation error detail."""

    field: Optional[str] = Field(default=None, description="Path to invalid field")
    message: str = Field(..., description="Human-readable explanation of error")


class ErrorBody(BaseModel):
    """Normalized error payload body."""

    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error summary")
    details: Optional[List[ErrorDetail]] = Field(
        default=None, description="Granular field-level errors"
    )
    request_id: Optional[str] = Field(
        default=None, description="Unique identifier for request tracing"
    )


class ErrorEnvelope(BaseModel):
    """Top-level error response envelope matching API standards."""

    error: ErrorBody
