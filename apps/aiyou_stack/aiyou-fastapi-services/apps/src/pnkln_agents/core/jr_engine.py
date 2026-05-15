"""JR Engine: Purpose/Reasons/Brakes Validator
Target latency: <500μs
Method: ATP 5-19 risk assessment (Probability × Severity → Level)
Function: Validates all agent actions before execution
"""

import time
from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Any

from src.antigravity.ironwood_mcp import log_event


class RiskLevel(IntEnum):
    """Risk levels based on ATP 5-19 methodology"""

    EXTREMELY_HIGH = 5  # Probability: Frequent, Severity: Catastrophic
    HIGH = 4  # Probability: Likely, Severity: Critical
    MODERATE = 3  # Probability: Occasional, Severity: Moderate
    LOW = 2  # Probability: Seldom, Severity: Negligible
    EXTREMELY_LOW = 1  # Probability: Unlikely, Severity: Negligible


class BrakeType(Enum):
    """Types of brakes that can halt execution"""

    SECURITY_VIOLATION = "security_violation"
    COMPLIANCE_VIOLATION = "compliance_violation"
    BUDGET_EXCEEDED = "budget_exceeded"
    UNAUTHORIZED_ACTION = "unauthorized_action"
    DATA_PRIVACY_RISK = "data_privacy_risk"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"


@dataclass
class Purpose:
    """Defines the intent and goal of an agent action"""

    intent: str
    business_value: str
    customer_id: str
    cost_estimate_usd: float
    expected_outcome: str


@dataclass
class Reason:
    """Supporting rationale for the action"""

    justification: str
    risk_probability: float  # 0.0 to 1.0
    risk_severity: float  # 0.0 to 1.0
    mitigation_strategy: str | None = None


@dataclass
class Brake:
    """Brake signal that halts execution"""

    triggered: bool
    brake_type: BrakeType
    reason: str
    risk_level: RiskLevel
    required_action: str  # What needs to happen to proceed


@dataclass
class JRDecision:
    """Output of JR Engine validation"""

    approved: bool
    purpose: Purpose
    reasons: list[Reason]
    brakes: list[Brake]
    constraints: dict[str, Any]
    audit_trail: dict[str, Any]
    validation_time_ms: float


