from fastapi import APIRouter, HTTPException

from app.orchestrator import app_orchestrator
from app.schemas import TaskRequest

router = APIRouter()


@router.post("/run", response_model=dict)
async def run_orchestrator(task: TaskRequest):
    """Executes the Antigravity Agent Swarm (Courtroom Flow)."""
    try:
        # Initial state
        initial_state = {
            "task": task,
            "messages": [],
            "risk_level": "GREEN",  # placeholder, router will update
            "policy_issues": [],
        }

        # Invoke LangGraph
        # We use .invoke similar to a function call for now
        final_state = app_orchestrator.invoke(initial_state)

        return {
            "final_output": final_state.get("final_output"),
            "risk_level": final_state.get("risk_level"),
            "cost_usd": final_state.get("cost_usd", 0.0),
            "trace_id": "simulated-trace-id",  # TODO: integrate real tracing
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
