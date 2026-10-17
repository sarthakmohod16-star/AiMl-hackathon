"""Business and Feasibility Analysis Schemas."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from app.schemas.location import LocationInput


class BusinessMode(str, Enum):
    """Operational mode of the business being assessed."""

    NEW = "new"
    EXISTING = "existing"


class BusinessProfileInput(BaseModel):
    """Business profile inputs defining the business nature and scope."""

    mode: BusinessMode = Field(
        ...,
        description="Business mode: 'new' (greenfield launch) or 'existing' (expansion/branching)",
        examples=["new"],
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=120,
        description="Business or venture name",
        examples=["Brew & Bite Artisan Cafe"],
    )
    category: str = Field(
        ...,
        min_length=1,
        max_length=80,
        description="Business industry or commercial category",
        examples=["Cafe & Bakery"],
    )
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional brief summary of the business concept, target demographic, or offerings",
        examples=["Specialty coffee and light snacks targeting students and professionals."],
    )
    historical_data_id: Optional[str] = Field(
        default=None,
        description="Optional upload ID of verified historical business records (for existing businesses only)",
    )

    @field_validator("name", "category")
    @classmethod
    def strip_and_validate_nonempty(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Field cannot be empty or whitespace only.")
        return cleaned


class FinancialInputs(BaseModel):
    """Financial parameters and baseline assumptions in INR currency."""

    currency: str = Field(
        default="INR",
        min_length=3,
        max_length=3,
        description="Supported ISO 4217 currency code. Default is INR (₹).",
        examples=["INR"],
    )
    initial_investment: float = Field(
        ...,
        ge=0.0,
        description="One-time upfront capital expenditure (CapEx) in INR (fit-out, equipment, licensing)",
        examples=[1200000.0],
    )
    working_capital: float = Field(
        ...,
        ge=0.0,
        description="Initial cash reserve allocated for operating liquidity in INR",
        examples=[300000.0],
    )
    average_customer_spend: float = Field(
        ...,
        gt=0.0,
        description="Average ticket size or transaction value per customer in INR (> 0)",
        examples=[250.0],
    )
    expected_customers_per_day: int = Field(
        ...,
        ge=0,
        description="Estimated daily customer footfall / transactions (>= 0)",
        examples=[80],
    )
    operating_days_per_month: int = Field(
        default=30,
        ge=1,
        le=31,
        description="Estimated operational days per calendar month (1 to 31)",
        examples=[30],
    )
    rent_per_month: float = Field(
        ...,
        ge=0.0,
        description="Monthly lease or rent for physical space in INR (>= 0)",
        examples=[65000.0],
    )
    salaries_per_month: float = Field(
        ...,
        ge=0.0,
        description="Monthly total payroll / staff compensation in INR (>= 0)",
        examples=[85000.0],
    )
    inventory_or_cogs_per_month: float = Field(
        ...,
        ge=0.0,
        description="Monthly cost of goods sold (COGS) / raw materials in INR (>= 0)",
        examples=[120000.0],
    )
    utilities_per_month: float = Field(
        ...,
        ge=0.0,
        description="Monthly utilities (electricity, water, internet) in INR (>= 0)",
        examples=[15000.0],
    )
    other_expenses_per_month: float = Field(
        ...,
        ge=0.0,
        description="Monthly miscellaneous overhead (marketing, maintenance, insurance) in INR (>= 0)",
        examples=[20000.0],
    )

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        upper = v.strip().upper()
        if upper != "INR":
            raise ValueError(f"Unsupported currency '{upper}'. Only 'INR' is supported in this release.")
        return upper


class ProjectionSettings(BaseModel):
    """Configuration for simulation horizon and scenario modeling."""

    period_months: int = Field(
        default=12,
        ge=1,
        le=60,
        description="Financial projection horizon in months (1 to 60)",
        examples=[12],
    )
    simulation_count: int = Field(
        default=1000,
        ge=100,
        le=5000,
        description="Number of stochastic simulation iterations (100 to 5000)",
        examples=[1000],
    )
    scenario_set: List[str] = Field(
        default_factory=lambda: ["conservative", "base", "aggressive"],
        description="List of scenario modeling sets to generate",
        examples=[["conservative", "base", "aggressive"]],
    )


class AnalysisCreateRequest(BaseModel):
    """Comprehensive request payload to initiate or validate feasibility analysis."""

    business: BusinessProfileInput
    location: LocationInput
    financial: FinancialInputs
    projection: ProjectionSettings = Field(default_factory=ProjectionSettings)


class AnalysisValidateResponse(BaseModel):
    """Normalized response confirming validity without executing persistence or simulations."""

    valid: bool = Field(
        default=True,
        description="Indicates whether the payload passed all schema and business rules",
    )
    message: str = Field(
        ...,
        description="Human-readable validation summary",
    )
    normalized_input: AnalysisCreateRequest = Field(
        ...,
        description="Cleaned and validated input payload ready for submission",
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Non-blocking warnings or guidance regarding inputs",
    )
    limitations: List[str] = Field(
        default_factory=list,
        description="Documented assumptions, boundaries, and scope constraints",
    )


class AnalysisCreateResponse(BaseModel):
    """Response returned upon successful creation and persistence of an analysis job."""

    id: str = Field(..., description="Unique persistent identifier for the analysis")
    status: str = Field(default="PENDING", description="Current lifecycle state (PENDING)")
    created_at: datetime = Field(..., description="UTC creation timestamp")
    business_name: str = Field(..., description="Business display name")
    business_mode: str = Field(..., description="Business operational mode")
    business_category: str = Field(..., description="Business category")
    currency: str = Field(..., description="Currency code (INR)")
    message: str = Field(
        default="Analysis record created with PENDING status. Feasibility simulation is currently in development.",
        description="Informational status message",
    )


class AnalysisListItem(BaseModel):
    """Compact summary of an analysis for paginated lists and dashboard views."""

    id: str = Field(..., description="Unique analysis identifier")
    status: str = Field(..., description="Lifecycle status")
    business_mode: str = Field(..., description="Operational mode ('new' or 'existing')")
    business_name: str = Field(..., description="Business name")
    business_category: str = Field(..., description="Business category")
    address: str = Field(..., description="Location address")
    currency: str = Field(..., description="Currency code")
    created_at: datetime = Field(..., description="UTC creation timestamp")
    updated_at: datetime = Field(..., description="UTC last updated timestamp")


class AnalysisListResponse(BaseModel):
    """Paginated list envelope for analysis records."""

    items: List[AnalysisListItem] = Field(..., description="List of matching analysis summaries")
    total: int = Field(..., ge=0, description="Total matching records across all pages")
    page: int = Field(..., ge=1, description="Current page number (1-indexed)")
    page_size: int = Field(..., ge=1, description="Number of items per page")
    total_pages: int = Field(..., ge=0, description="Total available pages")


class AnalysisDetailResponse(BaseModel):
    """Comprehensive detail representation of a single analysis record."""

    id: str = Field(..., description="Unique persistent analysis identifier")
    status: str = Field(..., description="Current lifecycle status")
    created_at: datetime = Field(..., description="UTC creation timestamp")
    updated_at: datetime = Field(..., description="UTC last updated timestamp")
    business_mode: str = Field(..., description="Business mode")
    business_name: str = Field(..., description="Business name")
    business_category: str = Field(..., description="Business category")
    business_description: Optional[str] = Field(default=None, description="Business description")
    address: str = Field(..., description="Location address")
    latitude: float = Field(..., description="Location latitude")
    longitude: float = Field(..., description="Location longitude")
    radius_meters: float = Field(..., description="Search radius in meters")
    currency: str = Field(..., description="Currency code")
    input_data: Dict[str, Any] = Field(..., description="Archive of normalized input parameters")
    error_message: Optional[str] = Field(default=None, description="Failure reason if job failed")
    results: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Computed feasibility projections, Monte Carlo scenarios, and risk metrics if completed",
    )
    limitations: List[str] = Field(
        default_factory=lambda: [
            "Simulation modeling and ML scoring are under active development and not yet computed for this record.",
            "Historical business performance is preserved as reported and not independently audited.",
        ],
        description="Active limitations and boundary notes",
    )
