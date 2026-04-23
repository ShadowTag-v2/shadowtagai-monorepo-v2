import logging
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from .zt_identity import ZeroTrustIdentity, verify_zero_trust_token

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/intercept",
    tags=["intercept"],
    dependencies=[Depends(verify_zero_trust_token)],
)


class ToolCallRequest(BaseModel):
    function_name: str
    arguments: dict[str, Any]


class ToolCallResponse(BaseModel):
    status: str
    reason: str | None = None


@router.post("/tool-call", response_model=ToolCallResponse)
async def intercept_tool_call(
    request: ToolCallRequest,
    identity: ZeroTrustIdentity = Depends(verify_zero_trust_token),  # noqa: B008
):
    logger.info(
        f"[SHIELD 1] Intercepting tool call: {request.function_name} by principal ID: {identity.email}",
    )

    # ATP 5-19 Deterministic Math
    if request.function_name == "execute_vanguard_purchase":
        cost_usd = float(request.arguments.get("cost_usd", 0))
        domain = request.arguments.get("supplier_domain", "")

        # Tier 5 (Catastrophic)
        if "restricted" in domain or "bank" in domain:
            logger.warning("[SHIELD 1] RKILL triggers on prohibited domain.")
            return ToolCallResponse(status="RKILL", reason="Tier 5 Violation: Restricted Domain")

        # Tier 3 (Significant Consequence / Require Native FaceID)
        if cost_usd > 100:
            logger.info("[SHIELD 1] REQUIRE COA triggers on high budget utilization.")
            return ToolCallResponse(
                status="REQUIRE_COA_CONFIRMATION",
                reason="Tier 3 Risk: High Cost Threshold",
            )

        # Tier 1/2 (Cleared)
        logger.info("[SHIELD 1] Tool cleared for execution.")
        return ToolCallResponse(status="CLEARED")

    if request.function_name == "trigger_swarm_refactor":
        scope = request.arguments.get("scope", "")
        if "core" in scope or "security" in scope:
            return ToolCallResponse(
                status="REQUIRE_COA_CONFIRMATION",
                reason="Tier 3 Risk: Core modification",
            )
        return ToolCallResponse(status="CLEARED")

    return ToolCallResponse(status="RKILL", reason="Unknown tool call blocked by un-allowed-list.")
