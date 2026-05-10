"""Orchestration API endpoints"""

from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter()


class ReasoningChainRequest(BaseModel):
    session_id: str
    query: str
    context: dict[str, Any] | None = None


class MultiAgentRequest(BaseModel):
    session_id: str
    task: str
    tools: list[str] | None = []


@router.post("/chain")
async def orchestrate_chain(request: ReasoningChainRequest, req: Request):
    """Orchestrate a reasoning chain with LangChain + GPTRAM"""
    orchestrator = req.app.state.orchestrator

    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    result = await orchestrator.orchestrate_reasoning_chain(
        session_id=request.session_id,
        query=request.query,
        context=request.context,
    )

    return result


@router.post("/multi-agent")
async def orchestrate_multi_agent(request: MultiAgentRequest, req: Request):
    """Orchestrate multi-agent task execution"""
    orchestrator = req.app.state.orchestrator

    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    # For simplicity, using empty tools list
    result = await orchestrator.orchestrate_multi_agent(
        session_id=request.session_id,
        task=request.task,
        tools=[],
    )

    return result


@router.get("/memory/{session_id}")
async def get_memory_stats(session_id: str, req: Request):
    """Get memory statistics for a session"""
    memory = req.app.state.memory

    if not memory:
        raise HTTPException(status_code=503, detail="Memory service not initialized")

    stats = await memory.get_memory_stats(session_id)
    return stats
