from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/unified", tags=["Unified Ecosystem"])


class ValuationRequest(BaseModel):
    """Request for enterprise valuation calculation."""

    aerospace_arr_usd: float = Field(default=440000000)
    pinkln_arr_usd: float = Field(default=10200000000)
    layer0_savings_annual_usd: float = Field(default=10100000000)
    monte_carlo_iterations: int = Field(default=10000, ge=100, le=100000)
    scenario: str = Field(default="base", regex="^(bear|base|bull)$")
