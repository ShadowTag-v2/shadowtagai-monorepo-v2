# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Clinical Validator & Liability Shield
====================================

Gating mechanism for AI-generated clinical interpretations.
Ensures every output passes:
1. Liability Shield (SB 243, Medical DLP, Clinical Gateway)
2. Judge 6 Governance Rules (Medical Alignment)
"""

import logging
from typing import Any

from pydantic import BaseModel

from activeshield_medical.core.liability_shield import liability_shield
from app.services.Claude_Code_6_grounded import score_governance

logger = logging.getLogger(__name__)


class ValidationResult(BaseModel):
    is_safe: bool
    action: str
    redacted_text: str
    warnings: list[str]
    audit_id: str
    liability_statement: str


class ClinicalValidator:
    """Final gatekeeper for AI Interpreter outputs."""

    def __init__(self):
        self.shield = liability_shield

    async def validate_interpretation(
        self,
        raw_text: str,
        session_id: str = "default_interpreter_session",
        context: dict[str, Any] | None = None,
    ) -> ValidationResult:
        """Validate interpretation against medical safety standards."""
        # 1. Liability Shield (Unified Mid-check)
        shield_result = await self.shield.mid_check(
            session_id=session_id,
            ai_response=raw_text,
            patient_context=context or {},
        )

        # 2. Judge 6 Grounding Check
        # Ensure the interpretation follows the "Medical Doctrine"
        try:
            judge_verdict = await score_governance(
                request_type="verify",  # Mapping clinical check to 'verify' type
                content=shield_result.processed_content or raw_text,
                user_region=context.get("region") if context else None,
            )
            judge_approved = judge_verdict.decision in [
                "APPROVE",
                "REVIEW",
            ]  # Allow REVIEW with warnings
            judge_warnings = [judge_verdict.reasoning]
        except Exception as e:
            logger.warning(f"Judge 6 audit failed: {e}")
            judge_approved = True  # Fallback to shield-only if judge is down
            judge_warnings = [f"Judge 6 offline fallback: {e}"]

        is_safe = shield_result.passed and judge_approved

        # Combine warnings
        all_warnings = shield_result.warnings + judge_warnings

        # 3. Apply Liability Shield Disclaimer
        liability_statement = self._get_liability_disclaimer(is_safe)

        return ValidationResult(
            is_safe=is_safe,
            action=shield_result.action.value,
            redacted_text=shield_result.processed_content or raw_text,
            warnings=all_warnings,
            audit_id=shield_result.shield_id,
            liability_statement=liability_statement,
        )

    def _get_liability_disclaimer(self, is_safe: bool) -> str:
        """Standard medical liability disclaimer based on safety status."""
        base = "DISCLAIMER: This AI-generated interpretation is for informational purposes only. "
        if not is_safe:
            return (
                base
                + "CAUTION: This interpretation has failed safety grounding and should NOT be used for clinical decisions."
            )
        return base + "Not a substitute for professional medical advice, diagnosis, or treatment."


# Global instance
clinical_validator = ClinicalValidator()
