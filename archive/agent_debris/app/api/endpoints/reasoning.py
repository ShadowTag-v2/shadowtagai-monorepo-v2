"""Reasoning API endpoints"""
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional

router = APIRouter()


class ReasoningRequest(BaseModel):
    session_id: str
    query: str
    context: dict[str, Any] | None = None
    mode: str = "hybrid"


class TrainAdapterRequest(BaseModel):
    expert_id: str
    training_data: list[dict[str, Any]]


@router.post("/reason")
async def execute_reasoning(request: ReasoningRequest, req: Request):
    """Execute core reasoning with BDH/RoT/MoE-CL"""
    reasoning = req.app.state.reasoning

    if not reasoning:
        raise HTTPException(status_code=503, detail="Reasoning engine not initialized")

    result = await reasoning.reason(
        session_id=request.session_id,
        query=request.query,
        context=request.context,
        mode=request.mode
    )

    return result


@router.post("/train-adapter")
async def train_adapter(request: TrainAdapterRequest, req: Request):
    """Train a MoE-CL adapter"""
    reasoning = req.app.state.reasoning

    if not reasoning:
        raise HTTPException(status_code=503, detail="Reasoning engine not initialized")

    result = await reasoning.train_adapter(
        expert_id=request.expert_id,
        training_data=request.training_data
    )

    return result
