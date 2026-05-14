# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
FinJudge - Financial Transaction Enforcement
Binary ALLOW/BLOCK decisions for financial transactions with HITL gates

Primary Use Case: $50K+ wire transfers requiring CFO approval
Decision Framework: Purpose=AiYouJR • Reason=Doctrine • Brakes=Army RM
"""

from typing import Any
from src.judges.base_judge import BaseJudge
from src.judges.models import JudgeRequest, JudgeDecision, JudgeType
from src.risk_matrix import Probability, Severity


class FinJudge(BaseJudge):
    """
    Financial transaction judge

    Evaluates:
    - Wire transfers
    - Payment authorizations
    - Contract financial approvals
    - Vendor payments
    - Capital expenditures
    """

    def __init__(self):
        super().__init__(JudgeType.FIN)
        self.wire_transfer_threshold = 50_000  # $50K threshold for CFO approval

    def evaluate_action(self, request: JudgeRequest) -> dict[str, Any]:
        """
        Evaluate financial transaction

        Decision logic:
        1. Amount checks (thresholds)
        2. Vendor verification status
        3. Purchase order validation
        4. Destination country risk
        5. Pattern anomaly detection
        """
        context = request.context
        action_type = request.action_type

        # Extract financial parameters
        amount_usd = context.get("amount_usd", 0)
        vendor_status = context.get("vendor_status", "unknown")
        has_purchase_order = context.get("purchase_order") is not None
        destination_country = context.get("destination_country", "US")
        is_new_vendor = vendor_status == "new" or vendor_status == "unverified"

        # Decision rules
        decision = JudgeDecision.ALLOW
        reasoning_parts = []

        # Rule 1: High-value wire transfer check
        if action_type == "wire_transfer" and amount_usd >= self.wire_transfer_threshold:
            reasoning_parts.append(f"Wire transfer amount ${amount_usd:,.0f} exceeds threshold")

            # Rule 2: New vendor without PO
            if is_new_vendor and not has_purchase_order:
                decision = JudgeDecision.BLOCK
                reasoning_parts.append("New/unverified vendor without purchase order - BLOCK")
            else:
                reasoning_parts.append("Requires CFO approval")

        # Rule 3: High-risk destination country
        high_risk_countries = ["Unknown", "XX", ""]
        if destination_country in high_risk_countries:
            if amount_usd > 10_000:
                decision = JudgeDecision.BLOCK
                reasoning_parts.append(f"High-risk destination country: {destination_country}")

        # Rule 4: Pattern anomaly (simplified - would use ML in production)
        if amount_usd > 100_000:
            # Large transaction always requires additional scrutiny
            reasoning_parts.append("Large transaction requires enhanced due diligence")

        # Rule 5: Approved vendor with PO - streamlined (only if not already blocked)
        if vendor_status == "approved" and has_purchase_order and decision != JudgeDecision.BLOCK:
            if amount_usd < self.wire_transfer_threshold:
                decision = JudgeDecision.ALLOW
                reasoning_parts.append("Approved vendor with PO - auto-approved")

        # Build reasoning
        if not reasoning_parts:
            reasoning = f"{action_type} for ${amount_usd:,.0f} - standard approval flow"
        else:
            reasoning = "; ".join(reasoning_parts)

        return {
            "decision": decision,
            "reasoning": reasoning,
            "metadata": {
                "amount_usd": amount_usd,
                "vendor_status": vendor_status,
                "has_po": has_purchase_order,
                "destination_country": destination_country,
                "threshold_exceeded": amount_usd >= self.wire_transfer_threshold,
            },
        }

    def extract_risk_factors(self, request: JudgeRequest, evaluation: dict[str, Any]) -> tuple[Probability, Severity, str, list[str]]:
        """
        Extract ATP 5-19 risk factors for financial transactions

        Probability factors:
        - Vendor verification status
        - Purchase order presence
        - Historical payment patterns
        - Fraud indicators

        Severity factors:
        - Transaction amount
        - Business impact if fraudulent
        - Regulatory implications
        """
        context = request.context
        amount_usd = context.get("amount_usd", 0)
        vendor_status = context.get("vendor_status", "unknown")
        has_po = context.get("purchase_order") is not None

        # Determine probability
        if vendor_status == "new" or vendor_status == "unverified":
            if not has_po:
                probability = Probability.B  # Likely (70-90%) - high fraud risk
            else:
                probability = Probability.C  # Possible (30-70%)
        elif vendor_status == "approved":
            probability = Probability.D  # Unlikely (10-30%)
        else:
            probability = Probability.C  # Possible

        # Determine severity based on amount
        if amount_usd >= 1_000_000:
            severity = Severity.I  # Catastrophic (>$10M potential impact with fraud chain)
        elif amount_usd >= 100_000:
            severity = Severity.II  # Critical ($1-10M impact potential)
        elif amount_usd >= 10_000:
            severity = Severity.III  # Moderate ($100K-1M impact)
        else:
            severity = Severity.IV  # Negligible (<$100K)

        # Rationale
        rationale = (
            f"Financial transaction: ${amount_usd:,.0f} to {vendor_status} vendor. "
            f"{'Purchase order in place' if has_po else 'No purchase order'}. "
            f"Risk of fraud or unauthorized payment."
        )

        # Mitigations
        mitigations = []
        if not has_po:
            mitigations.append("Verify vendor with external database (D&B, Creditsafe)")
        if vendor_status != "approved":
            mitigations.append("Conduct vendor due diligence")
        if amount_usd >= self.wire_transfer_threshold:
            mitigations.append("Require dual approval (CFO + Finance Director)")
        mitigations.append("Request supporting documentation from requester")
        mitigations.append("Verify bank account details via separate channel")

        return probability, severity, rationale, mitigations


__all__ = ["FinJudge"]
