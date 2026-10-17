"""Analyses API router for validation, creation, listing, and retrieval."""

import logging
import math
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.analysis import AnalysisRecord, AnalysisStatus
from app.schemas.analysis import (
    AnalysisCreateRequest,
    AnalysisCreateResponse,
    AnalysisDetailResponse,
    AnalysisListItem,
    AnalysisListResponse,
    AnalysisValidateResponse,
    BusinessMode,
)

logger = logging.getLogger("biztwin.analyses")

router = APIRouter(prefix="/analyses", tags=["Analyses"])


@router.post(
    "/validate",
    response_model=AnalysisValidateResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate and normalize analysis inputs",
    description=(
        "Validates and normalizes business profile, location, financial assumptions, "
        "and projection settings without persisting or running simulations. "
        "Provides feedback on missing historical data, input warnings, and documented limitations."
    ),
)
async def validate_analysis_input(
    payload: AnalysisCreateRequest,
) -> AnalysisValidateResponse:
    """Validate and normalize business analysis request without database persistence."""
    warnings: List[str] = []
    limitations: List[str] = [
        "This endpoint performs static validation and normalization only; no database record was created.",
        "Simulations and model scoring have not been executed. Use POST /api/analyses to run feasibility modeling.",
        "Revenue projections are based on user assumptions and do not represent guaranteed market outcomes.",
    ]

    # Business rule: Check existing business mode historical data linkage
    if payload.business.mode == BusinessMode.EXISTING and not payload.business.historical_data_id:
        warnings.append(
            "Existing business mode selected without verified historical data upload. "
            "Projections will rely purely on user-provided financial estimates with reduced baseline confidence."
        )

    # Business rule: Footfall sanity check
    if payload.financial.expected_customers_per_day == 0:
        warnings.append(
            "Expected daily customer count is 0. Estimated monthly revenue will be zero."
        )

    return AnalysisValidateResponse(
        valid=True,
        message="Analysis inputs successfully validated. Payload conforms to BizTwin MVP schema standards.",
        normalized_input=payload,
        warnings=warnings,
        limitations=limitations,
    )


@router.post(
    "",
    response_model=AnalysisCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create and persist a new feasibility analysis",
    description=(
        "Persists a new business feasibility analysis record in PENDING state. "
        "Feasibility simulations and location intelligence pipelines are currently in development "
        "and will execute in subsequent stages."
    ),
)
async def create_analysis(
    payload: AnalysisCreateRequest,
    db: Session = Depends(get_db),
) -> AnalysisCreateResponse:
    """Create a new analysis record with stable UUID and PENDING lifecycle status."""
    record = AnalysisRecord(
        business_mode=payload.business.mode.value,
        business_name=payload.business.name,
        business_category=payload.business.category,
        business_description=payload.business.description,
        address=payload.location.address,
        latitude=payload.location.latitude,
        longitude=payload.location.longitude,
        radius_meters=payload.location.radius_meters,
        currency=payload.financial.currency,
        input_data=payload.model_dump(),
        status=AnalysisStatus.PENDING.value,
    )

    try:
        db.add(record)
        db.commit()
        db.refresh(record)
    except Exception as e:
        db.rollback()
        logger.exception("Failed to persist analysis record: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database persistence failed while saving analysis record.",
        )

    logger.info("Persisted new analysis record [id=%s, mode=%s, name=%s]", record.id, record.business_mode, record.business_name)

    return AnalysisCreateResponse(
        id=record.id,
        status=record.status,
        created_at=record.created_at,
        business_name=record.business_name,
        business_mode=record.business_mode,
        business_category=record.business_category,
        currency=record.currency,
        message=(
            "Analysis record created with PENDING status. "
            "Feasibility simulation engine is currently under development and will be connected in future milestones."
        ),
    )


