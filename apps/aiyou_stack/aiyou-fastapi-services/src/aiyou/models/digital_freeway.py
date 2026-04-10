"""
Digital Freeway Pydantic Models
===============================

Request/Response schemas for Digital Freeway ROI Calculator API.
"""

from enum import StrEnum

from pydantic import BaseModel, Field


class CustomerType(StrEnum):
    """Customer type for ROI calculation"""

    TESLA = "tesla"
    WAYMO = "waymo"
    DOT = "dot"


class LocationType(StrEnum):
    """Geographic location for congestion data"""

    US_AVG = "us_avg"
    LA = "la"
    NYC_CHICAGO = "nyc_chicago"


# =============================================================================
# Request Models
# =============================================================================


class ROICalculationRequest(BaseModel):
    """Request model for ROI calculation"""

    customer_type: CustomerType = Field(
        default=CustomerType.TESLA, description="Customer type (tesla, waymo, dot)"
    )
    fleet_size: int = Field(
        default=1_000_000, ge=1, le=100_000_000, description="Number of vehicles in fleet"
    )
    congestion_reduction_pct: float = Field(
        default=0.20, ge=0.10, le=0.30, description="Congestion reduction percentage (0.10 to 0.30)"
    )
    crash_reduction_pct: float = Field(
        default=0.05, ge=0.02, le=0.10, description="Crash reduction percentage (0.02 to 0.10)"
    )
    location: LocationType = Field(
        default=LocationType.US_AVG, description="Geographic location for congestion data"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "customer_type": "tesla",
                "fleet_size": 1000000,
                "congestion_reduction_pct": 0.20,
                "crash_reduction_pct": 0.05,
                "location": "us_avg",
            }
        }


class ScenarioComparisonRequest(BaseModel):
    """Request model for scenario comparison"""

    fleet_size: int = Field(
        default=1_000_000, ge=1, le=100_000_000, description="Number of vehicles in fleet"
    )
    location: LocationType = Field(
        default=LocationType.US_AVG, description="Geographic location for congestion data"
    )


class NationalImpactRequest(BaseModel):
    """Request model for national impact calculation"""

    congestion_reduction_pct: float = Field(
        default=0.20, ge=0.10, le=0.30, description="Congestion reduction percentage"
    )
    crash_reduction_pct: float = Field(
        default=0.05, ge=0.02, le=0.10, description="Crash reduction percentage"
    )
    adoption_pct: float = Field(
        default=1.0, ge=0.01, le=1.0, description="Vehicle adoption percentage (0.01 to 1.0)"
    )


# =============================================================================
# Response Models
# =============================================================================


class CongestionSavingsResponse(BaseModel):
    """Congestion savings breakdown"""

    location: str
    base_annual_cost_usd: float
    base_hours_lost: float
    reduction_pct: float
    annual_savings_usd: float
    hours_saved: float


class CrashSavingsResponse(BaseModel):
    """Crash savings breakdown"""

    base_cost_per_vehicle_usd: float
    reduction_pct: float
    annual_savings_usd: float


class TotalsResponse(BaseModel):
    """Total savings summary"""

    annual_savings_usd: float
    annual_fee_usd: float
    net_savings_usd: float
    roi_multiple: float
    roi_percent: float


class PerVehicleROIResponse(BaseModel):
    """Per-vehicle ROI breakdown"""

    congestion_savings: CongestionSavingsResponse
    crash_savings: CrashSavingsResponse
    totals: TotalsResponse


class FleetMetricsResponse(BaseModel):
    """Fleet-level metrics"""

    annual_revenue_usd: float
    gross_profit_usd: float
    gross_margin_pct: float
    fleet_total_savings_usd: float
    value_unlocked_ratio: float


class FleetROIResponse(BaseModel):
    """Complete fleet ROI response"""

    fleet_size: int
    per_vehicle: PerVehicleROIResponse
    fleet_metrics: FleetMetricsResponse


class NationalCongestionImpact(BaseModel):
    """National congestion impact"""

    base_national_cost_usd: float
    reduction_pct: float
    savings_usd: float
    savings_billions: float


class NationalCrashImpact(BaseModel):
    """National crash impact"""

    base_national_cost_usd: float
    reduction_pct: float
    savings_usd: float
    savings_billions: float


class NationalTotals(BaseModel):
    """National totals"""

    total_savings_usd: float
    total_savings_billions: float
    platform_revenue_usd: float
    platform_revenue_billions: float
    value_created_ratio: float


class NationalImpactResponse(BaseModel):
    """National impact response"""

    adoption_pct: float
    vehicles_participating: int
    congestion: NationalCongestionImpact
    crash: NationalCrashImpact
    totals: NationalTotals


class ScenarioData(BaseModel):
    """Single scenario data"""

    description: str
    congestion_reduction_pct: float
    crash_reduction_pct: float
    per_vehicle_savings_usd: float
    per_vehicle_roi_multiple: float
    fleet_total_savings_usd: float
    platform_revenue_usd: float
    value_unlocked_ratio: float


class ScenarioComparisonResponse(BaseModel):
    """Scenario comparison response"""

    fleet_size: int
    location: str
    scenarios: dict


class SourceCitation(BaseModel):
    """Data source citation"""

    id: int
    name: str
    url: str
    data: str


class CustomerInfo(BaseModel):
    """Customer information"""

    type: str
    description: str
    focus_metric: str


class ParametersInfo(BaseModel):
    """Calculation parameters"""

    fleet_size: int
    location: str
    congestion_reduction_pct: float
    crash_reduction_pct: float


class PricingInfo(BaseModel):
    """Pricing information"""

    monthly_fee_usd: float
    annual_fee_usd: float
    gross_margin_pct: float


class OnePagerResponse(BaseModel):
    """Complete one-pager ROI response"""

    customer: CustomerInfo
    parameters: ParametersInfo
    roi: FleetROIResponse
    national_impact: NationalImpactResponse
    scenario_comparison: ScenarioComparisonResponse
    pricing: PricingInfo
    sources: list[SourceCitation]


class PresetResponse(BaseModel):
    """Preset configuration response"""

    customer_type: str
    congestion_reduction_pct: float
    crash_reduction_pct: float
    focus_metric: str
    description: str


class SourcesResponse(BaseModel):
    """All sources response"""

    sources: list[SourceCitation]
