from fastapi import APIRouter
from pydantic import BaseModel
import sys, os

# Path Hack
sys.path.append(os.path.abspath("../../../libs"))
from ShadowTag-v2.proxies.routing_agent import router as agent_router
# Check if arsenal/autoresearch exists, else mock it to prevent crash
try:
    from arsenal.autoresearch.swarm import SwarmController
    swarm = SwarmController()
except ImportError:
    class MockSwarm:
        def deploy_bravo(self, query): return "Mock Deployment: " + query
    swarm = MockSwarm()

api_router = APIRouter()

class RequestModel(BaseModel):
    query: str

@api_router.post("/dispatch")
def dispatch_task(r: RequestModel):
    # 1. Ask the Router (Is this for the n-autoresearch/Kosmos/BioAgents?)
    decision = agent_router.dispatch(r.query)
    
    # 2. Execute
    if decision["route"] == "SWARM":
        # Launch the Swarm
        result = swarm.deploy_bravo(r.query)
        return {"action": "SWARM_DEPLOYED", "details": result}
    else:
        # Just return the advice (Mocking Local execution)
        return {"action": "LOCAL_EXECUTION", "details": "Task is simple. Suggest doing it in-context."}
