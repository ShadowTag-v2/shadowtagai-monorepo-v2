
from fastapi import APIRouter

# Import Swarm
# Assuming libs is in path (it is added in main.py)
from libs.arsenal.autoresearch.swarm import swarm
from pydantic import BaseModel

router = APIRouter()

class TaskRequest(BaseModel):
    description: str

@router.get("/state")
async def get_swarm_state():
    """Returns the current state of the swarm for the UI."""
    return swarm.get_swarm_state()

@router.post("/task")
async def submit_task(task: TaskRequest):
    """Submits a task to the swarm."""
    return swarm.dispatch_task(task.description)

class SpawnRequest(BaseModel):
    type: str
    name: str

@router.post("/spawn")
async def spawn_agent(req: SpawnRequest):
    """Dynamically spawns a new agent."""
    agent_id = swarm.spawn_agent(req.type, req.name)
    return {"id": agent_id, "status": "SPAWNED", "name": req.name}
