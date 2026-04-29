# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os
import sys

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Imports
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../src/libs/shadowtag_v4")),
)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../src/libs")))
# UN-MOCKED BRIDGE (Sovereign)
from manager_routes import router as manager_router
from router_routes import api_router as router_dispatcher
from shadowtag_v4.bridge_client import bridge

# Verified: This file imports from src.memory, which defaults PROJECT_ID to os.getenv.
# No hardcoded ID here to replace, but good to check.
# from src.governance.judge_six.core import JudgeSixEngine # POSTPONED
# from src.intelligence.tegu_vision.detector import TeguVision # POSTPONED
from src.memory import get_memory_storage

app = FastAPI()

# Mount Routes
app.include_router(manager_router, prefix="/manager")
app.include_router(router_dispatcher, prefix="/api")

# UI (Make path robust)
ui_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../agent-manager-ui/public"))
if os.path.exists(ui_path):
    app.mount("/", StaticFiles(directory=ui_path, html=True), name="ui")
else:
    print(f"⚠️ UI Path not found: {ui_path}")

    @app.get("/")
    def root():
        return {"status": "Router Active. UI not found."}


# Initialize Engines
# Cor.Claude_Code_6 = JudgeSixEngine() # POSTPONED
# tegu = TeguVision() # POSTPONED
memory = get_memory_storage()
memory = get_memory_storage()
# bridge is imported directly above


class RiskRequest(BaseModel):
    code: str = None
    query: str = None
    mission_id: str = "CMD-001"


class ScanRequest(BaseModel):
    file_path: str
    intent: str


class UIRequest(BaseModel):
    intent: str


@app.get("/health")
async def health():
    return {"status": "ACTIVE", "system": "n-autoresearch/Kosmos/BioAgents v3.0"}


@app.post("/risk")
async def check_risk(request: RiskRequest):
    print(f"⚡ CMD: /risk received for {request.mission_id}")
    # Cor.Claude_Code_6 POSTPONED
    return {
        "approved": True,
        "risk_tier": "POSTPONED",
        "hash": "NO-HASH",
        "authority": "BYPASS_MONKEYS_ONLY",
    }


@app.post("/scan")
async def scan_file(request: ScanRequest):
    print(f"⚡ CMD: /scan received for {request.file_path}")
    # Tegu POSTPONED
    return {
        "status": "SCANNED",
        "tegu_score": 0.0,
        "extraction": f"Scanning postponed for {request.intent}",
    }


@app.post("/ui")
async def generate_ui(request: UIRequest):
    print(f"⚡ CMD: /ui received for {request.intent}")
    # Stub for A2UI generation
    return {
        "type": "A2UI_COMPONENT",
        "intent": request.intent,
        "layout": "default_card",
        "elements": ["header", "content", "actions"],
    }


class TaskRequest(BaseModel):
    instruction: str
    url: str = None
    intent: str = "general"


class LakeQuery(BaseModel):
    sql: str


# --- AGENT BRIDGE ENDPOINTS ---


@app.post("/agent/dispatch")
async def dispatch_agent_task(task: TaskRequest):
    """Refactored: Sends task to Firestore Task Queue for Workstation Agent"""
    task_id = bridge.dispatch_task(task.instruction, task.url, task.intent)
    return {"status": "dispatched", "task_id": task_id, "queue": "firestore::agent_tasks"}


@app.get("/agent/task/{task_id}")
async def get_agent_task(task_id: str):
    """Retrieves Agent Status & A2UI Result"""
    return bridge.get_task_status(task_id)


@app.post("/agent/lake")
async def query_lake(query: LakeQuery):
    """Queries the Iceberg Data Lake"""
    try:
        results = bridge.query_lake(query.sql)
        return {"status": "success", "rows": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.get("/memory")
async def get_memory():
    """Retrieve current context from Firestore/GCS"""
    return memory.load_from_firestore()


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
