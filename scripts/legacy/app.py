from __future__ import annotations

import logging
from typing import Any

from core.coryay.orchestrator import CloudIDEOrchestrator
from fastapi import FastAPI, HTTPException
from observability.logging_setup import set_up_observability
from policy_engine.objection.api import router as objection_router
from pydantic import BaseModel

set_up_observability()
logger = logging.getLogger("CorYayAPI")

app = FastAPI(
    title="Cor.Yay Sovereign OS",
    description="The Gideon OS Gate 1 Semantic & 17-Layer DOW CRSMC Governance Sandbox",
    version="6.1.0",
)

app.include_router(objection_router)

# Unified Orchestrator Instance
orchestrator = CloudIDEOrchestrator()


class AgentExecutionRequest(BaseModel):
    tenant_id: str
    user_id: str
    action: str
    payload: dict[str, Any]
    client_tier: str = "BASE"
    data_class: str = "STANDARD"
    active_framework: str = "NY_RAISE_ACT_2027"
    subscribed_tiers: list[str] = ["LAYER_25"]


@app.post("/api/v1/agent/execute")
async def execute_agent_endpoint(req: AgentExecutionRequest):
    """
    Main ingestion endpoint for Autonomous AI events underneath the Uphillsnowball Matrix.
    Forces all interactions through the 4-Gate System (Jurisdiction, Intent, Lattice, Sigstore).
    """
    try:
        signed_artifact = await orchestrator.execute_agent_action(
            tenant_id=req.tenant_id,
            user_id=req.user_id,
            action=req.action,
            payload=req.payload,
            client_tier=req.client_tier,
            data_class=req.data_class,
            active_framework=req.active_framework,
            subscribed_tiers=req.subscribed_tiers,
        )
        return {"status": "SUCCESS", "provenance": signed_artifact}

    except PermissionError as pe:
        logger.error(f"[GATE 0 FAILED] {str(pe)}")
        raise HTTPException(status_code=403, detail=str(pe))
    except RuntimeError as re:
        logger.error(f"[GATE 1 SEMANTIC JUDGE FAILED] {str(re)}")
        raise HTTPException(status_code=451, detail=str(re))
    except Exception as e:
        logger.critical(f"[LATTICE_ERROR] Terminal Containment activated. Cause: {str(e)}")
        raise HTTPException(status_code=500, detail="Terminal Governance Contains this Flow.")
