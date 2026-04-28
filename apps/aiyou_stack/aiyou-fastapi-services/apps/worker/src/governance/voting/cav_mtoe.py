# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import random


class CavMTOE:
    """Simulates a Cavalry Squadron (MTOE) Voting Swarm. ~650 Units."""

    def __init__(self, num_soldiers=650):
        self.num_soldiers = num_soldiers
        self.risk_thresholds = {"LOW": 0.51, "MEDIUM": 0.66, "HIGH": 0.80, "EXTREME": 0.95}

    def bottom_up_vote(self, intent: str, risk_level: str) -> dict:
        base_approval = random.uniform(0.60, 0.99)
        friction = 0.15 if risk_level == "HIGH" else 0.30 if risk_level == "EXTREME" else 0.0
        actual_approval = max(0, base_approval - friction)
        required_threshold = self.risk_thresholds.get(risk_level, 0.51)
        passed = actual_approval >= required_threshold

        return {
            "intent": intent,
            "risk_level": risk_level,
            "approval_rate": actual_approval,
            "final_action": "A" if passed else "D",
        }
