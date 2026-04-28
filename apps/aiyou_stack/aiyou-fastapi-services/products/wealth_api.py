# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.wealth.model import WealthAccelerator, WealthPlan

app = FastAPI(
    title="Wealth Accelerator API",
    description="Automated business analysis to find revenue leaks.",
    version="1.0.0",
)


class AnalysisRequest(BaseModel):
    revenue_monthly: float
    cac: float
    ltv: float
    churn_rate: float
    conversion_rates: dict[str, float]


@app.post("/analyze", response_model=WealthPlan)
async def analyze_business(req: AnalysisRequest):
    """Analyze business metrics and return a structured Wealth Plan."""
    accelerator = WealthAccelerator()

    try:
        plan = accelerator.analyze_business(
            revenue_monthly=req.revenue_monthly,
            cac=req.cac,
            ltv=req.ltv,
            churn_rate=req.churn_rate,
            conversion_rates=req.conversion_rates,
        )
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/health")
async def health():
    return {"status": "ok", "service": "wealth-accelerator"}


# Usage: uvicorn products.wealth_api:app --reload
