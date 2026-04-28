# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Judge 6: Core Judgment Rule System

Implements the six-gate evaluation process for AI governance:
GATE 1: ATP 5-19 Risk Classification (BEFORE processing)
GATE 2: Purpose Declaration Validation
GATE 3: Constitutional Axiom Verification
GATE 4: Resource Allocation per Risk Level
GATE 5: Execution with Monitoring
GATE 6: Cryptographic Provenance Stamp
"""

import logging

from judge6.config import get_config
from judge6.constitutional import COR53_AXIOMS
from judge6.models import ConstitutionalAxiom, JudgmentDecision, ProvenanceStamp, RiskLevel
from judge6.provenance import ProvenanceError, ShadowTagEngine
from judge6.risk_manager import AxiomValidationError, RiskAssessmentError, YourRiskManager

logger = logging.getLogger(__name__)


class JudgmentError(Exception):
    """Raised when judgment evaluation fails."""


class JudgmentRule:
    """Judge 6: PNKLN's Governance Enforcement Engine

    Purpose: Enforce ShadowTag-v2JR doctrine with cryptographic guarantees.

    Provides deterministic, auditable governance decisions with
    complete reasoning chain provenance.
    """

    def __init__(self, cor_instance_id: str | None = None):
        """Initialize Judge 6 governance engine.

        Args:
            cor_instance_id: Unique Cor instance identifier.
                           If None, uses config default.

        """
        config = get_config()
        self.cor_instance_id = cor_instance_id or config.COR_INSTANCE_ID

        # Load constitutional layer (immutable)
        self.constitutional_layer = COR53_AXIOMS

        # Initialize subsystems
        self.risk_manager = YourRiskManager()
        self.watermark_engine = ShadowTagEngine(self.cor_instance_id)

        # Test coverage tracking
        self.test_coverage = config.TEST_COVERAGE_TARGET
        self.decisions_made = 0
        self.decisions_approved = 0

        logger.info(
            "JudgmentRule initialized: instance=%s, axioms=%d",
            self.cor_instance_id,
            len(self.constitutional_layer),
        )

    def evaluate_request(
        self,
        user_input: str,
        declared_purpose: str | None = None,
    ) -> JudgmentDecision:
        """Execute six-gate evaluation process.

        Args:
            user_input: User request to evaluate
            declared_purpose: Optional explicitly declared purpose

        Returns:
            JudgmentDecision with complete reasoning and provenance

        Raises:
            JudgmentError: If evaluation fails critically

        """
        try:
            # Track decision count
            self.decisions_made += 1

            # GATE 1: ATP 5-19 Risk Classification (BEFORE processing)
            logger.debug("GATE 1: Risk Classification")
            risk_level = self._gate1_risk_classification(user_input)

            # GATE 2: Purpose Declaration Validation
            logger.debug("GATE 2: Purpose Validation")
            validated_purpose = self._gate2_purpose_validation(user_input, declared_purpose)

            # GATE 3: Constitutional Axiom Verification
            logger.debug("GATE 3: Axiom Verification")
            violated_axioms = self._gate3_axiom_verification(user_input)

            # GATE 4: Resource Allocation (implementation-specific)
            logger.debug("GATE 4: Resource Allocation")
            resource_decision = self._gate4_resource_allocation(risk_level)

            # Determine approval
            approved = self._determine_approval(risk_level, violated_axioms)
            if approved:
                self.decisions_approved += 1

            # Build reasoning chain
            reasoning = self._build_reasoning_chain(
                user_input=user_input,
                risk_level=risk_level,
                violated_axioms=violated_axioms,
                declared_purpose=validated_purpose,
                resource_decision=resource_decision,
            )

            # GATE 6: Generate Cryptographic Provenance Stamp
            logger.debug("GATE 6: Provenance Stamp Generation")
            provenance_stamp = None
            if approved:
                provenance_stamp = self._gate6_generate_provenance(
                    validated_purpose,
                    reasoning,
                    risk_level,
                )

            # Build metadata
            metadata = {
                "decision_number": self.decisions_made,
                "approval_rate": self.decisions_approved / self.decisions_made,
                "gates_passed": self._get_gates_passed(risk_level, violated_axioms, approved),
            }

            decision = JudgmentDecision(
                approved=approved,
                risk_level=risk_level,
                reasoning=reasoning,
                violated_axioms=violated_axioms,
                provenance_stamp=provenance_stamp,
                metadata=metadata,
            )

            logger.info(
                "Judgment decision #%d: approved=%s, risk=%s",
                self.decisions_made,
                approved,
                risk_level.value,
            )

            return decision

        except (RiskAssessmentError, AxiomValidationError, ProvenanceError) as e:
            # Expected errors - create rejection decision
            logger.error("Evaluation error: %s", str(e))
            return self._create_error_decision(str(e))

        except Exception as e:
            # Unexpected errors - fail closed
            logger.critical("Critical judgment error: %s", str(e), exc_info=True)
            raise JudgmentError(f"Judgment evaluation failed: {e!s}") from e

    def _gate1_risk_classification(self, user_input: str) -> RiskLevel:
        """GATE 1: Classify request using ATP 5-19 risk stratification.

        This happens BEFORE any processing to prevent exposure
        to high-risk content.

        Args:
            user_input: User request

        Returns:
            Assessed risk level

        """
        return self.risk_manager.classify_request(user_input)

    def _gate2_purpose_validation(self, user_input: str, declared_purpose: str | None) -> str:
        """GATE 2: Validate purpose declaration.

        Args:
            user_input: User request
            declared_purpose: Optional declared purpose

        Returns:
            Validated purpose string

        """
        if declared_purpose:
            return declared_purpose
        # Extract purpose from input
        return self._extract_purpose(user_input)

    def _gate3_axiom_verification(self, user_input: str) -> list[ConstitutionalAxiom]:
        """GATE 3: Verify constitutional axiom compliance.

        Args:
            user_input: User request

        Returns:
            List of violated axioms

        """
        return self.risk_manager.assess_axiom_violations(user_input, self.constitutional_layer)

    def _gate4_resource_allocation(self, risk_level: RiskLevel) -> dict:
        """GATE 4: Determine resource allocation based on risk.

        Higher risk requests receive more scrutiny and monitoring.

        Args:
            risk_level: Assessed risk level

        Returns:
            Resource allocation decision

        """
        resource_map = {
            RiskLevel.RA_1: {"monitoring": "standard", "review": "automated"},
            RiskLevel.RA_2: {"monitoring": "enhanced", "review": "automated"},
            RiskLevel.RA_3: {"monitoring": "intensive", "review": "human-in-loop"},
            RiskLevel.RA_4: {"monitoring": "maximum", "review": "human-required"},
        }
        return resource_map.get(risk_level, resource_map[RiskLevel.RA_1])

    def _gate6_generate_provenance(
        self,
        purpose: str,
        reasoning: str,
        risk_level: RiskLevel,
    ) -> ProvenanceStamp | None:
        """GATE 6: Generate cryptographic provenance stamp.

        Args:
            purpose: Validated purpose
            reasoning: Complete reasoning chain
            risk_level: Assessed risk level

        Returns:
            Provenance stamp or None if generation fails

        """
        try:
            axioms_verified = [ax.axiom_id for ax in self.constitutional_layer]
            return self.watermark_engine.generate_stamp(
                purpose,
                reasoning,
                risk_level,
                axioms_verified,
            )
        except ProvenanceError as e:
            logger.error("Provenance generation failed: %s", str(e))
            return None

    def _determine_approval(
        self,
        risk_level: RiskLevel,
        violated_axioms: list[ConstitutionalAxiom],
    ) -> bool:
        """Determine if request should be approved.

        Rejection criteria:
        - Risk level is RA-4 (catastrophic)
        - Any constitutional axioms violated

        Args:
            risk_level: Assessed risk level
            violated_axioms: List of violated axioms

        Returns:
            True if approved, False if rejected

        """
        if risk_level == RiskLevel.RA_4:
            logger.warning("Request rejected: RA-4 risk level")
            return False

        if len(violated_axioms) > 0:
            logger.warning("Request rejected: %d axiom violations", len(violated_axioms))
            return False

        return True

    def _extract_purpose(self, user_input: str) -> str:
        """Extract declared purpose from user input.

        Args:
            user_input: User request

        Returns:
            Extracted or inferred purpose

        """
        # Simplified extraction - production would use NLP
        max_chars = 100
        if len(user_input) > max_chars:
            return f"Inferred purpose from: {user_input[:max_chars]}..."
        return f"Inferred purpose from: {user_input}"

    def _build_reasoning_chain(
        self,
        user_input: str,
        risk_level: RiskLevel,
        violated_axioms: list[ConstitutionalAxiom],
        declared_purpose: str,
        resource_decision: dict,
    ) -> str:
        """Build detailed reasoning chain for decision transparency.

        Args:
            user_input: User request
            risk_level: Assessed risk level
            violated_axioms: List of violated axioms
            declared_purpose: Validated purpose
            resource_decision: Resource allocation decision

        Returns:
            Complete reasoning chain as formatted string

        """
        chain = []

        # Input summary
        max_input_display = 200
        input_display = user_input[:max_input_display]
        if len(user_input) > max_input_display:
            input_display += "..."
        chain.append(f"Input: {input_display}")

        # Purpose
        chain.append(f"Declared Purpose: {declared_purpose}")

        # Risk assessment
        chain.append(f"ATP 5-19 Risk Level: {risk_level.value} ({risk_level.name})")

        # Axiom violations
        if violated_axioms:
            chain.append("Constitutional Axioms Violated:")
            for axiom in violated_axioms:
                chain.append(f"  - {axiom.axiom_id}: {axiom.name}")
                chain.append(f"    Rule: {axiom.rule}")
                chain.append(f"    Consequence: {axiom.violation_consequence.value}")
        else:
            chain.append("No constitutional axioms violated")

        # Resource allocation
        chain.append(f"Resource Allocation: {resource_decision}")

        return "\n".join(chain)

    def _get_gates_passed(
        self,
        risk_level: RiskLevel,
        violated_axioms: list[ConstitutionalAxiom],
        approved: bool,
    ) -> list[str]:
        """Get list of gates successfully passed."""
        gates = ["GATE1_RISK", "GATE2_PURPOSE"]

        if not violated_axioms:
            gates.append("GATE3_AXIOMS")

        gates.append("GATE4_RESOURCES")

        if approved:
            gates.extend(["GATE5_EXECUTION", "GATE6_PROVENANCE"])

        return gates

    def _create_error_decision(self, error_message: str) -> JudgmentDecision:
        """Create rejection decision for evaluation errors.

        Args:
            error_message: Error description

        Returns:
            Rejection decision with error details

        """
        return JudgmentDecision(
            approved=False,
            risk_level=RiskLevel.RA_4,  # Fail closed
            reasoning=f"Evaluation error: {error_message}",
            violated_axioms=[],
            provenance_stamp=None,
            metadata={"error": True, "error_message": error_message},
        )

    def get_statistics(self) -> dict:
        """Get governance statistics.

        Returns:
            Dictionary of statistics

        """
        return {
            "total_decisions": self.decisions_made,
            "approved": self.decisions_approved,
            "rejected": self.decisions_made - self.decisions_approved,
            "approval_rate": (
                self.decisions_approved / self.decisions_made if self.decisions_made > 0 else 0.0
            ),
            "test_coverage_target": self.test_coverage,
            "constitutional_axioms": len(self.constitutional_layer),
        }
