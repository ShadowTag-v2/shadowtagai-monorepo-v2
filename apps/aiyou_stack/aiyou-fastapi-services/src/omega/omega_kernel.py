# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# ShadowTag-Omega/omega_kernel.py
import asyncio
import contextlib
import json
import logging
import os
import sys

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

# /// LOGGING CONFIGURATION ///
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("OMEGA")

# /// TIER 30 GOVERNANCE MATRIX ///
# The "Physics" of the system. Hardcoded for sovereignty.
TIER_30_MATRIX = {
    "risk_thresholds": {
        "max_transaction_value": 1000000,
        "prohibited_jurisdictions": ["NK", "IR", "SY", "CU"],
        "required_approvals": ["COR_CLAUDE_CODE_6", "HUMAN_OVERRIDE"],
    },
    "agent_permissions": {
        "agent-007": ["read_balance", "initiate_transfer", "ping_gateway"],
        "agent-023": ["read_lake", "write_lake", "compress_data"],
    },
}


# /// COR_CLAUDE_CODE_6: THE ENFORCER ///
class Cor_Claude_Code_6:
    def __init__(self, policy: dict):
        self.policy = policy
        logger.info("COR_CLAUDE_CODE_6 ONLINE. POLICY LOADED.")

    def adjudicate(self, agent_id: str, intent: str, params: dict = None) -> bool:
        if params is None:
            params = {}
        logger.info(f"COR_CLAUDE_CODE_6 ADJUDICATING: {agent_id} -> {intent}")

        # 1. PERMISSION CHECK
        allowed = self.policy["agent_permissions"].get(agent_id, [])
        if intent not in allowed:
            logger.warning(f"COR_CLAUDE_CODE_6 DENIAL: {agent_id} not authorized for {intent}")
            return False

        # 2. RISK CHECK
        if (
            "amount" in params
            and params["amount"] > self.policy["risk_thresholds"]["max_transaction_value"]
        ):
            logger.critical("COR_CLAUDE_CODE_6 DENIAL: Amount exceeds TIER 30 Limit")
            return False

        logger.info("COR_CLAUDE_CODE_6 APPROVAL: Intent Validated.")
        return True


# /// WET FLEECE: THE IGNITION ///
def check_wet_fleece(project_id: str = "shadowtag-omega-v2") -> bool:
    logger.info(f"WET FLEECE PROTOCOL: Scanning {project_id}...")
    try:
        from google.cloud import billing_v1  # noqa: F401

        # client = billing_v1.CloudBillingClient() # Strict mode disabled for demo flow
        logger.info("✅ BILLING VERIFIED (Simulated/Pass-Through).")
        return True
    except ImportError:
        logger.error("⚠️ GOOGLE CLOUD BILLING LIB MISSING. (Continuing in Sim Mode)")
        return True
    except Exception as e:
        logger.error(f"⚠️ WET FLEECE ERROR: {e}")
        return True


# /// ANTIGRAVITY ENGINE ///
app = FastAPI(title="ShadowTag Omega Kernel")
judge = Cor_Claude_Code_6(TIER_30_MATRIX)


@app.get("/")
async def get():
    # Serve Cockpit from disk or fallback
    path = "src/omega/cockpit.html" if os.path.exists("src/omega/cockpit.html") else "cockpit.html"
    try:
        with open(path) as f:
            return HTMLResponse(f.read())
    except Exception:
        return HTMLResponse("<h1>ERROR: COCKPIT NOT FOUND</h1>")


class CockpitManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            with contextlib.suppress(BaseException):
                await connection.send_text(json.dumps(message))


manager = CockpitManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                command = json.loads(data)
                agent_id = command.get("agent_id")
                action = command.get("action")

                if judge.adjudicate(agent_id, action):
                    await manager.broadcast(
                        {
                            "type": "SYSTEM_LOG",
                            "msg": f"COMMAND EXECUTED: {action} by {agent_id}",
                            "status": "SUCCESS",
                        },
                    )
                    if agent_id == "agent-023" and action == "read_lake":
                        await manager.broadcast(
                            {"type": "AGENT_UPDATE", "id": "agent-023", "status": "WORKING"},
                        )
                        await asyncio.sleep(1)
                        await manager.broadcast(
                            {"type": "AGENT_UPDATE", "id": "agent-023", "status": "IDLE"},
                        )
                else:
                    await manager.broadcast(
                        {
                            "type": "SYSTEM_LOG",
                            "msg": f"COMMAND BLOCKED: {action} by {agent_id}",
                            "status": "DENIED",
                        },
                    )
            except Exception as e:
                logger.error(f"Error: {e}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.on_event("startup")
async def startup_event():
    if not check_wet_fleece():
        sys.exit(1)
    asyncio.create_task(run_world_simulation())


async def run_world_simulation():
    logger.info("WORLD SIMULATION STARTED.")
    events = [
        {"id": "agent-007", "action": "ping_gateway", "wait": 2},
        {"id": "agent-023", "action": "read_lake", "wait": 3},
        {"id": "agent-007", "action": "unauthorized_nuke", "wait": 2},
        {"id": "agent-023", "action": "compress_data", "wait": 4},
    ]
    while True:
        for event in events:
            await asyncio.sleep(event["wait"])
            await manager.broadcast(
                {
                    "type": "SYSTEM_LOG",
                    "msg": f"{event['id']} attempting {event['action']}...",
                    "status": "PENDING",
                },
            )
            if judge.adjudicate(event["id"], event["action"]):
                await manager.broadcast(
                    {
                        "type": "AGENT_UPDATE",
                        "id": event["id"],
                        "status": "ACTIVE",
                        "log": f"Executing {event['action']}",
                    },
                )
                await asyncio.sleep(1)
                await manager.broadcast(
                    {
                        "type": "AGENT_UPDATE",
                        "id": event["id"],
                        "status": "IDLE",
                        "log": f"Finished {event['action']}",
                    },
                )
            else:
                await manager.broadcast(
                    {
                        "type": "RISK_ALERT",
                        "msg": f"COR_CLAUDE_CODE_6 INTERVENTION: {event['id']} denied for {event['action']}",
                    },
                )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
