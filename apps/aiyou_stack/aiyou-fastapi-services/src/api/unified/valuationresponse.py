from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(prefix="/api/v1/unified", tags=["Unified Ecosystem"])


class ValuationResponse(BaseModel):
    """Enterprise valuation with Monte Carlo simulation."""

    total_arr_usd: float
    enterprise_value_usd: float
    founder_equity_value_usd: float
    ev_p10: float
    ev_p50: float
    ev_p90: float
    ev_mean: float
    ev_std_dev: float
    probability_100b: float
    probability_500b: float
    probability_715b: float
