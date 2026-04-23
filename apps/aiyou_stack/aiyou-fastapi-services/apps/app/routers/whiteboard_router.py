from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agents.legal_whiteboard import whiteboard

router = APIRouter(prefix="/whiteboard", tags=["whiteboard"])


class RevenueEvent(BaseModel):
    amount_usd: float
    source: str
    agent_id: str | None = None


@router.post("/revenue")
async def record_revenue(event: RevenueEvent):
    """Record a revenue event and update whiteboard state."""
    try:
        whiteboard.record_revenue(event.amount_usd, event.source, event.agent_id)
        return {
            "status": "success",
            "new_total": whiteboard.state["total_revenue_usd"],
            "level": whiteboard.state["current_level"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/status")
async def get_status():
    """Get current whiteboard status."""
    return whiteboard.get_status()
