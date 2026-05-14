# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Strategic planning models for Cor.57 Unified Sky-Ground GPU Mesh
"""

from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class MilestoneStatus(str, Enum):
    """Milestone status"""

    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELAYED = "delayed"


class Milestone(BaseModel):
    """Strategic milestone"""

    date: str = Field(..., description="Target date (e.g., Q4 2025)")
    description: str
    valuation_impact: int = Field(..., description="Valuation impact in USD")
    status: MilestoneStatus = Field(default=MilestoneStatus.PLANNED)

    model_config = ConfigDict(json_schema_extra={
            "example": {
                "date": "Q4 2025",
                "description": "Pilot live (3 CoreWeave–Starlink sites)",
                "valuation_impact": 500000000,
                "status": "planned",
            }
        })
class StrategicEffect(BaseModel):
    """Strategic effect measurement"""

    category: str = Field(..., description="Effect category (e.g., 'Efficiency', 'Economic Leverage')")
    metric: str = Field(..., description="Metric name")
    improvement: str = Field(..., description="Improvement description")
    quantified_value: str | None = Field(None, description="Quantified value if applicable")

    model_config = ConfigDict(json_schema_extra={
            "example": {"category": "Efficiency", "metric": "Compute cost", "improvement": "45–55% reduction", "quantified_value": "↓ 45–55%"}
        })
class LegalPositioning(BaseModel):
    """Legal and contractual positioning"""

    role: str = Field(..., description="AiYou's legal role")
    description: str
    revenue_model: str | None = Field(None, description="Revenue model if applicable")
    ownership_rights: list[str] = Field(default_factory=list, description="Ownership rights")

    model_config = ConfigDict(json_schema_extra={
            "example": {
                "role": "Integrator of Record",
                "description": "Bridge contract between SpaceX, CoreWeave, and telecoms",
                "revenue_model": "10–15% brokerage on all compute/bandwidth flows",
                "ownership_rights": ["Orchestration IP", "Telemetry data", "Software platform"],
            }
        })
class CompetitiveAdvantage(BaseModel):
    """Competitive advantage description"""

    advantage: str
    description: str
    barrier_to_entry: str = Field(..., description="Barrier to entry level (Low, Medium, High)")
    sustainability: str = Field(..., description="Sustainability assessment")

    model_config = ConfigDict(json_schema_extra={
            "example": {
                "advantage": "Dual-Use Critical Infrastructure",
                "description": "Only entity bridging airspace and earth with verified AI",
                "barrier_to_entry": "High",
                "sustainability": "10+ years with proper execution",
            }
        })
class PartnershipModel(BaseModel):
    """Partnership model"""

    partner_name: str
    partner_type: str = Field(..., description="Type of partner (Provider, Customer, Both)")
    relationship: str = Field(..., description="Relationship description")
    revenue_sharing: str | None = Field(None, description="Revenue sharing model if applicable")
    strategic_value: str = Field(..., description="Strategic value description")

    model_config = ConfigDict(json_schema_extra={
            "example": {
                "partner_name": "SpaceX",
                "partner_type": "Both",
                "relationship": "Revenue-sharing partner providing Starlink infrastructure",
                "revenue_sharing": "Hybrid compute + bandwidth split",
                "strategic_value": "Critical for orbital layer; global coverage enabler",
            }
        })
class StrategicPlan(BaseModel):
    """Complete strategic plan overview"""

    document_id: str = Field(default="COR-57")
    version: str = Field(default="1.0")
    title: str = Field(default="Unified Sky–Ground GPU Mesh")
    executive_summary: str
    milestones: list[Milestone]
    strategic_effects: list[StrategicEffect]
    legal_positioning: list[LegalPositioning]
    competitive_advantages: list[CompetitiveAdvantage]
    key_partnerships: list[PartnershipModel]


class GlobalDeploymentMetrics(BaseModel):
    """Global deployment metrics"""

    total_towers: int = Field(..., description="Total number of cell towers")
    total_satellites: int = Field(..., description="Total number of satellites")
    total_vehicles: int = Field(..., description="Total number of connected vehicles")
    geographic_coverage: str = Field(..., description="Geographic coverage description")
    total_compute_nodes: int = Field(..., description="Total compute nodes")

    model_config = ConfigDict(json_schema_extra={
            "example": {
                "total_towers": 100000,
                "total_satellites": 3000,
                "total_vehicles": 3000000,
                "geographic_coverage": "Global - 95% populated areas",
                "total_compute_nodes": 3103000,
            }
        })
class ConsolidatedSummary(BaseModel):
    """Consolidated summary of Cor.57"""

    total_arr: int = Field(..., description="Total ARR in USD")
    ebitda_margin: float = Field(..., ge=0, le=100, description="EBITDA margin percentage")
    deployment_metrics: GlobalDeploymentMetrics
    valuation_private: int = Field(..., description="Private valuation in USD")
    annual_family_yield: int = Field(..., description="Annual family yield in USD")
    strategic_control: str = Field(..., description="Strategic control description")

    model_config = ConfigDict(json_schema_extra={
            "example": {
                "total_arr": 10000000000,
                "ebitda_margin": 84.0,
                "deployment_metrics": {
                    "total_towers": 100000,
                    "total_satellites": 3000,
                    "total_vehicles": 3000000,
                    "geographic_coverage": "Global",
                    "total_compute_nodes": 3103000,
                },
                "valuation_private": 160000000000,
                "annual_family_yield": 7000000000,
                "strategic_control": "100% infrastructure + IP ownership",
            }
        })