# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from src.governance.memory.memory_bank import MemoryBank
from src.governance.voting.cav_mtoe import CavMTOE


class JudgeSixSentinel:
    def __init__(self):
        self.army = CavMTOE()
        self.memory = MemoryBank()
        self.forbidden = ["sk-", "rm -rf", "0.0.0.0/0"]

    def evaluate(self, query: str, context: str = "general") -> dict:
        # 1. Hazard Check
        if any(bad in query for bad in self.forbidden):
            return {"status": "BLOCKED", "reason": "Hazard Pattern Detected (Gate 1)"}

        # 2. Memory Check
        if self.memory.consult(query, context) == "ALLOW":
            return {"status": "SUCCESS", "reason": "Memory Override"}

        # 3. Army Vote (Simulation of High Risk)
        # Assuming all new queries are 'Medium' risk by default
        vote = self.army.bottom_up_vote(query, "M")

        if vote["verdict"] == "APPROVED":
            return {"status": "SUCCESS", "reason": f"Army Consensus: {vote['approval_rate']:.1%}"}
        return {"status": "BLOCKED", "reason": "Army Rejected Mission"}
