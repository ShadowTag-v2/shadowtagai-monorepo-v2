# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Reasons Validator - JR Engine Component 2

Validates the REASONS for an action:
- Why is this action justified?
- What evidence supports this decision?
- What is the risk/reward analysis?
- What is the stakeholder impact?
"""

from ..models import Action, ReasonsVerdict, VerdictStatus


class ReasonsValidator:
    """Validates the REASONS dimension of an action"""

    def validate(self, action: Action) -> ReasonsVerdict:
        # Heuristic validation
        has_evidence = "evidence" in action.metadata or "justification" in action.payload
        risk = action.metadata.get("risk", "low")
        reward = action.metadata.get("reward", "medium")

        score = 5.0
        if has_evidence:
            score += 3.0

        status = VerdictStatus.APPROVED
        risk_reward_ratio = 1.0  # 1:1

        if risk == "high" and reward == "low":
            status = VerdictStatus.REJECTED
            score = 2.0
            explanation = "High risk, low reward."
        else:
            explanation = "Justification accepted."

        return ReasonsVerdict(
            score=score,
            status=status,
            evidence_quality="medium" if has_evidence else "weak",
            risk_reward_ratio=risk_reward_ratio,
            stakeholder_impact="medium",
            explanation=explanation,
        )
