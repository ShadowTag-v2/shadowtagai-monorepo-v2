"""Pydantic models for AWS Cost Optimizer API requests and responses.
"""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class GranularityType(StrEnum):
    """Cost data granularity options."""

    DAILY = "DAILY"
    MONTHLY = "MONTHLY"
    HOURLY = "HOURLY"


class OptimizationType(StrEnum):
    """Types of cost optimization recommendations."""

    RIGHT_SIZING = "RIGHT_SIZING"
    IDLE_RESOURCES = "IDLE_RESOURCES"
    SAVINGS_PLANS = "SAVINGS_PLANS"
    RESERVED_INSTANCES = "RESERVED_INSTANCES"
    AUTO_SCALING = "AUTO_SCALING"
    WASTE_ELIMINATION = "WASTE_ELIMINATION"


# Request Models
class CostAnalysisRequest(BaseModel):
    """Request model for cost analysis."""

    start_date: str | None = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: str | None = Field(None, description="End date (YYYY-MM-DD)")
    granularity: GranularityType = Field(GranularityType.DAILY, description="Data granularity")
    group_by: list[str] | None = Field(
        None, description="Dimension to group by (e.g., SERVICE, INSTANCE_TYPE)",
    )
    service_filter: list[str] | None = Field(None, description="Filter by specific AWS services")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "granularity": "DAILY",
                "group_by": ["SERVICE"],
                "service_filter": ["Amazon Elastic Compute Cloud - Compute"],
            },
        },
    )


class RecommendationRequest(BaseModel):
    """Request model for optimization recommendations."""

    optimization_types: list[OptimizationType] | None = Field(
        None, description="Types of optimizations to analyze",
    )
    min_savings_threshold: float | None = Field(
        100.0, description="Minimum monthly savings to include in recommendations",
    )
    include_forecast: bool = Field(False, description="Include cost forecast in analysis")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "optimization_types": ["RIGHT_SIZING", "IDLE_RESOURCES"],
                "min_savings_threshold": 100.0,
                "include_forecast": true,
            },
        },
    )


# Response Models
class CostDataPoint(BaseModel):
    """Individual cost data point."""

    date: str = Field(..., description="Date of the cost data")
    amount: float = Field(..., description="Cost amount in USD")
    unit: str = Field("USD", description="Currency unit")
    service: str | None = Field(None, description="AWS service name")


class CostSummary(BaseModel):
    """Summary of cost data."""

    total_cost: float = Field(..., description="Total cost in USD")
    average_daily_cost: float = Field(..., description="Average daily cost")
    period_start: str = Field(..., description="Analysis period start date")
    period_end: str = Field(..., description="Analysis period end date")
    top_services: list[dict[str, Any]] = Field(..., description="Top cost-driving services")


class CostAnalysisResponse(BaseModel):
    """Response model for cost analysis."""

    summary: CostSummary
    data_points: list[CostDataPoint]
    granularity: str
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "summary": {
                    "total_cost": 5432.10,
                    "average_daily_cost": 180.74,
                    "period_start": "2024-01-01",
                    "period_end": "2024-01-31",
                    "top_services": [
                        {"service": "Amazon EC2", "cost": 3200.50},
                        {"service": "Amazon S3", "cost": 1500.25},
                    ],
                },
                "data_points": [{"date": "2024-01-01", "amount": 175.50, "unit": "USD"}],
                "granularity": "DAILY",
                "analyzed_at": "2024-01-31T10:00:00Z",
            },
        },
    )


class OptimizationRecommendation(BaseModel):
    """Individual optimization recommendation."""

    recommendation_type: OptimizationType
    resource_id: str | None = Field(None, description="AWS resource ID")
    resource_type: str | None = Field(None, description="Resource type")
    current_cost: float = Field(..., description="Current monthly cost")
    estimated_savings: float = Field(..., description="Estimated monthly savings")
    savings_percentage: float = Field(..., description="Savings as percentage")
    description: str = Field(..., description="Recommendation description")
    action_items: list[str] = Field(..., description="Steps to implement recommendation")
    priority: str = Field(..., description="Priority level (HIGH, MEDIUM, LOW)")


class RecommendationsResponse(BaseModel):
    """Response model for optimization recommendations."""

    total_estimated_savings: float = Field(..., description="Total potential monthly savings")
    recommendations_count: int = Field(..., description="Number of recommendations")
    recommendations: list[OptimizationRecommendation]
    forecast: dict[str, Any] | None = Field(None, description="Cost forecast if requested")
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_estimated_savings": 2500.00,
                "recommendations_count": 5,
                "recommendations": [
                    {
                        "recommendation_type": "RIGHT_SIZING",
                        "resource_id": "i-1234567890abcdef0",
                        "resource_type": "EC2 Instance",
                        "current_cost": 150.00,
                        "estimated_savings": 75.00,
                        "savings_percentage": 50.0,
                        "description": "Downsize from t3.xlarge to t3.large",
                        "action_items": [
                            "Review instance metrics",
                            "Create AMI backup",
                            "Change instance type",
                        ],
                        "priority": "HIGH",
                    },
                ],
                "generated_at": "2024-01-31T10:00:00Z",
            },
        },
    )


class WasteAnalysisResponse(BaseModel):
    """Response model for waste analysis."""

    total_waste_cost: float = Field(..., description="Total monthly waste cost")
    waste_categories: dict[str, float] = Field(..., description="Waste breakdown by category")
    idle_resources: list[dict[str, Any]] = Field(..., description="List of idle resources")
    unused_resources: list[dict[str, Any]] = Field(..., description="List of unused resources")
    optimization_potential: float = Field(..., description="Total optimization potential")


class HealthCheckResponse(BaseModel):
    """Health check response."""

    status: str = Field("healthy", description="Service status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(..., description="API version")
    aws_connection: bool = Field(..., description="AWS connection status")


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    detail: str | None = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
