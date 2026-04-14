"""AunCRM Core Framework
Implements Purpose-Reasons-Brakes (PRB) compliance system
Based on ATP 5-19 risk stratification and Business Judgment Rule
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class RiskLevel(Enum):
    """ATP 5-19 Risk Classification"""

    RA_1 = "routine"  # Normal operations
    RA_2 = "low"  # Minor impact if fails
    RA_3 = "moderate"  # Significant but containable
    RA_4 = "high"  # Mission-critical failure


@dataclass
class Purpose:
    """PURPOSE: What specific problem does this action solve?
    First-principles thinking: Strip to core objective
    """

    description: str
    business_value: str
    success_criteria: list[str]
    alignment_check: str | None = None  # Against company mission

    def validate(self) -> bool:
        """Ensure purpose is specific and measurable"""
        if len(self.description) < 10:
            return False
        return self.success_criteria


@dataclass
class Reason:
    """REASONS: Why is this approach valid? What assumptions hold?
    Evidence-based justification with confidence intervals
    """

    justification: str
    evidence: list[str]
    assumptions: list[str]
    confidence_score: float  # 0.0 - 1.0
    verification_method: str | None = None

    def validate(self) -> bool:
        """Ensure reasoning is backed by evidence"""
        if not self.evidence:
            return False
        return 0.0 <= self.confidence_score <= 1.0


@dataclass
class Brake:
    """BRAKES: What constraints/limits must be respected?
    Hard stops, thresholds, and kill-switch conditions
    """

    constraint: str
    threshold: Any | None = None
    enforcement_method: str = "manual_review"
    violation_action: str = "halt_execution"

    # Financial brakes (from user's framework)
    roi_threshold: float | None = 3.0  # Minimum 3x ROI
    ltv_cac_ratio: float | None = 4.0  # Minimum 4:1 LTV:CAC
    time_horizon_months: int | None = 18  # Must meet ROI within 18 months

    def validate(self) -> bool:
        """Ensure brake is enforceable"""
        return not len(self.constraint) < 5


@dataclass
class ComplianceContext:
    """Complete AunCRM context for a single decision/action
    Combines Purpose + Reasons + Brakes with audit trail
    """

    context_id: str
    purpose: Purpose
    reasons: list[Reason]
    brakes: list[Brake]
    risk_level: RiskLevel

    # Metadata
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    created_by: str = "system"

    # Execution tracking
    approved: bool = False
    approval_timestamp: str | None = None
    execution_started: str | None = None
    execution_completed: str | None = None

    # Audit trail
    violations: list[dict[str, Any]] = field(default_factory=list)
    audit_log: list[dict[str, Any]] = field(default_factory=list)

    def generate_context_id(self) -> str:
        """Generate unique context ID based on content hash"""
        content = f"{self.purpose.description}{self.created_at}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def validate_all(self) -> tuple[bool, list[str]]:
        """Validate entire compliance context
        Returns (is_valid, violations_list)
        """
        violations = []

        # Validate purpose
        if not self.purpose.validate():
            violations.append("Purpose validation failed: insufficient detail or missing criteria")

        # Validate reasons
        if not self.reasons:
            violations.append("No reasons provided - every action must be justified")

        for i, reason in enumerate(self.reasons):
            if not reason.validate():
                violations.append(
                    f"Reason {i + 1} validation failed: insufficient evidence or invalid confidence",
                )

        # Validate brakes
        if not self.brakes:
            violations.append("No brakes defined - every action must have constraints")

        for i, brake in enumerate(self.brakes):
            if not brake.validate():
                violations.append(f"Brake {i + 1} validation failed: constraint too vague")

        # Risk level checks
        if self.risk_level == RiskLevel.RA_4:
            if len(self.reasons) < 3:
                violations.append("RA-4 (high risk) actions require at least 3 independent reasons")
            if len(self.brakes) < 2:
                violations.append("RA-4 (high risk) actions require at least 2 brake mechanisms")

        return (len(violations) == 0, violations)

    def log_violation(self, violation_type: str, details: str):
        """Log a compliance violation"""
        self.violations.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "type": violation_type,
                "details": details,
                "risk_level": self.risk_level.value,
            },
        )

    def to_audit_record(self) -> dict[str, Any]:
        """Generate complete audit trail record"""
        return {
            "context_id": self.context_id,
            "purpose": {
                "description": self.purpose.description,
                "business_value": self.purpose.business_value,
                "success_criteria": self.purpose.success_criteria,
            },
            "reasons": [
                {
                    "justification": r.justification,
                    "evidence": r.evidence,
                    "confidence": r.confidence_score,
                }
                for r in self.reasons
            ],
            "brakes": [
                {"constraint": b.constraint, "enforcement": b.enforcement_method}
                for b in self.brakes
            ],
            "risk_level": self.risk_level.value,
            "created_at": self.created_at,
            "approved": self.approved,
            "violations": self.violations,
            "audit_log": self.audit_log,
        }


class AunCRMValidator:
    """Main validator class for AunCRM compliance
    Implements Business Judgment Rule decision framework
    """

    def __init__(self, strict_mode: bool = True, auto_halt_on_violation: bool = True):
        self.strict_mode = strict_mode
        self.auto_halt_on_violation = auto_halt_on_violation
        self.validated_contexts: list[ComplianceContext] = []

    def validate_context(
        self, context: ComplianceContext,
    ) -> tuple[bool, list[str], dict[str, Any]]:
        """Validate compliance context against AunCRM rules

        Returns:
            (is_valid, violations, recommendations)

        """
        is_valid, violations = context.validate_all()
        recommendations = []

        # Apply Business Judgment Rule gates
        bjr_gates = self._apply_business_judgment_gates(context)

        if not bjr_gates["passes"]:
            violations.extend(bjr_gates["failures"])

        # Generate recommendations
        if context.risk_level in [RiskLevel.RA_3, RiskLevel.RA_4]:
            recommendations.append("High/moderate risk: Consider Monte Carlo simulation")
            recommendations.append("Required: Scenario planning (base/best/worst)")

        # Check financial gates for any monetary decisions
        if any(b.roi_threshold for b in context.brakes):
            recommendations.append(
                f"ROI gate: Must achieve ≥{context.brakes[0].roi_threshold}x within {context.brakes[0].time_horizon_months} months",
            )

        if is_valid:
            self.validated_contexts.append(context)

        return (
            is_valid,
            violations,
            {"recommendations": recommendations, "business_judgment_gates": bjr_gates},
        )

    def _apply_business_judgment_gates(self, context: ComplianceContext) -> dict[str, Any]:
        """Apply Business Judgment Rule decision gates
        Based on user's framework: ROI, LTV:CAC, kill-switch thresholds
        """
        gates = {"passes": True, "failures": [], "warnings": []}

        # Gate 1: Evidence-based reasoning
        avg_confidence = (
            sum(r.confidence_score for r in context.reasons) / len(context.reasons)
            if context.reasons
            else 0.0
        )

        if avg_confidence < 0.70:
            gates["failures"].append(
                f"Average confidence {avg_confidence:.2f} below 0.70 threshold",
            )
            gates["passes"] = False

        # Gate 2: Risk-adjusted execution
        if context.risk_level == RiskLevel.RA_4 and not context.approved:
            gates["failures"].append("RA-4 actions require explicit approval before execution")
            gates["passes"] = False

        # Gate 3: Brake enforcement
        if not context.brakes:
            gates["failures"].append("No brake mechanisms defined - violates fail-safe principle")
            gates["passes"] = False

        return gates

    def generate_compliance_report(self) -> dict[str, Any]:
        """Generate summary compliance report"""
        total = len(self.validated_contexts)

        if total == 0:
            return {"status": "no_contexts_validated"}

        risk_distribution = {
            level.value: len([c for c in self.validated_contexts if c.risk_level == level])
            for level in RiskLevel
        }

        violation_count = sum(len(c.violations) for c in self.validated_contexts)

        return {
            "total_contexts": total,
            "risk_distribution": risk_distribution,
            "total_violations": violation_count,
            "compliance_rate": (total - violation_count) / total if total > 0 else 0.0,
            "timestamp": datetime.utcnow().isoformat(),
        }
