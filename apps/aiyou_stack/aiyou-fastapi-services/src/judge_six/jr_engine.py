"""JR Engine - Purpose/Reasons/Brakes Validation Framework
Core orchestration for Judge #6
"""

import time

from .models import Action, JRVerdict, VerdictStatus
from .validators import BrakesValidator, PurposeValidator, ReasonsValidator


class JREngine:
    """JR Engine orchestrates Purpose/Reasons/Brakes validation

    Philosophy:
    - PURPOSE: What is this trying to accomplish?
    - REASONS: Why is this action justified?
    - BRAKES: What could go wrong?
    """

    def __init__(self):
        self.purpose_validator = PurposeValidator()
        self.reasons_validator = ReasonsValidator()
        self.brakes_validator = BrakesValidator()

    def validate(self, action: Action, policy_id: str | None = None) -> JRVerdict:
        """Run full JR validation pipeline
        """
        time.time()

        # 1. Validate Purpose
        purpose = self.purpose_validator.validate(action)

        # 2. Validate Reasons
        reasons = self.reasons_validator.validate(action)

        # 3. Validate Brakes (Risks)
        brakes = self.brakes_validator.validate(action)

        # 4. Determine Overall Verdict
        status = VerdictStatus.APPROVED
        confidence = 1.0
        summary = "Action approved."

        # Logic: Usage of Brakes is a hard stop
        if brakes.status == VerdictStatus.REJECTED:
            status = VerdictStatus.REJECTED
            summary = f"REJECTED: {brakes.explanation}"
            confidence = 0.95
        elif purpose.status == VerdictStatus.REJECTED:
            status = VerdictStatus.REJECTED
            summary = f"REJECTED: {purpose.explanation}"
            confidence = 0.90
        elif reasons.status == VerdictStatus.REJECTED:
            status = VerdictStatus.REJECTED
            summary = f"REJECTED: {reasons.explanation}"
            confidence = 0.85
        elif any(v.status == VerdictStatus.FLAGGED for v in [purpose, reasons, brakes]):
            status = VerdictStatus.FLAGGED
            summary = "FLAGGED: Risks or weaknesses detected."
            confidence = 0.80

        return JRVerdict(
            id=f"jr_{int(time.time())}",
            action_id=action.id,
            timestamp=action.timestamp,
            status=status,
            confidence=confidence,
            purpose=purpose,
            reasons=reasons,
            brakes=brakes,
            policy_id=policy_id,
            summary=summary,
        )
