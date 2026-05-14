# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import logging
from typing import Any

from agent_engine.verification.signing import ArtifactSigner
from core.coryay.lattice import lattice_engine
from core.governance.fabric import PolicyObjectionError, governance_fabric
from core.jurisdiction.engine import JurisdictionEngine
from observability.pii import redact_pii
from policy_engine.objection.service import ObjectionEngine

logger = logging.getLogger("CorYayOrchestrator")


class CloudIDEOrchestrator:
    """
    The Nervous System of Cor.Yay Sovereign OS.
    Fuses the VFS IDE, Kosmos Swarm, 17-Layer Shield, and Gideon Server into a single API endpoint.
    """

    def __init__(self):
        self.jurisdiction = JurisdictionEngine()
        self.objection = ObjectionEngine()
        self.fabric = governance_fabric
        self.lattice = lattice_engine
        self.signer = ArtifactSigner()

    async def execute_agent_action(
        self,
        tenant_id: str,
        user_id: str,
        action: str,
        payload: dict[str, Any],
        client_tier: str = "BASE",
        data_class: str = "STANDARD",
        active_framework: str = "NY_RAISE_ACT_2027",
        subscribed_tiers: list[str] = None,
    ) -> dict:
        if subscribed_tiers is None:
            subscribed_tiers = ["LAYER_25"]  # Hardcoding the RAISE Act shield default for demo purposes

        logger.info(f"Orchestrator Booting for {tenant_id} action: {action}")

        # 1. Jurisdiction Wall (Physical Routing)
        self.jurisdiction.raise_if_prohibited(client_tier, data_class)
        logger.info(f"[GATE 0] Physical Execution Zone Verified ({self.jurisdiction.current_zone.value})")

        # 2. Gate 1 Semantic Objection Engine (Pre-execution intent check)
        # Check diff intent if payload contains "diff_text"
        diff_text = payload.get("diff_text")
        if diff_text:
            decision = self.objection.evaluate_diff("Automated PR", diff_text, ["agent_target.py"])
            self.objection.raise_if_rejected(decision)
            logger.info(f"[GATE 1] LLM-Judge passed semantic intent check (Confidence: {decision.confidence})")

        # 3. 5-Layer ATP-5-19 Lattice (Runtime Compliance & Risk Overlay)
        try:
            safe_payload = await self.lattice.execute_lattice_flow(
                action=action,
                payload=payload,
                user_id=user_id,
                framework=active_framework,
                subscribed_tiers=subscribed_tiers,
            )
        except PolicyObjectionError as e:
            # PII redactor catches the error trace before Sentry
            safe_error = redact_pii(str(e))
            logger.critical(f"[GATE 2] LATTICE CONTAINMENT REACHED. Action aborted: {safe_error}")
            raise e

        # 4. Final Zero-Trust Artifact Signature
        signed_execution = self.signer.sign_payload(safe_payload)
        logger.info(f"[GATE 3] Validated Output Signed by SigStore ({self.signer.identity})")

        return signed_execution