@router.get(
    "",
    response_model=AnalysisListResponse,
    status_code=status.HTTP_200_OK,
    summary="List paginated analysis records",
    description="Retrieve a paginated list of analysis records with optional filtering by status and business mode.",
)
async def list_analyses(
    page: int = Query(default=1, ge=1, description="Page index (1-based)"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    status: Optional[AnalysisStatus] = Query(default=None, description="Filter by status (PENDING, PROCESSING, COMPLETED, FAILED)"),
    mode: Optional[BusinessMode] = Query(default=None, description="Filter by business mode ('new', 'existing')"),
    db: Session = Depends(get_db),
) -> AnalysisListResponse:
    """List analysis summaries with pagination and optional filtering."""
    base_query = select(AnalysisRecord)

    if status is not None:
        base_query = base_query.where(AnalysisRecord.status == status.value)
    if mode is not None:
        base_query = base_query.where(AnalysisRecord.business_mode == mode.value)

    # Compute total matching records
    total = db.scalar(select(func.count()).select_from(base_query.subquery())) or 0
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    # Stable pagination: newest created_at first, tie-breaker on id descending
    offset = (page - 1) * page_size
    query = base_query.order_by(AnalysisRecord.created_at.desc(), AnalysisRecord.id.desc()).offset(offset).limit(page_size)
    records = db.scalars(query).all()

    items = [
        AnalysisListItem(
            id=r.id,
            status=r.status,
            business_mode=r.business_mode,
            business_name=r.business_name,
            business_category=r.business_category,
            address=r.address,
            currency=r.currency,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in records
    ]

    return AnalysisListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/{analysis_id}",
    response_model=AnalysisDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve single analysis by ID",
    description="Fetch complete stored analysis details, normalized inputs, and status history.",
)
async def get_analysis(
    analysis_id: str = Path(..., min_length=1, max_length=64, description="Analysis UUID identifier"),
    db: Session = Depends(get_db),
) -> AnalysisDetailResponse:
    """Retrieve full details of an analysis by its ID."""
    clean_id = analysis_id.strip()
    record = db.scalar(select(AnalysisRecord).where(AnalysisRecord.id == clean_id))

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with ID '{clean_id}' was not found.",
        )

    return AnalysisDetailResponse(
        id=record.id,
        status=record.status,
        created_at=record.created_at,
        updated_at=record.updated_at,
        business_mode=record.business_mode,
        business_name=record.business_name,
        business_category=record.business_category,
        business_description=record.business_description,
        address=record.address,
        latitude=record.latitude,
        longitude=record.longitude,
        radius_meters=record.radius_meters,
        currency=record.currency,
        input_data=record.input_data,
        error_message=record.error_message,
        results=record.results_data,
        limitations=(
            record.results_data.get("limitations")
            if (record.results_data and isinstance(record.results_data, dict) and "limitations" in record.results_data)
            else [
                "Simulation modeling and ML scoring are under active development and not yet computed for this record.",
                "Historical business performance is preserved as reported and not independently audited.",
            ]
        ),
    )


@router.post(
    "/{analysis_id}/execute",
    response_model=AnalysisDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute feasibility modeling and simulations",
    description="Runs deterministic financial calculations and Monte Carlo simulation distributions for this analysis.",
)
async def execute_analysis_endpoint(
    analysis_id: str = Path(..., min_length=1, max_length=64, description="Analysis UUID identifier"),
    db: Session = Depends(get_db),
) -> AnalysisDetailResponse:
    """Trigger execution of financial projections and Monte Carlo simulations for an analysis."""
    from app.services.analysis_service import AnalysisPipelineService

    clean_id = analysis_id.strip()
    record = db.scalar(select(AnalysisRecord).where(AnalysisRecord.id == clean_id))
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with ID '{clean_id}' was not found.",
        )

    AnalysisPipelineService.execute_analysis(clean_id, db=db)
    db.refresh(record)

    return AnalysisDetailResponse(
        id=record.id,
        status=record.status,
        created_at=record.created_at,
        updated_at=record.updated_at,
        business_mode=record.business_mode,
        business_name=record.business_name,
        business_category=record.business_category,
        business_description=record.business_description,
        address=record.address,
        latitude=record.latitude,
        longitude=record.longitude,
        radius_meters=record.radius_meters,
        currency=record.currency,
        input_data=record.input_data,
        error_message=record.error_message,
        results=record.results_data,
        limitations=(
            record.results_data.get("limitations")
            if (record.results_data and isinstance(record.results_data, dict) and "limitations" in record.results_data)
            else []
        ),
    )
