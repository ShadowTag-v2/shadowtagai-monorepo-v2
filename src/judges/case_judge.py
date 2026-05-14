# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
CaseJudge - Legal Case Assessment
Binary ALLOW/BLOCK decisions for legal case strategies and actions

Primary Use Cases:
- Case acceptance decisions
- Settlement authorization
- Litigation strategy approval
- Discovery scope validation
"""

from typing import Dict, Any
from src.judges.base_judge import BaseJudge
from src.judges.models import JudgeRequest, JudgeDecision, JudgeType
from src.risk_matrix import Probability, Severity


class CaseJudge(BaseJudge):
    """
    Legal case assessment judge

    Evaluates:
    - Case acceptance (new client/matter intake)
    - Settlement proposals
    - Litigation strategy changes
    - Discovery requests
    - Motion filings
    """

    def __init__(self):
        super().__init__(JudgeType.CASE)
        self.settlement_threshold = 100_000  # $100K settlement approval threshold

    def evaluate_action(self, request: JudgeRequest) -> dict[str, Any]:
        """
        Evaluate legal case action

        Decision logic:
        1. Case value assessment
        2. Conflict of interest check
        3. Risk/reward analysis
        4. Resource availability
        5. Strategic alignment
        """
        context = request.context
        action_type = request.action_type

        # Extract case parameters
        case_value = context.get("case_value_usd", 0)
        case_type = context.get("case_type", "unknown")
        conflict_check = context.get("conflict_check_passed", False)
        settlement_amount = context.get("settlement_amount_usd", 0)
        probability_of_success = context.get("probability_of_success", 0.5)
        statute_of_limitations = context.get("statute_of_limitations_days", 365)

        # Decision rules
        decision = JudgeDecision.ALLOW
        reasoning_parts = []

        # Rule 1: Case acceptance - conflict check
        if action_type == "case_acceptance":
            if not conflict_check:
                decision = JudgeDecision.BLOCK
                reasoning_parts.append("Conflict of interest check not passed - BLOCK")
            elif case_value < 10_000:
                decision = JudgeDecision.BLOCK
                reasoning_parts.append("Case value below minimum threshold")
            else:
                reasoning_parts.append("Case acceptance approved pending engagement letter")

        # Rule 2: Settlement authorization
        elif action_type == "settlement_approval":
            if settlement_amount >= self.settlement_threshold:
                reasoning_parts.append(f"Settlement ${settlement_amount:,.0f} requires partner approval")

            if settlement_amount > case_value * 0.8:
                reasoning_parts.append("Settlement >80% of case value - favorable")
            elif settlement_amount < case_value * 0.2:
                decision = JudgeDecision.BLOCK
                reasoning_parts.append("Settlement <20% of case value - requires justification")

        # Rule 3: Litigation strategy
        elif action_type == "litigation_strategy":
            if probability_of_success < 0.3:
                decision = JudgeDecision.BLOCK
                reasoning_parts.append("Low probability of success (<30%) - recommend settlement")
            elif probability_of_success > 0.7:
                reasoning_parts.append("High probability of success - proceed with litigation")

        # Rule 4: Statute of limitations check
        if statute_of_limitations < 30:
            reasoning_parts.append("URGENT: Statute of limitations < 30 days - expedite")

        # Build reasoning
        if not reasoning_parts:
            reasoning = f"{action_type} for {case_type} case - standard review"
        else:
            reasoning = "; ".join(reasoning_parts)

        return {
            "decision": decision,
            "reasoning": reasoning,
            "metadata": {
                "case_value": case_value,
                "case_type": case_type,
                "settlement_amount": settlement_amount,
                "probability_of_success": probability_of_success,
                "conflict_check": conflict_check,
            },
        }

    def extract_risk_factors(self, request: JudgeRequest, evaluation: dict[str, Any]) -> tuple[Probability, Severity, str, list[str]]:
        """
        Extract ATP 5-19 risk factors for legal cases

        Probability factors:
        - Probability of success assessment
        - Conflict of interest presence
        - Precedent strength
        - Jurisdiction favorability

        Severity factors:
        - Case value
        - Reputational impact
        - Regulatory implications
        - Client relationship importance
        """
        context = request.context
        case_value = context.get("case_value_usd", 0)
        prob_success = context.get("probability_of_success", 0.5)
        conflict_check = context.get("conflict_check_passed", False)

        # Determine probability based on success likelihood
        if not conflict_check:
            probability = Probability.A  # Almost certain (ethics violation)
        elif prob_success < 0.3:
            probability = Probability.B  # Likely (to lose case)
        elif prob_success < 0.5:
            probability = Probability.C  # Possible
        elif prob_success < 0.7:
            probability = Probability.D  # Unlikely (to lose)
        else:
            probability = Probability.E  # Rare (to lose)

        # Determine severity based on case value and type
        if case_value >= 10_000_000 or context.get("high_profile", False):
            severity = Severity.I  # Catastrophic (reputational + financial)
        elif case_value >= 1_000_000:
            severity = Severity.II  # Critical
        elif case_value >= 100_000:
            severity = Severity.III  # Moderate
        else:
            severity = Severity.IV  # Negligible

        # Rationale
        case_type = context.get("case_type", "unknown")
        rationale = (
            f"Legal case assessment: {case_type} valued at ${case_value:,.0f}. "
            f"Probability of success: {prob_success * 100:.0f}%. "
            f"Conflict check: {'passed' if conflict_check else 'FAILED'}. "
            f"Risk of adverse outcome or ethics violation."
        )

        # Mitigations
        mitigations = []
        if not conflict_check:
            mitigations.append("Complete comprehensive conflict of interest analysis")
            mitigations.append("Obtain ethics committee clearance")
        if prob_success < 0.5:
            mitigations.append("Explore settlement options")
            mitigations.append("Obtain second opinion from senior litigator")
        if case_value >= self.settlement_threshold:
            mitigations.append("Require partner-level approval")
        mitigations.append("Document decision rationale for file")
        mitigations.append("Obtain client informed consent")

        return probability, severity, rationale, mitigations


__all__ = ["CaseJudge"]
