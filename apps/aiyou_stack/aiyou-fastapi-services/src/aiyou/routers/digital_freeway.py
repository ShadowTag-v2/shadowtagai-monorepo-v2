# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Digital Freeway ROI Calculator API Routes
=========================================

FastAPI router for traffic congestion and crash cost savings ROI calculations.

Endpoints:
- POST /calculate - Calculate ROI based on parameters
- GET /presets/{customer_type} - Get preset values for Tesla/Waymo/DOT
- POST /scenarios - Compare conservative/mid/aggressive scenarios
- POST /national-impact - Calculate national-level impact
- GET /sources - Get all data sources with citations
"""

from fastapi import APIRouter, HTTPException

from ..models.digital_freeway import (
    CustomerType,
    FleetROIResponse,
    NationalImpactRequest,
    NationalImpactResponse,
    OnePagerResponse,
    PresetResponse,
    ROICalculationRequest,
    ScenarioComparisonRequest,
    ScenarioComparisonResponse,
    SourcesResponse,
)
from ..services.financial.digital_freeway_roi import (
    CustomerType as ServiceCustomerType,
)
from ..services.financial.digital_freeway_roi import (
    DigitalFreewayROICalculator,
)

router = APIRouter(
    prefix="/api/v1/digital-freeway",
    tags=["Digital Freeway ROI"],
    responses={404: {"description": "Not found"}},
)

# Initialize calculator
calculator = DigitalFreewayROICalculator()


@router.post(
    "/calculate",
    response_model=OnePagerResponse,
    summary="Calculate Digital Freeway ROI",
    description="""
    Calculate comprehensive ROI for Digital Freeway traffic coordination platform.

    Supports three customer types with different default assumptions:
    - **Tesla**: OEM vehicle manufacturer (20% congestion, 5% crash reduction)
    - **Waymo**: Autonomous fleet operator (25% congestion, 7% crash reduction)
    - **DOT**: Government transportation dept (15% congestion, 3% crash reduction)

    Returns per-vehicle savings, fleet economics, national impact, and scenario comparisons.
    """,
)
async def calculate_roi(request: ROICalculationRequest) -> OnePagerResponse:
    """Calculate ROI based on input parameters"""
    try:
        # Map Pydantic enum to service enum
        service_customer_type = ServiceCustomerType(request.customer_type.value)

        result = calculator.generate_one_pager(
            customer_type=service_customer_type,
            fleet_size=request.fleet_size,
            congestion_reduction_pct=request.congestion_reduction_pct,
            crash_reduction_pct=request.crash_reduction_pct,
            location=request.location.value,
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get(
    "/presets/{customer_type}",
    response_model=PresetResponse,
    summary="Get Customer Type Presets",
    description="""
    Get default reduction percentages and focus metrics for a customer type.

    - **tesla**: Driver ROI focus, 20% congestion, 5% crash
    - **waymo**: Fleet economics focus, 25% congestion, 7% crash
    - **dot**: National savings focus, 15% congestion, 3% crash
    """,
)
async def get_preset(customer_type: CustomerType) -> PresetResponse:
    """Get preset configuration for a customer type"""
    try:
        service_customer_type = ServiceCustomerType(customer_type.value)
        preset = calculator.get_preset(service_customer_type)

        return PresetResponse(
            customer_type=customer_type.value,
            congestion_reduction_pct=preset["congestion_reduction_pct"],
            crash_reduction_pct=preset["crash_reduction_pct"],
            focus_metric=preset["focus_metric"],
            description=preset["description"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post(
    "/scenarios",
    response_model=ScenarioComparisonResponse,
    summary="Compare ROI Scenarios",
    description="""
    Compare conservative, mid, and aggressive ROI scenarios.

    - **Conservative**: 15% congestion + 2% crash reduction
    - **Mid**: 20% congestion + 5% crash reduction
    - **Aggressive**: 30% congestion + 10% crash reduction
    """,
)
async def compare_scenarios(request: ScenarioComparisonRequest) -> ScenarioComparisonResponse:
    """Compare multiple scenarios"""
    try:
        result = calculator.calculate_scenario_comparison(
            fleet_size=request.fleet_size,
            location=request.location.value,
        )

        return ScenarioComparisonResponse(
            fleet_size=result["fleet_size"],
            location=result["location"],
            scenarios=result["scenarios"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post(
    "/national-impact",
    response_model=NationalImpactResponse,
    summary="Calculate National Impact",
    description="""
    Calculate national-level savings impact for DOT/government stakeholders.

    Based on:
    - Total U.S. congestion cost: $74B/year (INRIX 2024)
    - Total crash economic cost: $340B/year (NHTSA 2019)
    - U.S. registered vehicles: 286M
    """,
)
async def calculate_national_impact(request: NationalImpactRequest) -> NationalImpactResponse:
    """Calculate national impact"""
    try:
        result = calculator.calculate_national_impact(
            congestion_reduction_pct=request.congestion_reduction_pct,
            crash_reduction_pct=request.crash_reduction_pct,
            adoption_pct=request.adoption_pct,
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get(
    "/fleet-roi",
    response_model=FleetROIResponse,
    summary="Quick Fleet ROI Calculation",
    description="Calculate fleet ROI with query parameters for quick lookups",
)
async def quick_fleet_roi(
    fleet_size: int = 1_000_000,
    congestion_pct: float = 0.20,
    crash_pct: float = 0.05,
    location: str = "us_avg",
) -> FleetROIResponse:
    """Quick fleet ROI calculation via query params"""
    try:
        result = calculator.calculate_fleet_roi(
            fleet_size=fleet_size,
            congestion_reduction_pct=congestion_pct,
            crash_reduction_pct=crash_pct,
            location=location,
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get(
    "/sources",
    response_model=SourcesResponse,
    summary="Get Data Sources",
    description="""
    Get all data sources used in ROI calculations with proper citations.

    Sources include:
    1. INRIX 2024 Global Traffic Scorecard (congestion costs)
    2. NHTSA Economic & Societal Impact Report 2019 (crash costs)
    3. Tesla Q1 2024 Autopilot Safety Data (baseline crash rates)
    """,
)
async def get_sources() -> SourcesResponse:
    """Get all data sources with citations"""
    return SourcesResponse(sources=calculator.get_all_sources())


@router.get(
    "/health",
    summary="Health Check",
    description="Check if the Digital Freeway ROI service is operational",
)
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "digital-freeway-roi", "version": "1.0.0"}
