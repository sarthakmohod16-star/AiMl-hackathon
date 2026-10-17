"""Uploads API router for business historical data parsing and validation."""

import logging
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, File, HTTPException, Path, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database import get_db
from app.models.upload import UploadRecord
from app.schemas.upload import (
    UploadDetailResponse,
    UploadRowError,
    UploadStatus,
    UploadSummaryMetrics,
)
from app.services.upload_service import (
    UploadProcessingError,
    UploadService,
)

logger = logging.getLogger("biztwin.uploads")

router = APIRouter(prefix="/uploads", tags=["Uploads"])


@router.post(
    "/business-history",
    response_model=UploadDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and validate historical business performance records",
    description=(
        "Upload a CSV (or Excel) file of past business operational records. "
        "Validates headers, date consistency, non-negative monetary values, duplicates, and row integrity. "
        "Provides granular row errors, statistical summary, and a preview without executing code or macros."
    ),
)
async def upload_business_history(
    file: UploadFile = File(..., description="CSV or Excel file with historical business performance"),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> UploadDetailResponse:
    """Process, validate, summarize, and persist historical business records upload."""
    upload_id = str(uuid.uuid4())
    filename = file.filename or "unknown.csv"

    try:
        content = await file.read()
    except Exception as e:
        logger.error("Failed to read uploaded file stream: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read uploaded file: {str(e)}",
        )

    try:
        result = UploadService.process_and_validate(
            upload_id=upload_id,
            filename=filename,
            content=content,
            max_bytes=settings.max_upload_size_bytes,
        )
    except UploadProcessingError as e:
        logger.warning("Upload validation failed for %s: %s", filename, e.message)
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
        )
    except Exception as e:
        logger.exception("Unexpected error processing file %s: %s", filename, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while parsing the file: {str(e)}",
        )

    # Persist upload metadata, summary, errors, and preview
    record = UploadRecord(
        id=upload_id,
        filename=result.filename,
        file_size_bytes=result.file_size_bytes,
        status=result.status.value,
        total_rows=result.summary.total_rows,
        valid_rows=result.summary.valid_rows,
        invalid_rows=result.summary.invalid_rows,
        summary_data=result.summary.model_dump(),
        errors_data=[e.model_dump() for e in result.errors],
        preview_data=result.preview,
        created_at=datetime.now(timezone.utc),
    )

    try:
        db.add(record)
        db.commit()
        db.refresh(record)
    except Exception as e:
        db.rollback()
        logger.exception("Failed to persist upload record: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to persist upload metadata to database.",
        )

    logger.info("Persisted upload record [id=%s, file=%s, status=%s]", upload_id, result.filename, result.status.value)
    return result


@router.get(
    "/{upload_id}",
    response_model=UploadDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve upload processing details by ID",
    description="Fetch validation outcome, statistical summary, row-specific error logs, and preview for a previously uploaded file.",
)
async def get_upload_detail(
    upload_id: str = Path(..., min_length=1, max_length=64, description="Upload UUID identifier"),
    db: Session = Depends(get_db),
) -> UploadDetailResponse:
    """Fetch stored validation and summary information for an upload."""
    clean_id = upload_id.strip()
    record = db.scalar(select(UploadRecord).where(UploadRecord.id == clean_id))

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Upload record with ID '{clean_id}' was not found.",
        )

    return UploadDetailResponse(
        upload_id=record.id,
        filename=record.filename,
        file_size_bytes=record.file_size_bytes,
        status=UploadStatus(record.status),
        summary=UploadSummaryMetrics(**record.summary_data),
        errors=[UploadRowError(**e) for e in record.errors_data],
        preview=record.preview_data,
        message=f"Upload status: {record.status}. {record.valid_rows} valid records out of {record.total_rows} total rows.",
        created_at=record.created_at,
    )
