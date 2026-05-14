# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Agent API endpoints for Pinkln multi-agent platform.

Premium tiers:
- Agent API: $10,000/month (PanelGPT, Code Crafter, Wealth Accelerator)
- Strategy Engine: $20,000/month (Full orchestrator + DTE evolution)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.base import AgentConfig
from app.agents.debate import DebateAgent, DebateOrchestrator, DebateResult
from app.wealth.model import WealthAccelerator, WealthPlan

router = APIRouter(prefix="/agents", tags=["agents"])


# Request/Response Models


class DebateRequest(BaseModel):
    """Request for multi-agent debate (PanelGPT)."""

    question: str = Field(..., description="Question to debate")
    num_agents: int = Field(3, ge=2, le=10, description="Number of agents (2-10)")
    max_rounds: int = Field(3, ge=1, le=10, description="Maximum debate rounds")
    consensus_threshold: float = Field(0.8, ge=0.0, le=1.0)


class WealthAnalysisRequest(BaseModel):
    """Request for wealth planning analysis."""

    revenue_monthly: float = Field(..., gt=0, description="Monthly recurring revenue")
    cac: float = Field(..., gt=0, description="Customer acquisition cost")
    ltv: float = Field(..., gt=0, description="Lifetime value")
    churn_rate: float = Field(..., ge=0, le=100, description="Monthly churn rate (%)")
    conversion_rates: dict[str, float] = Field(default_factory=dict, description="Conversion rates by funnel stage")


@router.post("/debate", response_model=DebateResult)
async def multi_agent_debate(request: DebateRequest) -> DebateResult:
    """
    PanelGPT: Multi-Agent Debate for collaborative reasoning.

    **Requires**: Agent API tier ($10,000/month)
    """
    try:
        personas = [
            "A critical thinker who challenges assumptions",
            "A creative problem solver who thinks outside the box",
            "A detail-oriented analyst who focuses on facts",
        ]

        agents = []
        for i in range(request.num_agents):
            config = AgentConfig(
                name=f"Agent-{i + 1}",
                description=f"Debate participant {i + 1}",
                model="gemini-2.0-flash-exp",
            )
            agents.append(DebateAgent(config, persona=personas[i % len(personas)]))

        orchestrator = DebateOrchestrator(
            agents=agents,
            max_rounds=request.max_rounds,
            consensus_threshold=request.consensus_threshold,
        )

        result = await orchestrator.run_debate(request.question)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Debate failed: {str(e)}")


@router.post("/wealth", response_model=WealthPlan)
async def wealth_accelerator(request: WealthAnalysisRequest) -> WealthPlan:
    """
    Wealth Accelerator: Revenue leak detection and optimization planning.

    **Requires**: Agent API tier ($10,000/month)
    """
    try:
        accelerator = WealthAccelerator()

        plan = accelerator.analyze_business(
            revenue_monthly=request.revenue_monthly,
            cac=request.cac,
            ltv=request.ltv,
            churn_rate=request.churn_rate,
            conversion_rates=request.conversion_rates or {},
        )

        return plan

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Wealth analysis failed: {str(e)}")
