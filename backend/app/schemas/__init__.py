"""Schemas package initialization."""

from app.schemas.health import HealthResponse
from app.schemas.errors import ErrorEnvelope, ErrorBody, ErrorDetail
from app.schemas.location import (
    CompetitorClassification,
    LocationInput,
    LocationSearchRequest,
    GeocodedLocation,
    LocationSearchResponse,
    LocationAnalyzeRequest,
    NearbyPlace,
    LocationAnalyzeResponse,
)
from app.schemas.analysis import (
    BusinessMode,
    BusinessProfileInput,
    FinancialInputs,
    ProjectionSettings,
    AnalysisCreateRequest,
    AnalysisValidateResponse,
    AnalysisCreateResponse,
    AnalysisListItem,
    AnalysisListResponse,
    AnalysisDetailResponse,
)
from app.schemas.dashboard import DashboardSummaryResponse
from app.schemas.upload import (
    UploadStatus,
    UploadRowError,
    UploadSummaryMetrics,
    UploadDetailResponse,
)

__all__ = [
    "HealthResponse",
    "ErrorEnvelope",
    "ErrorBody",
    "ErrorDetail",
    "CompetitorClassification",
    "LocationInput",
    "LocationSearchRequest",
    "GeocodedLocation",
    "LocationSearchResponse",
    "LocationAnalyzeRequest",
    "NearbyPlace",
    "LocationAnalyzeResponse",
    "BusinessMode",
    "BusinessProfileInput",
    "FinancialInputs",
    "ProjectionSettings",
    "AnalysisCreateRequest",
    "AnalysisValidateResponse",
    "AnalysisCreateResponse",
    "AnalysisListItem",
    "AnalysisListResponse",
    "AnalysisDetailResponse",
    "DashboardSummaryResponse",
    "UploadStatus",
    "UploadRowError",
    "UploadSummaryMetrics",
    "UploadDetailResponse",
]
