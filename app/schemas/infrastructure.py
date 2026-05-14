# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Infrastructure layer data models for Cor.57 Unified Sky-Ground GPU Mesh
"""

from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class LayerType(str, Enum):
    """Infrastructure layer types"""

    ORBITAL = "orbital"
    TERRESTRIAL = "terrestrial"
    USER = "user"


class InfrastructureLayer(BaseModel):
    """Model for infrastructure layer configuration"""

    layer: LayerType
    platform: str = Field(..., description="Platform name (e.g., Starlink LEO satellites)")
    function: str = Field(..., description="Primary function of the layer")
    customer_value: str = Field(..., description="Value proposition for customers")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "layer": "orbital",
                "platform": "Starlink LEO satellites",
                "function": "Edge inference + global backhaul",
                "customer_value": "Low-latency, resilient global coverage",
            }
        }
    )


class TechnicalMetrics(BaseModel):
    """Technical performance metrics"""

    node_uptime: float = Field(..., ge=0, le=100, description="Node uptime percentage")
    compute_utilization: float = Field(..., ge=0, le=100, description="Average compute utilization percentage")
    latency_reduction_ms: int = Field(..., description="Latency reduction in milliseconds")
    energy_efficiency_improvement: float = Field(..., ge=0, le=100, description="Energy efficiency improvement percentage")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"node_uptime": 99.98, "compute_utilization": 70.0, "latency_reduction_ms": 65, "energy_efficiency_improvement": 25.0}
        }
    )


class CapexComponent(BaseModel):
    """Capital expenditure component"""

    component: str
    unit_cost: int = Field(..., description="Cost per unit in USD")
    volume: int = Field(..., description="Number of units by Year 5")
    total_capex: int = Field(..., description="Total CAPEX in USD")
    notes: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "component": "CoreWeave tower GPUs",
                "unit_cost": 15000,
                "volume": 100000,
                "total_capex": 1500000000,
                "notes": "1 GPU/node, shared w/ carriers",
            }
        }
    )


class InfrastructureDeployment(BaseModel):
    """Complete infrastructure deployment plan"""

    layers: list[InfrastructureLayer]
    technical_metrics: TechnicalMetrics
    capex_components: list[CapexComponent]
    total_capex: int = Field(..., description="Total CAPEX in USD")
    roi_period_years: float = Field(..., description="Return on investment period in years")
