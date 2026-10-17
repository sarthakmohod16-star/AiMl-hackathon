"""Dashboard API router providing operational and portfolio analytics."""

from typing import Dict, List
from fastapi import APIRouter, Depends, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.analysis import AnalysisRecord, AnalysisStatus
from app.schemas.analysis import AnalysisListItem
from app.schemas.dashboard import DashboardSummaryResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Dashboard aggregate analytics summary",
    description=(
        "Returns verified aggregate metrics computed directly from stored analyses. "
        "Includes total volume, status distribution, mode distribution, and recent activity."
    ),
)
async def get_dashboard_summary(
    db: Session = Depends(get_db),
) -> DashboardSummaryResponse:
    """Calculate and return real database aggregates for the dashboard."""
    # Total count
    total = db.scalar(select(func.count(AnalysisRecord.id))) or 0

    # Lifecycle status distribution
    status_rows = db.execute(
        select(AnalysisRecord.status, func.count(AnalysisRecord.id)).group_by(AnalysisRecord.status)
    ).all()
    by_status: Dict[str, int] = {s.value: 0 for s in AnalysisStatus}
    for st, count in status_rows:
        if st in by_status:
            by_status[st] = count
        else:
            by_status[st] = count

    # Business mode distribution
    mode_rows = db.execute(
        select(AnalysisRecord.business_mode, func.count(AnalysisRecord.id)).group_by(AnalysisRecord.business_mode)
    ).all()
    by_mode: Dict[str, int] = {"new": 0, "existing": 0}
    for md, count in mode_rows:
        by_mode[md] = count

    # Up to 5 most recent analyses
    recent_records = db.scalars(
        select(AnalysisRecord).order_by(AnalysisRecord.created_at.desc(), AnalysisRecord.id.desc()).limit(5)
    ).all()

    recent_items = [
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
        for r in recent_records
    ]

    return DashboardSummaryResponse(
        total_analyses=total,
        by_status=by_status,
        by_mode=by_mode,
        recent_analyses=recent_items,
    )