class JREngine:
    """Purpose/Reasons/Brakes validator for agent actions

    Validates every agent action against:
    - Business purpose alignment
    - Risk assessment (ATP 5-19)
    - Constraint enforcement (budget, compliance, security)
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.max_budget_per_action = self.config.get("max_budget_per_action", 100.0)
        self.require_human_approval_above = self.config.get("require_human_approval_above", 1000.0)
        self.strict_mode = self.config.get("strict_mode", True)

    def validate(
        self,
        purpose: Purpose,
        reasons: list[Reason],
        context: dict[str, Any] | None = None,
    ) -> JRDecision:
        """Validates an agent action using Purpose/Reasons/Brakes framework

        Args:
            purpose: Intent and goal of the action
            reasons: Supporting rationale and risk assessment
            context: Additional context (user permissions, current state, etc.)

        Returns:
            JRDecision with approval status, constraints, and audit trail

        """
        start_time = time.perf_counter()
        context = context or {}
        brakes = []
        constraints = {}

        # Validate purpose
        purpose_brake = self._validate_purpose(purpose, context)
        if purpose_brake:
            brakes.append(purpose_brake)

        # Validate reasons and assess risk
        risk_brake = self._validate_reasons(reasons, purpose, context)
        if risk_brake:
            brakes.append(risk_brake)

        # Check budget constraints
        budget_brake = self._check_budget(purpose, context)
        if budget_brake:
            brakes.append(budget_brake)

        # Check compliance requirements
        compliance_brake = self._check_compliance(purpose, context)
        if compliance_brake:
            brakes.append(compliance_brake)

        # Build constraints for approved actions
        if not brakes:
            constraints = self._build_constraints(purpose, reasons, context)

        # Build audit trail
        audit_trail = self._build_audit_trail(purpose, reasons, brakes, context)

        validation_time_ms = (time.perf_counter() - start_time) * 1000

        # Log to Universal Tape
        try:
            log_content = {
                "approved": len(brakes) == 0,
                "purpose_hash": hash(purpose.intent),
                "risk_max": max([r.risk_severity * r.risk_probability for r in reasons])
                if reasons
                else 0,
                "brakes": [b.brake_type.name for b in brakes],
            }
            log_event(
                source="JR-Engine",
                event_type="access_control",
                content=str(log_content),
            )
        except Exception as e:
            print(f"Scribe Log Failed: {e}")

        return JRDecision(
            approved=len(brakes) == 0,
            purpose=purpose,
            reasons=reasons,
            brakes=brakes,
            constraints=constraints,
            audit_trail=audit_trail,
            validation_time_ms=validation_time_ms,
        )

    def _validate_purpose(self, purpose: Purpose, context: dict[str, Any]) -> Brake | None:
        """Validate that purpose is clear and authorized"""
        if not purpose.intent or len(purpose.intent.strip()) < 10:
            return Brake(
                triggered=True,
                brake_type=BrakeType.UNAUTHORIZED_ACTION,
                reason="Purpose intent is unclear or too vague",
                risk_level=RiskLevel.HIGH,
                required_action="Provide clear, detailed intent (min 10 characters)",
            )

        if not purpose.customer_id:
            return Brake(
                triggered=True,
                brake_type=BrakeType.UNAUTHORIZED_ACTION,
                reason="No customer_id provided - cannot attribute action",
                risk_level=RiskLevel.HIGH,
                required_action="Provide valid customer_id for attribution",
            )

        return None

    def _validate_reasons(
        self,
        reasons: list[Reason],
        purpose: Purpose,
        context: dict[str, Any],
    ) -> Brake | None:
        """Validate reasons and assess risk using ATP 5-19"""
        if not reasons:
            return Brake(
                triggered=True,
                brake_type=BrakeType.UNAUTHORIZED_ACTION,
                reason="No reasons provided for action",
                risk_level=RiskLevel.MODERATE,
                required_action="Provide at least one reason with risk assessment",
            )

        # Calculate overall risk level
        max_risk_score = 0.0
        for reason in reasons:
            risk_score = reason.risk_probability * reason.risk_severity
            max_risk_score = max(max_risk_score, risk_score)

        # Map risk score to risk level
        risk_level = self._calculate_risk_level(max_risk_score)

        # High-risk actions require mitigation strategy
        if risk_level in [RiskLevel.HIGH, RiskLevel.EXTREMELY_HIGH]:
            has_mitigation = any(r.mitigation_strategy for r in reasons)
            if not has_mitigation:
                return Brake(
                    triggered=True,
                    brake_type=BrakeType.UNAUTHORIZED_ACTION,
                    reason=f"High-risk action ({risk_level.name}) requires mitigation strategy",
                    risk_level=risk_level,
                    required_action="Provide mitigation strategy for high-risk action",
                )

        # Extremely high risk requires human approval
        if risk_level == RiskLevel.EXTREMELY_HIGH:
            return Brake(
                triggered=True,
                brake_type=BrakeType.UNAUTHORIZED_ACTION,
                reason="Extremely high risk - requires human approval",
                risk_level=risk_level,
                required_action="Escalate to human for approval",
            )

        return None

    def _check_budget(self, purpose: Purpose, context: dict[str, Any]) -> Brake | None:
        """Check budget constraints"""
        if purpose.cost_estimate_usd > self.max_budget_per_action:
            return Brake(
                triggered=True,
                brake_type=BrakeType.BUDGET_EXCEEDED,
                reason=f"Cost estimate ${purpose.cost_estimate_usd:.2f} exceeds limit ${self.max_budget_per_action:.2f}",
                risk_level=RiskLevel.HIGH,
                required_action="Reduce cost or request budget increase",
            )

        if purpose.cost_estimate_usd > self.require_human_approval_above:
            return Brake(
                triggered=True,
                brake_type=BrakeType.BUDGET_EXCEEDED,
                reason=f"Cost ${purpose.cost_estimate_usd:.2f} requires human approval",
                risk_level=RiskLevel.MODERATE,
                required_action="Escalate to human for budget approval",
            )

        return None

    def _check_compliance(self, purpose: Purpose, context: dict[str, Any]) -> Brake | None:
        """Check compliance requirements"""
        # Check if action involves regulated data
        involves_pii = context.get("involves_pii", False)
        involves_phi = context.get("involves_phi", False)
        eu_customer = context.get("eu_customer", False)

        if involves_pii and not context.get("gdpr_consent", False) and eu_customer:
            return Brake(
                triggered=True,
                brake_type=BrakeType.COMPLIANCE_VIOLATION,
                reason="Action involves PII for EU customer without GDPR consent",
                risk_level=RiskLevel.EXTREMELY_HIGH,
                required_action="Obtain GDPR consent before processing EU customer PII",
            )

        if involves_phi and not context.get("hipaa_authorization", False):
            return Brake(
                triggered=True,
                brake_type=BrakeType.COMPLIANCE_VIOLATION,
                reason="Action involves PHI without HIPAA authorization",
                risk_level=RiskLevel.EXTREMELY_HIGH,
                required_action="Obtain HIPAA authorization before processing PHI",
            )

        return None

    def _build_constraints(
        self,
        purpose: Purpose,
        reasons: list[Reason],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Build constraints for approved actions"""
        constraints = {
            "max_cost_usd": min(purpose.cost_estimate_usd * 1.2, self.max_budget_per_action),
            "timeout_seconds": 300,  # 5 minutes default
            "retry_limit": 3,
            "require_audit_trail": True,
        }

        # Add stricter constraints for higher-risk actions
        max_risk_score = max(r.risk_probability * r.risk_severity for r in reasons)
        risk_level = self._calculate_risk_level(max_risk_score)

        if risk_level >= RiskLevel.MODERATE:
            constraints["timeout_seconds"] = 60  # Shorter timeout for risky actions
            constraints["retry_limit"] = 1  # Fewer retries
            constraints["require_human_review"] = True

        return constraints

    def _build_audit_trail(
        self,
        purpose: Purpose,
        reasons: list[Reason],
        brakes: list[Brake],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Build comprehensive audit trail"""
        return {
            "timestamp": time.time(),
            "purpose": {
                "intent": purpose.intent,
                "business_value": purpose.business_value,
                "customer_id": purpose.customer_id,
                "cost_estimate_usd": purpose.cost_estimate_usd,
                "expected_outcome": purpose.expected_outcome,
            },
            "reasons": [
                {
                    "justification": r.justification,
                    "risk_probability": r.risk_probability,
                    "risk_severity": r.risk_severity,
                    "risk_score": r.risk_probability * r.risk_severity,
                    "mitigation_strategy": r.mitigation_strategy,
                }
                for r in reasons
            ],
            "brakes": [
                {
                    "triggered": b.triggered,
                    "brake_type": b.brake_type.value,
                    "reason": b.reason,
                    "risk_level": b.risk_level.name,
                    "required_action": b.required_action,
                }
                for b in brakes
            ],
            "context": context,
            "approved": len(brakes) == 0,
        }

    def _calculate_risk_level(self, risk_score: float) -> RiskLevel:
        """Calculate risk level from probability × severity score"""
        if risk_score >= 0.8:
            return RiskLevel.EXTREMELY_HIGH
        if risk_score >= 0.6:
            return RiskLevel.HIGH
        if risk_score >= 0.4:
            return RiskLevel.MODERATE
        if risk_score >= 0.2:
            return RiskLevel.LOW
        return RiskLevel.EXTREMELY_LOW
