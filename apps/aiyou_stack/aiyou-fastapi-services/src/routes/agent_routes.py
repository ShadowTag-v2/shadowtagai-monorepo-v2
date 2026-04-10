"""API routes for agent operations."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.schemas import (
    AgentExecuteRequest,
)
from ..services import AgentService

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("/")
async def list_agents(db: Session = Depends(get_db)) -> dict[str, Any]:
    """
    List all available agents.

    Returns:
        Dictionary of agents with their metadata
    """
    service = AgentService(db)
    return {"agents": service.list_agents()}


@router.get("/{agent_id}")
async def get_agent(agent_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    """
    Get agent details.

    Args:
        agent_id: The agent ID

    Returns:
        Agent metadata
    """
    service = AgentService(db)
    agent = service.get_agent(agent_id)

    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    return agent.get_metadata()


@router.post("/{agent_id}/execute")
async def execute_agent(
    agent_id: str,
    request: AgentExecuteRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    Execute an agent with a task.

    Args:
        agent_id: The agent ID
        request: The execution request

    Returns:
        Execution result
    """
    service = AgentService(db)

    try:
        result = await service.execute_agent(
            agent_id=agent_id,
            task=request.task,
            context=request.context,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")


@router.get("/{agent_id}/history")
async def get_agent_history(
    agent_id: str,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    Get execution history for an agent.

    Args:
        agent_id: The agent ID
        limit: Maximum number of executions to return
        offset: Number of executions to skip

    Returns:
        Execution history
    """
    service = AgentService(db)
    return service.get_execution_history(agent_id, limit, offset)


@router.get("/{agent_id}/tools")
async def get_agent_tools(agent_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    """
    Get available tools for an agent.

    Args:
        agent_id: The agent ID

    Returns:
        Dictionary of tools
    """
    service = AgentService(db)

    try:
        return service.get_agent_tools(agent_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/tools/{tool_name}/execute")
async def execute_tool(
    tool_name: str,
    args: dict[str, Any],
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    Execute a tool directly.

    Args:
        tool_name: The tool name
        args: The tool arguments

    Returns:
        Tool result
    """
    service = AgentService(db)

    try:
        return service.execute_tool(tool_name, args)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")
