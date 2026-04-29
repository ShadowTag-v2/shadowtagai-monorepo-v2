# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Judge 6 Enforcement - ShadowTag-v2JR Doctrine Compliance & Gemini Integration

This module implements the Judge 6 enforcement layer from ShadowTag-v2JR doctrine:
1. Purpose, Reasons, Brakes (PRB) validation gates
2. Pre-flight task validation before execution
3. Doctrine violation detection and kill-switch enforcement
4. Gemini integration for secondary validation
5. Comprehensive audit trail generation

ShadowTag-v2JR Doctrine Gates:
- PURPOSE: Task must align with strategic objectives (30-vertical expansion, $0K bootstrap)
- REASONS: Justification must be sound and risk-assessed (ATP 5-19)
- BRAKES: Kill-switch criteria must be checked (RA-1 violations, doctrine breaches)

Violation Levels:
- V0: Compliant (no violations detected)
- V1: MINOR - Suboptimal approach, warning issued
- V2: MODERATE - Doctrine misalignment, requires review
- V3: MAJOR - Risk violation, task blocked pending approval
- V4: CRITICAL - Doctrine breach, immediate termination, audit triggered

Author: PNKLN Strategic Systems
Version: 1.0.0
"""

import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any

# Google Gemini imports
try:
    import google.generativeai as genai

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("Google Gemini not installed. Install with: pip install google-generativeai")

from cor_skill_registry import CORSkillRegistry, SkillMetadata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ViolationLevel(Enum):
    """Doctrine violation severity levels"""

    V0_COMPLIANT = "V0_COMPLIANT"
    V1_MINOR = "V1_MINOR"
    V2_MODERATE = "V2_MODERATE"
    V3_MAJOR = "V3_MAJOR"
    V4_CRITICAL = "V4_CRITICAL"


@dataclass
class ValidationResult:
    """Result of PRB validation"""

    is_valid: bool
    violation_level: ViolationLevel
    purpose_score: float  # 0.0 - 1.0
    reasons_score: float  # 0.0 - 1.0
    brakes_triggered: bool
    violations: list[str]
    recommendations: list[str]
    gemini_validation: dict[str, Any] | None
    audit_trail: dict[str, Any]
    timestamp: str


@dataclass
class DoctrineConstraints:
    """ShadowTag-v2JR doctrine constraints"""

    bootstrap_limit: int = 0  # $0K capital constraint
    vertical_target: int = 30  # 30-vertical expansion target
    max_execution_hours: int = 48  # Maximum task execution time
    required_watermark: bool = True  # ShadowTag watermarking required
    compliance_frameworks: list[str] = None  # e.g., ['HIPAA', 'SEC', 'FDA']

    def __post_init__(self):
        if self.compliance_frameworks is None:
            self.compliance_frameworks = ["HIPAA", "SEC", "FDA", "DoD"]


class PurposeGate:
    """PURPOSE validation gate - Strategic alignment check"""

    def __init__(self, doctrine: DoctrineConstraints):
        self.doctrine = doctrine

    def validate(self, task_description: str, context: dict[str, Any]) -> tuple[float, list[str]]:
        """Validate task aligns with strategic purpose

        Returns:
            tuple: (score, violations)

        """
        score = 1.0
        violations = []

        task_lower = task_description.lower()

        # Check for capital expenditure violations
        if any(keyword in task_lower for keyword in ["purchase", "buy", "subscribe", "pay"]):  # noqa: SIM102
            if context.get("cost_estimate", 0) > self.doctrine.bootstrap_limit:
                score -= 0.4
                violations.append(
                    f"Capital expenditure violates ${self.doctrine.bootstrap_limit}K bootstrap constraint",
                )

        # Check for strategic alignment with 30-vertical expansion
        strategic_keywords = ["healthcare", "gtm", "market", "vertical", "strategy", "expansion"]
        if not any(keyword in task_lower for keyword in strategic_keywords):
            score -= 0.2
            violations.append("Task may not align with 30-vertical expansion strategy")

        # Check for Doctrine-as-a-Service alignment
        doctrine_keywords = ["compliance", "enforcement", "doctrine", "validation", "audit"]
        if any(keyword in task_lower for keyword in doctrine_keywords):
            score += 0.1  # Bonus for doctrine-aligned work

        # Check for vertical market indicators
        vertical_markets = ["healthcare", "finance", "legal", "manufacturing", "education"]
        if any(market in task_lower for market in vertical_markets):
            score += 0.1  # Bonus for vertical-specific work

        return max(0.0, min(1.0, score)), violations


class ReasonsGate:
    """REASONS validation gate - Justification soundness check"""

    def __init__(self, skill_registry: CORSkillRegistry):
        self.skill_registry = skill_registry

    def validate(
        self,
        task_description: str,
        justification: str,
        risk_level: str,
    ) -> tuple[float, list[str]]:
        """Validate task justification is sound

        Returns:
            tuple: (score, violations)

        """
        score = 1.0
        violations = []

        # Check justification quality
        if not justification or len(justification) < 50:
            score -= 0.3
            violations.append("Insufficient justification (minimum 50 characters required)")

        # Check risk level acknowledgment
        if risk_level in ["RA-1", "RA-2"] and "risk" not in justification.lower():
            score -= 0.4
            violations.append("High-risk task lacks explicit risk acknowledgment in justification")

        # Check for required reasoning elements
        reasoning_elements = ["because", "therefore", "in order to", "enables", "necessary for"]
        if not any(element in justification.lower() for element in reasoning_elements):
            score -= 0.2
            violations.append("Justification lacks clear causal reasoning")

        # Check for benefit articulation
        benefit_keywords = ["improve", "enable", "accelerate", "reduce", "increase", "optimize"]
        if not any(keyword in justification.lower() for keyword in benefit_keywords):
            score -= 0.1
            violations.append("Justification should articulate clear benefits")

        return max(0.0, min(1.0, score)), violations


class BrakesGate:
    """BRAKES validation gate - Kill-switch criteria check"""

    def __init__(self, doctrine: DoctrineConstraints):
        self.doctrine = doctrine

    def validate(
        self,
        task_description: str,
        skill: SkillMetadata | None,
        context: dict[str, Any],
    ) -> tuple[bool, list[str]]:
        """Check if brakes should be triggered

        Returns:
            tuple: (brakes_triggered, violations)

        """
        brakes_triggered = False
        violations = []

        task_lower = task_description.lower()

        # BRAKE 1: Irreversible production operations
        irreversible_keywords = [
            "delete production",
            "drop database",
            "terminate production",
            "destroy",
            "irreversible",
        ]
        if any(keyword in task_lower for keyword in irreversible_keywords):
            brakes_triggered = True
            violations.append("BRAKE TRIGGERED: Irreversible production operation detected")

        # BRAKE 2: RA-1 violations without approval
        if skill and skill.risk_level == "RA-1" and not context.get("ra1_approval", False):
            brakes_triggered = True
            violations.append("BRAKE TRIGGERED: RA-1 operation requires explicit approval")

        # BRAKE 3: Compliance framework violations
        compliance_violations = []
        if "patient data" in task_lower and "HIPAA" in self.doctrine.compliance_frameworks:  # noqa: SIM102
            if not context.get("hipaa_compliant", False):
                compliance_violations.append("HIPAA")

        if "financial transaction" in task_lower and "SEC" in self.doctrine.compliance_frameworks:  # noqa: SIM102
            if not context.get("sec_compliant", False):
                compliance_violations.append("SEC")

        if compliance_violations:
            brakes_triggered = True
            violations.append(
                f"BRAKE TRIGGERED: Compliance violations: {', '.join(compliance_violations)}",
            )

        # BRAKE 4: Execution time exceeds doctrine limits
        estimated_hours = context.get("estimated_hours", 0)
        if estimated_hours > self.doctrine.max_execution_hours:
            brakes_triggered = True
            violations.append(
                f"BRAKE TRIGGERED: Estimated execution time ({estimated_hours}h) exceeds limit ({self.doctrine.max_execution_hours}h)",
            )

        # BRAKE 5: Missing watermark requirement
        if self.doctrine.required_watermark and not context.get("watermark_enabled", True):
            brakes_triggered = True
            violations.append("BRAKE TRIGGERED: ShadowTag watermarking required but disabled")

        return brakes_triggered, violations


class GeminiValidator:
    """Google Gemini secondary validation layer"""

    def __init__(self, api_key: str | None = None):
        """Initialize Gemini validator

        Args:
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)

        """
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")

        if GEMINI_AVAILABLE and self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(
                "gemini-3.1-flash-lite-preview", tools="code_execution"
            )
            self.enabled = True
            logger.info("Gemini validator initialized")
        else:
            self.enabled = False
            logger.warning("Gemini validator disabled (API key missing or package not installed)")

    def validate_task(
        self,
        task_description: str,
        justification: str,
        risk_level: str,
    ) -> dict[str, Any] | None:
        """Perform secondary validation using Gemini

        Returns:
            Validation results or None if Gemini unavailable

        """
        if not self.enabled:
            return None

        try:
            prompt = f"""Analyze this task for ShadowTag-v2JR doctrine compliance:

