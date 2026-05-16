# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Financial projection models for Cor.57 Unified Sky-Ground GPU Mesh
"""

from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class RevenueSource(str, Enum):
  """Revenue source categories"""

  STARLINK_INFERENCE = "starlink_inference"
  CELLULAR_AI = "cellular_ai"
  DEFENSE_PNT = "defense_pnt"
  ENTERPRISE_COMPUTE = "enterprise_compute"
  DATA_RESELL = "data_resell"


class RevenueStream(BaseModel):
  """Revenue stream model"""

  source: RevenueSource
  description: str
  annual_revenue: int = Field(..., description="Annual revenue in USD")
  margin_percentage: float = Field(
    ..., ge=0, le=100, description="Profit margin percentage"
  )
  notes: str

  model_config = ConfigDict(
    json_schema_extra={
      "example": {
        "source": "starlink_inference",
        "description": "Starlink inference traffic",
        "annual_revenue": 2100000000,
        "margin_percentage": 85.0,
        "notes": "AI overlay + data compression",
      }
    }
  )


class FinancialProjection(BaseModel):
  """Financial projection for a specific year"""

  year: int = Field(..., ge=2025, le=2035, description="Projection year")
  arr: int = Field(..., description="Annual Recurring Revenue in USD")
  ebitda: int = Field(..., description="EBITDA in USD")
  ebitda_margin: float = Field(
    ..., ge=0, le=100, description="EBITDA margin percentage"
  )
  free_cash_flow: int = Field(..., description="Free cash flow in USD")
  revenue_streams: list[RevenueStream]

  model_config = ConfigDict(
    json_schema_extra={
      "example": {
        "year": 2030,
        "arr": 10000000000,
        "ebitda": 8400000000,
        "ebitda_margin": 84.0,
        "free_cash_flow": 7000000000,
        "revenue_streams": [],
      }
    }
  )


class ValuationScenario(str, Enum):
  """Valuation scenario types"""

  IPO_GLOBAL_AI = "ipo_global_ai"
  PRIVATE_RETENTION = "private_retention"
  STRATEGIC_SALE = "strategic_sale"
  HYBRID = "hybrid"


class Valuation(BaseModel):
  """Valuation model"""

  scenario: ValuationScenario
  rationale: str
  estimated_value: int = Field(..., description="Estimated value in USD")
  control_percentage: float | None = Field(
    None, ge=0, le=100, description="Control retained percentage"
  )
  tax_exposure_percentage: float | None = Field(
    None, ge=0, le=100, description="Effective tax rate percentage"
  )
  liquidity_level: str = Field(..., description="Liquidity level (Low, Medium, High)")

  model_config = ConfigDict(
    json_schema_extra={
      "example": {
        "scenario": "hybrid",
        "rationale": "Private Infra ($160B) + Public Digital ($150B)",
        "estimated_value": 310000000000,
        "control_percentage": 80.0,
        "tax_exposure_percentage": 8.0,
        "liquidity_level": "High",
      }
    }
  )


class CustomerSegment(BaseModel):
  """Customer segment financial model"""

  customer_name: str
  annual_spend: int = Field(..., description="Annual spend in USD")
  description: str
  contract_type: str = Field(default="IaaS", description="Contract type")

  model_config = ConfigDict(
    json_schema_extra={
      "example": {
        "customer_name": "SpaceX / Starlink",
        "annual_spend": 400000000,
        "description": "Starlink + AiYou hybrid AI routing",
        "contract_type": "IaaS",
      }
    }
  )


class ConsolidatedFinancials(BaseModel):
  """Consolidated financial overview"""

  total_arr: int = Field(..., description="Total ARR in USD")
  total_ebitda: int = Field(..., description="Total EBITDA in USD")
  blended_margin: float = Field(
    ..., ge=0, le=100, description="Blended margin percentage"
  )
  primary_valuation: Valuation
  alternative_valuations: list[Valuation]
  customer_segments: list[CustomerSegment]
  total_customer_spend: int = Field(..., description="Total customer spend in USD")


class OperatingModel(BaseModel):
  """Operating model metrics"""

  annual_opex: int = Field(..., description="Annual OPEX in USD")
  average_uptime: float = Field(
    ..., ge=0, le=100, description="Average uptime percentage"
  )
  compute_utilization: float = Field(
    ..., ge=0, le=100, description="Compute utilization percentage"
  )
  roi_period_years: float = Field(..., description="ROI period in years")
  break_even_milestone: str = Field(..., description="Break-even milestone description")

  model_config = ConfigDict(
    json_schema_extra={
      "example": {
        "annual_opex": 400000000,
        "average_uptime": 99.98,
        "compute_utilization": 70.0,
        "roi_period_years": 2.4,
        "break_even_milestone": "Mid-Year 3",
      }
    }
  )
