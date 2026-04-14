from fastapi import APIRouter
from pydantic import BaseModel

# Path Hack
# Path Hack
# from src.governance.traffic_cop.routing_agent import RoutingAgent
# Corrected import after package refactor:
# from shadowtag_v4.proxies.routing_agent import RoutingAgent
# Legacy - Removed for Sovereign Kosmos
# from shadowtag_v4.agents.repair_loop import SovereignRepairLoop # POSTPONED


class SwarmController:
    def deploy_bravo(self, query):
        return f"Swarm Bravo deployed for: {query}"


api_router = APIRouter()
swarm = SwarmController()


class RepairRequest(BaseModel):
    error: str
    code: str
    file_path: str


@api_router.post("/agent/repair")
def trigger_repair_loop(r: RepairRequest):
    """Triggers the Sovereign Repair Loop (Fix/Review/Report)"""
    # loop = SovereignRepairLoop()
    # result = loop.execute_loop(r.error, r.code, r.file_path)
    return {"status": "POSTPONED", "details": "n-autoresearch/Kosmos/BioAgents Only Mode"}


class RequestModel(BaseModel):
    query: str


@api_router.post("/dispatch")
async def dispatch_task(r: RequestModel):
    # SOVEREIGN KOSMOS UNIFICATION (Gemini 2.5 Pro + Judge #6)
    from src.libs.shadowtag_v4.governance.judge_client import judge

    # 1. Consult the Judge (Governance Layer)
    verdict = await judge.evaluate(r.query)

    # 2. Return Verdict
    return {"action": "SOVEREIGN_JUDGMENT", "details": verdict, "judge": judge.base_url}


@api_router.post("/dispatch/recursive")
async def dispatch_recursive(r: RequestModel):
    """Triggers the Self-Correcting Recursive RLM Agent.
    """
    from libs.shadowtag_v4.agents.recursive_rlm import agent

    result = await agent.run_loop(r.query)
    return result
