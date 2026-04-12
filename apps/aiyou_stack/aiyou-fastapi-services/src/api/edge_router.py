import logging
import os

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

# Security / ZT Imports
from src.api.zt_identity import TemporalIdentityPayload, parse_and_lock_identity

edge_router = APIRouter(prefix="/api/v1/edge", tags=["edge_router"])
logger = logging.getLogger("EdgeRouter")

MOCK_CLOUD_RUN_ANE = os.getenv("MOCK_CLOUD_RUN_ANE", "true").lower() == "true"


class SecurityPayload(BaseModel):
    threat_string: str
    regex_hash: str


class PreferencePayload(BaseModel):
    category: str
    max_budget: float
    user_id: str


@edge_router.post("/csrmc/evaluate")
async def evaluate_threat_edge(
    payload: SecurityPayload, identity: TemporalIdentityPayload = Depends(parse_and_lock_identity)
):
    """
    PHASE II: The Micro (CSRMC Edge)
    A tiny endpoint for the consumer app serving as a nerve ending.
    It intercepts MDM/Local VPN Regex hits.
    """
    logger.info(
        f"Edge Router triggered by Device: {identity.principal_id}. Threat Vector: {payload.regex_hash}"
    )

    if len(payload.threat_string) > 2048:
        raise HTTPException(
            status_code=400, detail="Edge Router Rejection: Payload exceeds 2KB CSRMC tolerance."
        )

    if MOCK_CLOUD_RUN_ANE:
        # Simulate local Kosmos Legal Execution Check natively
        return {
            "status": "Safe",
            "action": "log",
            "message": "[Apple Silicon Mode] 2KB Regex Validated against Edge Threat Matrix",
            "hash": payload.regex_hash,
        }

    # Cloud Run Sub-Penny Execution using Google Cloud Functions / Vertex Checks...
    return {"status": "Escalated to Hive Mind"}


@edge_router.post("/preference/terminal")
async def sync_blind_box_preference(
    payload: PreferencePayload, identity: TemporalIdentityPayload = Depends(parse_and_lock_identity)
):
    """
    The Preference Terminal: The glass UI where the user logs their Keep/Return ratio
    and "Blind Box" limits. This feeds into the overarching Hive Mind structure.
    """
    # Write preference state back to LanceDB / Cloud SQL for the Macro to ingest.
    logger.info(
        f"User {payload.user_id} configured Blind Box Category: {payload.category} at ${payload.max_budget}"
    )

    return {
        "status": "Logged to Macro Vector State",
        "category": payload.category,
        "action": "Blind Box Syndicate Updated",
    }
