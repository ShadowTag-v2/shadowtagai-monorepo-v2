from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/unified", tags=["Unified Ecosystem"])


class AerospaceDeploymentResponse(BaseModel):
    """Aerospace deployment economics and ROI."""

    deployment_name: str
    total_investment_usd: float
    monthly_revenue_usd: float
    annual_revenue_usd: float
    roi_months: float
    roi_percent: float
    valuation_usd: float
    base_gpu_cost_monthly: float
    optimized_gpu_cost_monthly: float
    gpu_savings_monthly: float
    gpu_savings_percent: float
