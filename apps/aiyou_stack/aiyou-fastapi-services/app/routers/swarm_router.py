# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Swarm API Router - REST endpoints for LiveSwarm orchestration.

Endpoints:
- GET /swarm/status - Swarm status
- GET /swarm/agents - List agents
- POST /swarm/spawn - Spawn new agent
- POST /swarm/task - Execute task
- POST /swarm/revenue - Record revenue
- GET /swarm/tree - Dynasty tree
"""

# Import swarm
import sys
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shadowtagai.agents.live_swarm import get_swarm

router = APIRouter(prefix="/swarm", tags=["swarm"])


class SpawnRequest(BaseModel):
    name: str
    parent_id: str = "OVERLORD_PRIME"
    specialization: str = "general"


class TaskRequest(BaseModel):
    type: str = "general"
    complexity: float = 0.5
    agent_id: str | None = None


class RevenueRequest(BaseModel):
    agent_id: str
    amount_usd: float
    simulated: bool = False


@router.get("/status")
async def get_swarm_status() -> dict[str, Any]:
    """Get current swarm status."""
    swarm = get_swarm()
    return swarm.get_swarm_status()


@router.get("/agents")
async def list_agents() -> list[dict[str, Any]]:
    """List all agents in swarm."""
    swarm = get_swarm()
    return swarm.list_agents()


@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str) -> dict[str, Any]:
    """Get specific agent details."""
    swarm = get_swarm()
    agent = swarm.agents.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    return agent.to_dict()


@router.post("/spawn")
async def spawn_agent(request: SpawnRequest) -> dict[str, Any]:
    """Spawn a new agent from a parent."""
    swarm = get_swarm()
    agent = swarm.spawn_agent(
        parent_id=request.parent_id,
        name=request.name,
        specialization=request.specialization,
    )
    if not agent:
        raise HTTPException(
            status_code=400,
            detail="Failed to spawn agent. Parent may not have SPAWNER level.",
        )
    return {"status": "spawned", "agent": agent.to_dict()}


@router.post("/task")
async def execute_task(request: TaskRequest) -> dict[str, Any]:
    """Execute a task in the swarm."""
    swarm = get_swarm()
    result = await swarm.execute_task(
        task={"type": request.type, "complexity": request.complexity},
        agent_id=request.agent_id,
    )
    return result


@router.post("/revenue")
async def record_revenue(request: RevenueRequest) -> dict[str, Any]:
    """Record revenue for an agent with DNA share distribution."""
    swarm = get_swarm()
    distribution = swarm.record_revenue(
        agent_id=request.agent_id,
        amount_usd=request.amount_usd,
        simulated=request.simulated,
    )
    if "error" in distribution:
        raise HTTPException(status_code=404, detail=distribution["error"])
    return {"status": "recorded", "amount_usd": request.amount_usd, "distribution": distribution}


@router.get("/tree")
async def get_dynasty_tree() -> dict[str, Any]:
    """Get the dynasty tree of all agents."""
    swarm = get_swarm()
    return swarm.get_dynasty_tree()


@router.post("/activate")
async def activate_swarm() -> dict[str, Any]:
    """Activate the swarm and spawn initial agents.

    This bootstraps the swarm with core specialization agents.
    """
    swarm = get_swarm()

    # Initial agent specializations
    specializations = [
        ("Compliance_V1", "compliance"),
        ("Revenue_V1", "revenue"),
        ("CodeReview_V1", "code_review"),
        ("Research_V1", "research"),
        ("Orchestrator_V1", "orchestration"),
    ]

    spawned = []
    for name, spec in specializations:
        # Check if already exists
        exists = any(a.name == name for a in swarm.agents.values())
        if not exists:
            agent = swarm.spawn_agent(parent_id="OVERLORD_PRIME", name=name, specialization=spec)
            if agent:
                spawned.append(agent.to_dict())

    return {
        "status": "activated",
        "spawned_count": len(spawned),
        "agents": spawned,
        "total_agents": len(swarm.agents),
    }


@router.get("/health")
async def swarm_health() -> dict[str, Any]:
    """Health check for swarm."""
    swarm = get_swarm()
    status = swarm.get_swarm_status()

    return {
        "status": "healthy",
        "agents": status["swarm"]["total_agents"],
        "overlord_level": status["overlord"]["level"],
        "total_revenue": status["swarm"]["total_revenue_usd"],
    }