Task: {task_description}
Justification: {justification}
Risk Level: {risk_level}

Evaluate on a scale of 0-10:
1. Strategic alignment (does this advance 30-vertical expansion?)
2. Risk justification quality (is the risk/benefit analysis sound?)
3. Compliance risk (any regulatory red flags?)

Provide scores and brief rationale. Format response as JSON:
{{
  "strategic_alignment": <score>,
  "justification_quality": <score>,
  "compliance_risk": <score>,
  "rationale": "<brief explanation>",
  "recommendation": "APPROVE|REVIEW|REJECT"
}}"""

            response = self.model.generate_content(prompt)
            result_text = response.text

            # Parse JSON response
            # Remove markdown code blocks if present
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]

            result = json.loads(result_text.strip())

            logger.info(f"Gemini validation: {result['recommendation']}")
            return result

        except Exception as e:
            logger.error(f"Gemini validation failed: {e}")
            return {
                "error": str(e),
                "recommendation": "REVIEW",  # Fail-safe to manual review
            }


class Cor.Claude_Code_6Enforcer:
    """Judge 6 Enforcement Engine - Complete PRB validation and enforcement"""

    def __init__(
        self,
        api_key: str | None = None,
        gemini_api_key: str | None = None,
        doctrine: DoctrineConstraints | None = None,
    ):
        """Initialize Judge 6 Enforcer

        Args:
            api_key: Anthropic API key
            gemini_api_key: Google API key for Gemini
            doctrine: Doctrine constraints (uses defaults if not provided)

        """
        self.doctrine = doctrine or DoctrineConstraints()
        self.skill_registry = CORSkillRegistry(api_key=api_key)
        self.skill_registry.discover_skills()

        # Initialize validation gates
        self.purpose_gate = PurposeGate(self.doctrine)
        self.reasons_gate = ReasonsGate(self.skill_registry)
        self.brakes_gate = BrakesGate(self.doctrine)

        # Initialize Gemini validator
        self.gemini_validator = GeminiValidator(api_key=gemini_api_key)

        self.audit_log: list[ValidationResult] = []

        logger.info("Judge 6 Enforcer initialized with PRB gates")

    def validate_task(
        self,
        task_description: str,
        justification: str = "",
        context: dict[str, Any] | None = None,
    ) -> ValidationResult:
        """Perform complete PRB validation on a task

        Args:
            task_description: Task to validate
            justification: Task justification
            context: Additional context (cost_estimate, risk_level, etc.)

        Returns:
            ValidationResult with enforcement decision

        """
        context = context or {}
        violations = []
        recommendations = []

        logger.info(f"Judge 6 validating task: {task_description[:50]}...")

        # Determine skill and risk level
        from cor_autogen_integration import SkillRouter

        router = SkillRouter(self.skill_registry)
        skill = router.route_task(task_description)
        risk_level = skill.risk_level if skill else "RA-4"

        # GATE 1: PURPOSE validation
        purpose_score, purpose_violations = self.purpose_gate.validate(task_description, context)
        violations.extend(purpose_violations)

        # GATE 2: REASONS validation
        reasons_score, reasons_violations = self.reasons_gate.validate(
            task_description,
            justification,
            risk_level,
        )
        violations.extend(reasons_violations)

        # GATE 3: BRAKES check
        brakes_triggered, brakes_violations = self.brakes_gate.validate(
            task_description,
            skill,
            context,
        )
        violations.extend(brakes_violations)

        # GATE 4: Gemini secondary validation (if enabled)
        gemini_result = None
        if self.gemini_validator.enabled:
            gemini_result = self.gemini_validator.validate_task(
                task_description,
                justification,
                risk_level,
            )

            if gemini_result and gemini_result.get("recommendation") == "REJECT":
                violations.append(
                    f"Gemini validation rejected: {gemini_result.get('rationale', 'No rationale')}",
                )

        # Determine overall validation result
        is_valid = True
        violation_level = ViolationLevel.V0_COMPLIANT

        if brakes_triggered:
            is_valid = False
            violation_level = ViolationLevel.V4_CRITICAL
            recommendations.append("IMMEDIATE ACTION: Task execution blocked by kill-switch")
            recommendations.append("Requires manual override approval from doctrine administrator")

        elif len(violations) > 3 or purpose_score < 0.5 or reasons_score < 0.5:
            is_valid = False
            violation_level = ViolationLevel.V3_MAJOR
            recommendations.append("Task blocked pending review and approval")
            recommendations.append("Improve justification and address violations")

        elif len(violations) > 1:
            violation_level = ViolationLevel.V2_MODERATE
            recommendations.append("Task execution allowed with monitoring")
            recommendations.append("Address violations in next iteration")

        elif len(violations) == 1:
            violation_level = ViolationLevel.V1_MINOR
            recommendations.append("Task execution approved with minor warnings")

        # Generate audit trail
        audit_trail = {
            "task_description": task_description,
            "justification": justification,
            "context": context,
            "skill_matched": skill.name if skill else None,
            "risk_level": risk_level,
            "purpose_score": purpose_score,
            "reasons_score": reasons_score,
            "brakes_triggered": brakes_triggered,
            "gemini_recommendation": gemini_result.get("recommendation") if gemini_result else None,
            "enforcement_decision": "BLOCKED" if not is_valid else "APPROVED",
            "validator": "Cor.Claude_Code_6_v1.0.0",
        }

        result = ValidationResult(
            is_valid=is_valid,
            violation_level=violation_level,
            purpose_score=purpose_score,
            reasons_score=reasons_score,
            brakes_triggered=brakes_triggered,
            violations=violations,
            recommendations=recommendations,
            gemini_validation=gemini_result,
            audit_trail=audit_trail,
            timestamp=datetime.utcnow().isoformat(),
        )

        # Log to audit trail
        self.audit_log.append(result)

        logger.info(
            f"Validation complete: {violation_level.value} - {'BLOCKED' if not is_valid else 'APPROVED'}",
        )

        return result

    def export_audit_log(self, output_path: str = "Cor.Claude_Code_6_audit_log.json") -> str:
        """Export comprehensive audit log

        Args:
            output_path: Path to write audit log

        Returns:
            Path to audit log file

        """
        audit_data = {
            "generated_at": datetime.utcnow().isoformat(),
            "total_validations": len(self.audit_log),
            "doctrine_version": "1.0.0",
            "validations": [asdict(result) for result in self.audit_log],
        }

        with open(output_path, "w") as f:
            json.dump(audit_data, f, indent=2, default=str)

        logger.info(f"Audit log exported: {output_path}")
        return output_path


def main():
    """Example usage and smoke test"""
    print("=== Judge 6 Enforcement - ShadowTag-v2JR Doctrine Compliance ===\n")

    # Initialize enforcer
    enforcer = Cor.Claude_Code_6Enforcer()

    # Test 1: Compliant task
    print("\n--- Test 1: Compliant Healthcare GTM Task ---")
    result = enforcer.validate_task(
        task_description="Develop healthcare market entry strategy for telehealth vertical",
        justification="This task is necessary to enable PNKLN's 30-vertical expansion strategy. "
        "Telehealth represents a $50B market opportunity with clear regulatory pathways. "
        "This research enables strategic positioning without capital expenditure.",
        context={"cost_estimate": 0, "estimated_hours": 8},
    )
    print(f"Validation: {result.violation_level.value}")
    print(f"Decision: {'APPROVED' if result.is_valid else 'BLOCKED'}")
    print(f"Purpose Score: {result.purpose_score:.2f}")
    print(f"Reasons Score: {result.reasons_score:.2f}")
    print(f"Violations: {len(result.violations)}")

    # Test 2: RA-1 violation (should trigger brakes)
    print("\n--- Test 2: RA-1 Production Database Operation ---")
    result = enforcer.validate_task(
        task_description="Delete production database records for inactive users",
        justification="Need to clean up database",
        context={"cost_estimate": 0, "estimated_hours": 2},
    )
    print(f"Validation: {result.violation_level.value}")
    print(f"Decision: {'APPROVED' if result.is_valid else 'BLOCKED'}")
    print(f"Brakes Triggered: {result.brakes_triggered}")
    print(f"Violations: {result.violations}")

    # Test 3: Poor justification
    print("\n--- Test 3: Insufficient Justification ---")
    result = enforcer.validate_task(
        task_description="Implement new feature for user dashboard",
        justification="Because users want it",
        context={"cost_estimate": 0, "estimated_hours": 20},
    )
    print(f"Validation: {result.violation_level.value}")
    print(f"Decision: {'APPROVED' if result.is_valid else 'BLOCKED'}")
    print(f"Reasons Score: {result.reasons_score:.2f}")
    print(f"Recommendations: {result.recommendations}")

    # Export audit log
    print("\n--- Exporting Audit Log ---")
    audit_path = enforcer.export_audit_log()
    print(f"✓ Audit log: {audit_path}")

    print("\n✓ Judge 6 enforcement smoke test complete")


if __name__ == "__main__":
    main()
