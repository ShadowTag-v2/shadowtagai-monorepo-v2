# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
JR Engine - Purpose/Reasons/Brakes Validation Framework
Core orchestration for Judge #6
"""

import time
from .models import Action, JRVerdict, VerdictStatus
from .validators import PurposeValidator, ReasonsValidator, BrakesValidator


class JREngine:
    """
    JR Engine orchestrates Purpose/Reasons/Brakes validation

    Philosophy:
    - PURPOSE: What is this trying to accomplish?
    - REASONS: Why is this action justified?
    - BRAKES: What could go wrong?

    An action must pass ALL three dimensions to be approved.
    """

    def __init__(
        self,
        purpose_validator: PurposeValidator | None = None,
        reasons_validator: ReasonsValidator | None = None,
        brakes_validator: BrakesValidator | None = None,
    ):
        """
        Initialize JR Engine with validators

        Args:
            purpose_validator: Custom PurposeValidator (optional)
            reasons_validator: Custom ReasonsValidator (optional)
            brakes_validator: Custom BrakesValidator (optional)
        """
        self.purpose_validator = purpose_validator or PurposeValidator()
        self.reasons_validator = reasons_validator or ReasonsValidator()
        self.brakes_validator = brakes_validator or BrakesValidator()

    def validate(self, action: Action) -> JRVerdict:
        """
        Validate an action through Purpose/Reasons/Brakes framework

        Args:
            action: The action to validate

        Returns:
            JRVerdict with comprehensive validation results
        """
        start_time = time.time()

        # Step 1: Validate PURPOSE
        purpose_verdict = self.purpose_validator.validate(action)

        # Step 2: Validate REASONS
        reasons_verdict = self.reasons_validator.validate(action)

        # Step 3: Validate BRAKES (risk detection)
        brakes_verdict = self.brakes_validator.validate(action)

        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000

        # Determine overall status
        overall_status = self._determine_overall_status(purpose_verdict, reasons_verdict, brakes_verdict)

        return JRVerdict(
            action_id=action.action_id,
            purpose=purpose_verdict,
            reasons=reasons_verdict,
            brakes=brakes_verdict,
            overall_status=overall_status,
            latency_ms=latency_ms,
            policy_ids=[],  # Populated by policy loader in production
        )

    def _determine_overall_status(self, purpose, reasons, brakes) -> VerdictStatus:
        """
        Determine overall verdict status based on all three dimensions

        Logic:
        1. If BRAKES blocked → REJECTED (safety first)
        2. If PURPOSE or REASONS rejected → REJECTED
        3. If any dimension requires review → REQUIRES_REVIEW
        4. If any dimension flagged → FLAGGED
        5. If all approved → APPROVED
        """
        # Safety first: If brakes blocked, reject immediately
        if brakes.blocked():
            return VerdictStatus.REJECTED

        # If PURPOSE or REASONS rejected, reject overall
        if purpose.status == VerdictStatus.REJECTED or reasons.status == VerdictStatus.REJECTED:
            return VerdictStatus.REJECTED

        # If any dimension requires review, overall requires review
        if (
            purpose.status == VerdictStatus.REQUIRES_REVIEW
            or reasons.status == VerdictStatus.REQUIRES_REVIEW
            or brakes.status == VerdictStatus.REQUIRES_REVIEW
        ):
            return VerdictStatus.REQUIRES_REVIEW

        # If any dimension flagged, overall flagged
        if purpose.status == VerdictStatus.FLAGGED or reasons.status == VerdictStatus.FLAGGED or brakes.status == VerdictStatus.FLAGGED:
            return VerdictStatus.FLAGGED

        # All approved
        return VerdictStatus.APPROVED

    def validate_batch(self, actions: list[Action]) -> list[JRVerdict]:
        """
        Validate multiple actions in batch

        Args:
            actions: List of actions to validate

        Returns:
            List of JRVerdicts
        """
        return [self.validate(action) for action in actions]

    def get_stats(self) -> dict:
        """
        Get engine statistics (for monitoring)

        Returns:
            Dictionary with engine stats
        """
        return {
            "engine_version": "1.0.0",
            "validators": {
                "purpose": self.purpose_validator.__class__.__name__,
                "reasons": self.reasons_validator.__class__.__name__,
                "brakes": self.brakes_validator.__class__.__name__,
            },
        }
