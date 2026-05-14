# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Purpose Validator - JR Engine Component 1

Validates the PURPOSE of an action:
- What is this action trying to accomplish?
- Does it align with business objectives?
- Is there a clear mission statement?
- What is the value proposition?
"""

from typing import Optional
from ..models import Action, PurposeVerdict, VerdictStatus


class PurposeValidator:
    """
    Validates the PURPOSE dimension of an action
    """

    def __init__(self):
        self.mission_keywords = {"enable", "improve", "optimize", "secure", "protect", "deliver", "provide", "support", "enhance", "facilitate"}
        self.prohibited_purposes = {"bypass", "circumvent", "exploit", "hack", "abuse"}

    def validate(self, action: Action) -> PurposeVerdict:
        """
        Validate the purpose of an action

        Args:
            action: The action to validate

        Returns:
            PurposeVerdict with status and scoring
        """
        # Extract purpose from action description/context
        purpose = self._extract_purpose(action)

        # Check for clear business objective
        business_objective = self._identify_business_objective(action)

        # Check mission alignment
        mission_alignment = self._check_mission_alignment(action)

        # Check value proposition
        value_proposition = self._assess_value_proposition(action)

        # Calculate alignment score (0-10)
        score = self._calculate_score(business_objective, mission_alignment, value_proposition)

        # Determine status
        if score >= 7.0:
            status = VerdictStatus.APPROVED
        elif score >= 5.0:
            status = VerdictStatus.FLAGGED
        elif score >= 3.0:
            status = VerdictStatus.REQUIRES_REVIEW
        else:
            status = VerdictStatus.REJECTED

        # Check for prohibited purposes
        if self._has_prohibited_purpose(action):
            status = VerdictStatus.REJECTED
            score = 0.0

        explanation = self._generate_explanation(status, score, business_objective, mission_alignment)

        return PurposeVerdict(
            status=status,
            score=score,
            business_objective=business_objective,
            mission_alignment=mission_alignment,
            value_proposition=value_proposition,
            explanation=explanation,
            confidence=0.85,  # Default confidence (could be ML-based)
        )

    def _extract_purpose(self, action: Action) -> str:
        """Extract purpose from action description/context"""
        # Check for explicit purpose in context
        if "purpose" in action.context:
            return action.context["purpose"]

        # Otherwise use description
        return action.description

    def _identify_business_objective(self, action: Action) -> str | None:
        """Identify the business objective"""
        purpose = self._extract_purpose(action)

        # Look for mission keywords
        for keyword in self.mission_keywords:
            if keyword in purpose.lower():
                return f"Identified objective: {keyword.upper()} user/system capability"

        # Check context for objective
        if "objective" in action.context:
            return action.context["objective"]

        return None

    def _check_mission_alignment(self, action: Action) -> str:
        """Check if action aligns with organizational mission"""
        purpose = self._extract_purpose(action).lower()

        # Positive alignment indicators
        positive_indicators = ["user", "customer", "security", "compliance", "value"]
        negative_indicators = ["workaround", "temporary fix", "quick hack"]

        positive_count = sum(1 for ind in positive_indicators if ind in purpose)
        negative_count = sum(1 for ind in negative_indicators if ind in purpose)

        if positive_count > negative_count:
            return "aligned"
        elif negative_count > positive_count:
            return "misaligned"
        else:
            return "unclear"

    def _assess_value_proposition(self, action: Action) -> str | None:
        """Assess the value proposition of the action"""
        purpose = self._extract_purpose(action).lower()

        value_keywords = {
            "improve": "efficiency_gain",
            "optimize": "performance_improvement",
            "secure": "security_enhancement",
            "enable": "capability_creation",
            "reduce": "cost_reduction",
        }

        for keyword, value_type in value_keywords.items():
            if keyword in purpose:
                return value_type

        return None

    def _has_prohibited_purpose(self, action: Action) -> bool:
        """Check if action has a prohibited purpose"""
        purpose = self._extract_purpose(action).lower()

        for prohibited in self.prohibited_purposes:
            if prohibited in purpose:
                return True

        return False

    def _calculate_score(
        self,
        business_objective: str | None,
        mission_alignment: str,
        value_proposition: str | None,
    ) -> float:
        """Calculate purpose alignment score (0-10)"""
        score = 5.0  # Baseline

        # Business objective defined: +2.0
        if business_objective:
            score += 2.0

        # Mission alignment: -2.0 to +2.0
        if mission_alignment == "aligned":
            score += 2.0
        elif mission_alignment == "misaligned":
            score -= 2.0

        # Value proposition defined: +1.0
        if value_proposition:
            score += 1.0

        return min(10.0, max(0.0, score))

    def _generate_explanation(
        self,
        status: VerdictStatus,
        score: float,
        business_objective: str | None,
        mission_alignment: str,
    ) -> str:
        """Generate human-readable explanation"""
        if status == VerdictStatus.APPROVED:
            return (
                f"Purpose is clear and aligned (score: {score}/10). "
                f"Business objective: {business_objective or 'implicit'}. "
                f"Mission alignment: {mission_alignment}."
            )
        elif status == VerdictStatus.REJECTED:
            return f"Purpose is unclear or prohibited (score: {score}/10). Action does not meet purpose criteria."
        elif status == VerdictStatus.FLAGGED:
            return f"Purpose is somewhat clear but requires attention (score: {score}/10). Mission alignment: {mission_alignment}."
        else:  # REQUIRES_REVIEW
            return f"Purpose requires human review (score: {score}/10). Insufficient clarity on business objective or mission alignment."
