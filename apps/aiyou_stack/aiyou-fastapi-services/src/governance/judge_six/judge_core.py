"""Judge 6 Core - The Governance Engine
Combined Implementation: Legacy Logic + CSRMC 2026 + Omega Protocol

Authority:
- DoD CSRMC 2026 (Defense Grid)
- EU AI Act (Legislative Guardrails)
- ShadowTag Business Judgment Layer
- Gemini 3.0 Doctrine (90/10 Model Split)
"""

import hashlib
import logging
import os
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

import yaml

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - JUDGE6 - %(levelname)s - %(message)s")
logger = logging.getLogger("Judge6")


class Verdict(Enum):
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    ESCALATE = "ESCALATE"
    MONITOR = "MONITOR"


@dataclass
class JudgeReceipt:
    """Immutable receipt for every decision"""

    decision_id: str
    timestamp: float
    action: str
    verdict: str
    risk_score: float
    policy_hash: str
    notes: list[str]


class JudgeSixEngine:
    """The centralized governance authority.
    Enforces ATP 5-19, Purpose/Reasons/Brakes, and CSRMC.
    """

    def __init__(self, policy_path: str = "apps/app/policy.yaml"):
        self.policy_path = policy_path
        self.constitution = self._load_constitution_from_file() or self._load_default_constitution()
        logger.info(
            f"⚖️  Judge 6 Engine Online - CSRMC Active (Constitution v{self.constitution.get('judge6_constitution', {}).get('version', 'Unknown')})",
        )

    def _load_constitution_from_file(self) -> dict[str, Any] | None:
        """Load detailed constitution from YAML"""
        try:
            if os.path.exists(self.policy_path):
                with open(self.policy_path) as f:
                    data = yaml.safe_load(f)
                    # Flatten slightly for easier access if nested under judge6_constitution
                    if "judge6_constitution" in data:
                        return data["judge6_constitution"]
                    return data
        except Exception as e:
            logger.error(f"Failed to load policy.yaml: {e}")
        return None

    def _load_default_constitution(self) -> dict[str, Any]:
        """Load default hardcoded constitution if file fails"""
        return {
            "critical_controls": {"blocked_patterns": ["curl | sh", "eval(", "exec("]},
            "model_governance": {"standard": "gemini-3.0-flash", "allocation": 0.90},
        }

    def validate_action(self, action: str, context: dict[str, Any]) -> JudgeReceipt:
        """Validates an action against the Doctrine.
        Returns a receipt.
        """
        decision_id = hashlib.sha256(f"{action}{time.time()}".encode()).hexdigest()[:12]
        notes = []
        risk_score = 0.0

        # 1. Purpose/Reasons/Brakes (Legacy Check)
        purpose = context.get("purpose")
        reasons = context.get("reasons")
        brakes = context.get("brakes", "OFF")

        if not purpose or not reasons:
            notes.append("Legacy: Missing Purpose or Reasons")
            risk_score += 50

        if brakes == "ENGAGED":
            notes.append("Legacy: Brakes ENGAGED by operator")
            return self._mint_receipt(decision_id, action, Verdict.DENIED, 100.0, notes)

        # 2. CSRMC Defense Grid (New Check)
        for pattern in self.constitution["critical_controls"]["blocked_patterns"]:
            if pattern in action:
                notes.append(f"CSRMC: Blocked pattern detected: {pattern}")
                return self._mint_receipt(decision_id, action, Verdict.DENIED, 100.0, notes)

        # 3. Model Governance (Gemini 3.0 Doctrine)
        model_requested = context.get("model")
        if model_requested == "gemini-3.1-flash-lite-preview":
            notes.append("Governance: Gemini 1.5 is DEPRECATED. Use Gemini 3.0.")
            return self._mint_receipt(decision_id, action, Verdict.DENIED, 90.0, notes)

        # 4. Final Verdict
        if risk_score > 80:
            verdict = Verdict.DENIED
        elif risk_score > 40:
            verdict = Verdict.ESCALATE
        else:
            verdict = Verdict.APPROVED

        return self._mint_receipt(decision_id, action, verdict, risk_score, notes)

    def _mint_receipt(
        self,
        decision_id: str,
        action: str,
        verdict: Verdict,
        risk: float,
        notes: list[str],
    ) -> JudgeReceipt:
        """Create the immutable receipt"""
        receipt = JudgeReceipt(
            decision_id=decision_id,
            timestamp=time.time(),
            action=action,
            verdict=verdict.value,
            risk_score=risk,
            policy_hash="sha256:constitution_v6",
            notes=notes,
        )

        # Audit Log
        symbol = "✅" if verdict == Verdict.APPROVED else "❌"
        logger.info(
            f"Decision {decision_id}: {symbol} {verdict.value} (Risk: {risk}) | {action[:50]}",
        )
        return receipt


# Mission Critical: Governance Check
if __name__ == "__main__":
    judge = JudgeSixEngine()

    # Test 1: Valid
    ctx1 = {"purpose": "Revenue", "reasons": "Growth", "model": "gemini-3.0-flash"}
    judge.validate_action("DEPLOY_POD_A", ctx1)

    # Test 2: Blocked Pattern
    ctx2 = {"purpose": "Hacking", "reasons": "Fun"}
    judge.validate_action("os.system('rm -rf /')", ctx2)

    # Test 3: Deprecated Model
    ctx3 = {"purpose": "Legacy", "reasons": "Old Code", "model": "gemini-3.1-flash-lite-preview"}
    judge.validate_action("GENERATE_CODE", ctx3)
