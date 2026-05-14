# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations

import logging

from core.governance.fabric import PolicyObjectionError, governance_fabric

logger = logging.getLogger("ATP_5_19_LATTICE")


class ContinuityLattice:
    """
    Implements the Universal 5-Step ATP 5-19 Continuity Lattice inside Cor.Yay.
    Detect -> Score -> Overlay-select -> Enforce -> Terminal Containment.
    """

    def __init__(self):
        self.fabric = governance_fabric

    async def execute_lattice_flow(
        self,
        action: str,
        payload: dict,
        user_id: str,
        framework: str,
        subscribed_tiers: list[str],
    ) -> dict:
        """
        Runs the 5-layer continuity protocol across an agent's intended action.
        Throws a PolicyObjectionError if the action is deemed catastrophic or illegal.
        Returns the AST-rewritten payload if it is permitted with modifiers.
        """
        logger.info(f"Initiating ATP 5-19 Lattice for action [{action}] on user {user_id}")

        try:
            # The entire 5-layer pipeline is physically baked into the Governance Fabric
            final_payload = await self.fabric._run_atp5_19(
                action=action,
                payload=payload,
                user_id=user_id,
                framework=framework,
                subscribed_tiers=subscribed_tiers,
            )
            logger.info("Lattice check PASSED. Output structurally safe.")
            return final_payload

        except PolicyObjectionError as e:
            logger.critical(f"Lattice TERMINAL CONTAINMENT ENFORCED: {str(e)}")
            raise


lattice_engine = ContinuityLattice()
