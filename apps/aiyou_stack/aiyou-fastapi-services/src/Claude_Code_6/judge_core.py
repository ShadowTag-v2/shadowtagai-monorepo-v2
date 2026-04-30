# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Judge 6 Core - Governance Engine
Target Valuation: $35.0B
Purpose / Reasons / Brakes
"""

import logging
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class Verdict(Enum):
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    ESCALATE = "ESCALATE"


class JudgeSix:
    """The centralized governance authority.
    Enforces ATP 5-19 and Purpose/Reasons/Brakes.
    Includes Claude Code BLOCK/ALLOW rule engine with User Intent override.
    """

    @staticmethod
    def _evaluate_block_allow(action: str, context: dict[str, Any]) -> Verdict:
        user_intent = context.get("user_intent", False)

        # User Intent Override (Highest Precedence)
        if user_intent:
            logger.info("BLOCK/ALLOW: User Intent Override active. Action permitted.")
            return Verdict.APPROVED

        # Memory Poisoning Detection
        if "write" in action.lower() and "permission" in str(context).lower():
            logger.warning("BLOCK/ALLOW: Memory Poisoning attempt detected.")
            return Verdict.DENIED

        # Sub-agent Delegation Attack
        if "spawn" in action.lower() and "block" in str(context).lower():
            logger.warning("BLOCK/ALLOW: Sub-agent delegation attack detected.")
            return Verdict.DENIED

        # Shared Infra Bias
        if "cloud" in action.lower() or "cluster" in action.lower():
            if not context.get("infra_approved"):
                logger.warning("BLOCK/ALLOW: Shared Infra target without approval.")
                return Verdict.DENIED

        # Composite Action Decomposition
        if "&&" in action or ";" in action:
            logger.info("BLOCK/ALLOW: Composite action detected, needs decomposition.")
            # For simplicity, if we detect chained commands, we escalate or deny
            return Verdict.ESCALATE

        # Written File Execution
        if "execute_written" in action.lower():
            logger.warning("BLOCK/ALLOW: Written file execution requires explicit ALLOW.")
            return Verdict.DENIED

        return Verdict.APPROVED

    @staticmethod
    def validate_action(action: str, context: dict[str, Any]) -> Verdict:
        """Validates an action against the Doctrine."""
        purpose = context.get("purpose")
        reasons = context.get("reasons")
        brakes = context.get("brakes")

        if not purpose or not reasons:
            logger.error(f"Action {action} denied: Missing Purpose or Reasons.")
            return Verdict.DENIED

        if brakes == "ENGAGED":
            logger.warning(f"Action {action} halted: Brakes engaged.")
            return Verdict.DENIED

        # Evaluate BLOCK/ALLOW Engine
        rule_verdict = JudgeSix._evaluate_block_allow(action, context)
        if rule_verdict != Verdict.APPROVED:
            return rule_verdict

        logger.info(f"Action {action} APPROVED by Judge 6.")
        return Verdict.APPROVED

    @staticmethod
    def audit_trail(decision_id: str, verdict: Verdict):
        """Logs decision to immutable ledger (Elasticsearch/Log)."""
        # TODO: Push to Elasticsearch


# Mission Critical: Governance Check
if __name__ == "__main__":
    ctx = {"purpose": "Revenue", "reasons": "Sustainability", "brakes": "OFF"}
    print(JudgeSix.validate_action("DEPLOY_SKYNODE", ctx))
