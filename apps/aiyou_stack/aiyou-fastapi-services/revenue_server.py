"""
Standalone Revenue Engine Server
Minimal FastAPI server for whiteboard revenue simulation
"""

from fastapi import FastAPI
from pydantic import BaseModel

from agents.legal_whiteboard import whiteboard

app = FastAPI(title="ShadowTagAI Revenue Engine")


class RevenueRequest(BaseModel):
    amount_usd: float
    source: str
    agent_id: str = "agent_001"


@app.post("/api/v1/whiteboard/revenue")
async def record_revenue(req: RevenueRequest):
    """Record revenue and trigger level progression"""
    whiteboard.record_revenue(req.amount_usd, req.source, req.agent_id)

    return {
        "success": True,
        "total_revenue_usd": whiteboard.state["total_revenue_usd"],
        "current_level": whiteboard.state["current_level"],
        "agent_revenue": whiteboard.state["agents"]
        .get(req.agent_id, {})
        .get("revenue_generated", 0),
    }


@app.get("/api/v1/whiteboard/status")
async def get_status():
    """Get current whiteboard status"""
    return whiteboard.get_status()


@app.get("/health")
async def health():
    return {"status": "healthy"}
