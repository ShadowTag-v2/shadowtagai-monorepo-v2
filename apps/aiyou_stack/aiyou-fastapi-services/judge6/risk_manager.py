# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""YRM: Your Risk Manager - ATP 5-19 Risk Assessment & Stratification

Implements military-grade risk classification and constitutional
axiom validation for AI governance.
"""

import logging

from Claude_Code_6.config import get_config
from Claude_Code_6.models import ConstitutionalAxiom, RiskLevel

logger = logging.getLogger(__name__)


class RiskAssessmentError(Exception):
    """Raised when risk assessment fails."""


class AxiomValidationError(Exception):
    """Raised when axiom validation fails."""


class YourRiskManager:
    """ATP 5-19 Risk Assessment & Stratification Engine

    Provides deterministic, rule-based risk classification according
    to military operational security standards.
    """

    def __init__(self):
        """Initialize risk manager with configuration."""
        config = get_config()
        self.ra_patterns = {
            RiskLevel.RA_4: config.risk_patterns.RA_4_PATTERNS,
            RiskLevel.RA_3: config.risk_patterns.RA_3_PATTERNS,
            RiskLevel.RA_2: config.risk_patterns.RA_2_PATTERNS,
        }
        self.axiom_config = config.axiom_validation
        logger.info("YourRiskManager initialized with %d risk levels", len(self.ra_patterns))

    def classify_request(self, user_input: str) -> RiskLevel:
        """Classify request using ATP 5-19 risk stratification.

        Performs hierarchical risk assessment from most severe (RA-4)
        to least severe (RA-1).

        Args:
            user_input: User request to classify

        Returns:
            RiskLevel: Assessed risk level

        Raises:
            RiskAssessmentError: If classification fails

        """
        if not user_input:
            raise RiskAssessmentError("Cannot classify empty input")

        try:
            input_lower = user_input.lower()

            # Check RA-4 first (most severe - catastrophic)
            for pattern in self.ra_patterns[RiskLevel.RA_4]:
                if pattern in input_lower:
                    logger.warning("RA-4 pattern detected: %s", pattern)
                    return RiskLevel.RA_4

            # Check RA-3 (moderate - significant impact)
            for pattern in self.ra_patterns[RiskLevel.RA_3]:
                if pattern in input_lower:
                    logger.info("RA-3 pattern detected: %s", pattern)
                    return RiskLevel.RA_3

            # Check RA-2 (low - limited impact)
            for pattern in self.ra_patterns[RiskLevel.RA_2]:
                if pattern in input_lower:
                    logger.debug("RA-2 pattern detected: %s", pattern)
                    return RiskLevel.RA_2

            # Default to RA-1 (negligible)
            logger.debug("No risk patterns detected, classified as RA-1")
            return RiskLevel.RA_1

        except Exception as e:
            raise RiskAssessmentError(f"Risk classification failed: {e!s}") from e

    def assess_axiom_violations(
        self,
        user_input: str,
        axioms: list[ConstitutionalAxiom],
    ) -> list[ConstitutionalAxiom]:
        """Check for constitutional axiom violations.

        Args:
            user_input: User request to validate
            axioms: List of axioms to check

        Returns:
            List of violated axioms

        Raises:
            AxiomValidationError: If validation fails

        """
        if not user_input:
            raise AxiomValidationError("Cannot validate empty input")

        if not axioms:
            raise AxiomValidationError("No axioms provided for validation")

        violations: list[ConstitutionalAxiom] = []

        try:
            for axiom in axioms:
                if self._violates_axiom(user_input, axiom):
                    violations.append(axiom)
                    logger.warning("Axiom violation detected: %s (%s)", axiom.axiom_id, axiom.name)

            logger.info("Axiom validation complete: %d violations found", len(violations))
            return violations

        except Exception as e:
            raise AxiomValidationError(f"Axiom validation failed: {e!s}") from e

    def _violates_axiom(self, user_input: str, axiom: ConstitutionalAxiom) -> bool:
        """Check if input violates specific axiom.

        Args:
            user_input: User request to check
            axiom: Constitutional axiom to validate against

        Returns:
            True if axiom is violated, False otherwise

        """
        input_lower = user_input.lower()

        if axiom.axiom_id == "A1":  # PURPOSE_REQUIRED
            return self._check_purpose_required(input_lower)

        if axiom.axiom_id == "A2":  # HARM_PROHIBITION
            return self._check_harm_prohibition(input_lower)

        if axiom.axiom_id == "A6":  # NO_USER_OVERRIDE
            return self._check_no_user_override(input_lower)

        # Other axioms (A3, A4, A5) are enforced at system level,
        # not user input level
        return False

    def _check_purpose_required(self, input_lower: str) -> bool:
        """Check if purpose declaration is missing."""
        return not any(
            indicator in input_lower for indicator in self.axiom_config.PURPOSE_INDICATORS
        )

    def _check_harm_prohibition(self, input_lower: str) -> bool:
        """Check for harm-related content."""
        return any(pattern in input_lower for pattern in self.axiom_config.HARM_PATTERNS)

    def _check_no_user_override(self, input_lower: str) -> bool:
        """Check for attempts to override governance rules."""
        return any(pattern in input_lower for pattern in self.axiom_config.OVERRIDE_PATTERNS)

    def get_risk_threshold(self, risk_level: RiskLevel) -> float:
        """Get confidence threshold for risk level.

        Args:
            risk_level: Risk level to get threshold for

        Returns:
            Confidence threshold (0.0 to 1.0)

        """
        thresholds = {
            RiskLevel.RA_1: 0.0,
            RiskLevel.RA_2: 0.3,
            RiskLevel.RA_3: 0.6,
            RiskLevel.RA_4: 0.9,
        }
        return thresholds.get(risk_level, 0.0)
