# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import logging

from src.governance.Claude_Code_6.gauntlet_17_layer import Gauntlet17Layer
from src.governance.memory.memory_bank import MemoryBank

logger = logging.getLogger(__name__)


class JudgeSixSentinel:
    """Sovereign OS Governance Core.
    Gates execution via Hazard checking, Context Memory, and Swarm Consensus.
    """

    def __init__(self):
        self.gauntlet = Gauntlet17Layer()
        self.memory = MemoryBank()
        # Simulated forbidden vectors tailored to Sovereign architecture
        self.forbidden = ["sk-", "rm -rf", "0.0.0.0/0", "drop table", "truncate"]

    def evaluate(self, query: str, context: str = "general") -> dict:
        # 1. Hazard Check
        if any(bad in query.lower() for bad in self.forbidden):
            logger.warning("[SENTINEL] Hazard pattern detected in query.")
            return {"status": "BLOCKED", "reason": "Hazard Pattern Detected (Gate 1)"}

        # 2. Memory Check (Learned suppression bypass)
        if self.memory.consult(query, context) == "ALLOW":
            logger.info("[SENTINEL] Exception mapped via Memory Override.")
            return {"status": "SUCCESS", "reason": "Memory Override Allows Exception"}

        # 3. 17-Layer DOW CRSMC Gauntlet (ATP 5-19 Risk Mitigation)
        inspection = self.gauntlet.judge(query)

        if inspection["verdict"] == "APPROVED":
            logger.info("[SENTINEL] Mission Authorized by 17-Layer Gauntlet.")
            return {"status": "SUCCESS", "reason": "Gauntlet Passed"}
        logger.warning("[SENTINEL] Mission Denied by Gauntlet.")
        return {
            "status": "BLOCKED",
            "reason": inspection.get("reason", "Gauntlet Rejected Mission"),
        }
