"""Infrastructure models and schemas
"""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class CloudProvider(StrEnum):
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"


class WorkloadType(StrEnum):
    WEB_APP = "web_app"
    API = "api"
    MICROSERVICES = "microservices"
    DATA_PIPELINE = "data_pipeline"
    ML_TRAINING = "ml_training"
    BATCH_PROCESSING = "batch_processing"


class InfrastructureDesignRequest(BaseModel):
    """Request model for infrastructure design"""

    name: str = Field(..., description="Project or application name")
    cloud_provider: CloudProvider = Field(..., description="Target cloud provider")
    workload_type: WorkloadType = Field(..., description="Type of workload")
    expected_traffic: int = Field(..., description="Expected requests per second", gt=0)
    high_availability: bool = Field(default=True, description="Enable HA configuration")
    budget_limit: float | None = Field(None, description="Monthly budget limit in USD")
    requirements: dict[str, Any] = Field(
        default_factory=dict, description="Additional requirements",
    )


class InfrastructureComponent(BaseModel):
    """Infrastructure component"""

    name: str
    type: str
    provider_service: str
    configuration: dict[str, Any]
    estimated_monthly_cost: float


class InfrastructureDesignResponse(BaseModel):
    """Response model for infrastructure design"""

    design_id: str
    name: str
    cloud_provider: CloudProvider
    components: list[InfrastructureComponent]
    architecture_diagram: str | None = None
    recommendations: list[str]
    estimated_monthly_cost: float
    scalability_score: float = Field(..., ge=0, le=10)
    cost_efficiency_score: float = Field(..., ge=0, le=10)


class CostEstimateRequest(BaseModel):
    """Request model for cost estimation"""

    cloud_provider: CloudProvider
    components: list[dict[str, Any]]
    region: str = "us-east-1"
    hours_per_month: int = Field(default=730, description="Hours of operation per month")


class CostBreakdown(BaseModel):
    """Cost breakdown by component"""

    component: str
    monthly_cost: float
    cost_drivers: list[str]


class CostEstimateResponse(BaseModel):
    """Response model for cost estimation"""

    total_monthly_cost: float
    breakdown: list[CostBreakdown]
    optimization_opportunities: list[str]
    potential_savings: float


class ScalingRecommendation(BaseModel):
    """Scaling recommendations"""

    auto_scaling_enabled: bool
    min_instances: int
    max_instances: int
    target_cpu_utilization: int
    scale_up_cooldown: int
    scale_down_cooldown: int
    recommendations: list[str]
