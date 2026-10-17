"""Dashboard Summary Schemas."""

from typing import Dict, List
from pydantic import BaseModel, Field
from app.schemas.analysis import AnalysisListItem


class DashboardSummaryResponse(BaseModel):
    """Aggregate metrics for executive and feasibility analysis dashboard."""

    total_analyses: int = Field(..., ge=0, description="Total number of stored analyses")
    by_status: Dict[str, int] = Field(
        ...,
        description="Counts grouped by lifecycle status (PENDING, PROCESSING, COMPLETED, FAILED)",
        examples=[{"PENDING": 4, "PROCESSING": 0, "COMPLETED": 2, "FAILED": 1}],
    )
    by_mode: Dict[str, int] = Field(
        ...,
        description="Counts grouped by business mode ('new', 'existing')",
        examples=[{"new": 5, "existing": 2}],
    )
    recent_analyses: List[AnalysisListItem] = Field(
        default_factory=list,
        description="List of the most recently initiated analyses (up to 5)",
    )
