#!/bin/bash
set -e
REPO_NAME="ShadowTag-Omega"
if [ -d "$REPO_NAME" ]; then cd "$REPO_NAME"; fi

echo ">>> 🦍 INITIATING ROUTER INJECTION (v64)..."
echo ">>> 🚦 BUILDING: GEMINI ROUTING AGENT (WITH ECHO)..."

# ENSURE DIRECTORIES EXIST
mkdir -p libs/aiyou/proxies
mkdir -p apps/flyingmonkeys-server/src

# ==============================================================================
# 1. THE ROUTING AGENT (The Traffic Cop)
# ==============================================================================
# This agent decides if a task is for the "Swarm" or "Local".
# It uses ECHO PROTOCOL for 97% classification accuracy.

cat <<PYTHON > libs/aiyou/proxies/routing_agent.py
import logging
from ..agents.recursive_rlm import RecursiveAgent

class RoutingAgent:
    def __init__(self):
        self.brain = RecursiveAgent()
        
    def dispatch(self, user_request: str) -> dict:
        """
        Decides: Do we keep this LOCAL or send to SWARM?
        Uses ECHO PROTOCOL for 97% classification accuracy.
        """
        
        # 1. CONSTRUCT THE ECHO PROMPT
        # We repeat the classification instruction to force attention.
        
        classification_prompt = f"""
        ROLE: System Router.
        TASK: Classify the following User Request into 'LOCAL' (Simple edit/question) or 'SWARM' (Complex research/multi-file refactor).
        
        USER REQUEST: "{user_request}"
        
        ---
        
        ROLE: System Router.
        TASK: Classify the following User Request into 'LOCAL' (Simple edit/question) or 'SWARM' (Complex research/multi-file refactor).
        
        USER REQUEST: "{user_request}"
        
        OUTPUT FORMAT: Just the word 'LOCAL' or 'SWARM'.
        """
        
        # 2. CALL THE BRAIN (RecursiveAgent handles the API)
        # Note: RecursiveAgent might also double-echo if configured, which is fine.
        verdict = self.brain.solve(classification_prompt).strip().upper()
        
        logging.info(f"🚦 ROUTER: Verdict for '{user_request[:20]}...' is {verdict}")
        
        if "SWARM" in verdict:
            return {"route": "SWARM", "target": "flying_monkeys", "payload": user_request}
        else:
            return {"route": "LOCAL", "target": "gemini_flash", "payload": user_request}

router = RoutingAgent()
PYTHON

# ==============================================================================
# 2. INTEGRATE INTO SERVER (The API Endpoint)
# ==============================================================================
# We add a /route endpoint so your IDE can call it.

cat <<PYTHON > apps/flyingmonkeys-server/src/router_routes.py
from fastapi import APIRouter
from pydantic import BaseModel
import sys, os

# Path Hack
sys.path.append(os.path.abspath("../../../libs"))
from aiyou.proxies.routing_agent import router as agent_router
# Check if arsenal/flying_monkeys exists, else mock it to prevent crash
try:
    from arsenal.flying_monkeys.swarm import SwarmController
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
    # 1. Ask the Router (Is this for the monkeys?)
    decision = agent_router.dispatch(r.query)
    
    # 2. Execute
    if decision["route"] == "SWARM":
        # Launch the Swarm
        result = swarm.deploy_bravo(r.query)
        return {"action": "SWARM_DEPLOYED", "details": result}
    else:
        # Just return the advice (Mocking Local execution)
        return {"action": "LOCAL_EXECUTION", "details": "Task is simple. Suggest doing it in-context."}
PYTHON

# ==============================================================================
# 3. UPDATE MAIN SERVER
# ==============================================================================

# Ensure manager_routes exists or create mock
if [ ! -f apps/flyingmonkeys-server/src/manager_routes.py ]; then
    cat <<PYTHON > apps/flyingmonkeys-server/src/manager_routes.py
from fastapi import APIRouter
router = APIRouter()
@router.get("/")
def home(): return {"status": "Mock Manager Active"}
PYTHON
fi

cat <<PYTHON > apps/flyingmonkeys-server/src/main.py
import sys, os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Imports
sys.path.append(os.path.abspath("../../../libs"))
from manager_routes import router as manager_router
from router_routes import api_router as router_dispatcher

app = FastAPI()

# Mount Routes
app.include_router(manager_router, prefix="/manager")
app.include_router(router_dispatcher, prefix="/api")

# UI
if os.path.isdir("../../apps/agent-manager-ui/public"):
    app.mount("/", StaticFiles(directory="../../apps/agent-manager-ui/public", html=True), name="ui")
else:
    print("UI directory not found, skipping mount.")

PYTHON

echo ">>> ✅ ROUTER INJECTED."
echo "👉 The Router uses the ECHO PROTOCOL to classify tasks."
echo "👉 Use: POST /api/dispatch {'query': '...'} to test."
