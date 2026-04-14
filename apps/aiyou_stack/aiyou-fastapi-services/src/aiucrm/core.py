"""AiUCRM Core Engine
Military Composite Risk Management System adapted for AI governance

Pre-execution validation framework that gates all AI operations.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk classification levels (Military standard)"""

    MINIMAL = "minimal"  # Risk ≤5% probability, ≤$1K impact
    LOW = "low"  # Risk ≤15% probability, ≤$10K impact
    MODERATE = "moderate"  # Risk ≤40% probability, ≤$100K impact
    HIGH = "high"  # Risk ≤70% probability, ≤$1M impact
    CRITICAL = "critical"  # Risk >70% probability, >$1M impact


class ComplianceStatus(Enum):
    """Compliance validation status"""

    APPROVED = "approved"  # All checks passed
    CONDITIONAL = "conditional"  # Approved with conditions
    BLOCKED_LEGAL = "blocked_legal"  # Legal compliance failure
    BLOCKED_ETHICAL = "blocked_ethical"  # Ethical violation
    BLOCKED_SAFETY = "blocked_safety"  # Safety risk detected
    BLOCKED_SOVEREIGNTY = "blocked_sovereignty"  # Data sovereignty violation


@dataclass
class ComplianceResult:
    """Result of AiUCRM validation"""

    status: ComplianceStatus
    risk_level: RiskLevel
    risk_score: float  # 0.0-1.0
    legal_compliant: bool
    ethical_compliant: bool
    safety_compliant: bool
    sovereignty_compliant: bool
    explanation: str
    recommendations: list[str] = field(default_factory=list)
    audit_trail: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for logging"""
        return {
            "status": self.status.value,
            "risk_level": self.risk_level.value,
            "risk_score": self.risk_score,
            "legal_compliant": self.legal_compliant,
            "ethical_compliant": self.ethical_compliant,
            "safety_compliant": self.safety_compliant,
            "sovereignty_compliant": self.sovereignty_compliant,
            "explanation": self.explanation,
            "recommendations": self.recommendations,
            "audit_trail": self.audit_trail,
            "timestamp": self.timestamp,
        }


class AiUCRM:
    """AI Unified Compliance & Risk Management Engine

    Implements pre-execution validation for all AI operations across:
    - Legal compliance (EU AI Act, FAA, DoD, HIPAA, MDR)
    - Ethical standards (Purpose/Reasons/Brakes)
    - Operational safety (Incident prevention)
    - Data sovereignty (GDPR, CCPA, regional laws)

    Example:
        ```python
        # Initialize AiUCRM
        aiucrm = AiUCRM(
            legal_frameworks=["EU_AI_ACT", "HIPAA", "FAA"],
            risk_threshold=0.3,  # Block if risk score >30%
            audit_enabled=True
        )

        # Validate AI operation before execution
        request = AIOperationRequest(
            operation_type="medical_diagnosis",
            data_region="EU",
            user_consent=True,
            purpose="patient_care"
        )

        result = aiucrm.validate(request)

        if result.status == ComplianceStatus.APPROVED:
            # Safe to execute AI operation
            execute_ai_inference(request)
        else:
            # Block and log violation
            logger.warning(f"Blocked: {result.explanation}")
        ```

    """

    def __init__(
        self,
        legal_frameworks: list[str] = None,
        risk_threshold: float = 0.3,
        audit_enabled: bool = True,
        strict_mode: bool = False,
    ):
        """Initialize AiUCRM engine

        Args:
            legal_frameworks: List of applicable legal frameworks
                (e.g., ["EU_AI_ACT", "HIPAA", "FAA", "DoD_RAI"])
            risk_threshold: Maximum acceptable risk score (0.0-1.0)
            audit_enabled: Whether to generate audit trails
            strict_mode: If True, blocks on ANY violation; if False, allows conditional approval

        """
        self.legal_frameworks = legal_frameworks or ["EU_AI_ACT"]
        self.risk_threshold = risk_threshold
        self.audit_enabled = audit_enabled
        self.strict_mode = strict_mode

        # Initialize validators (will be injected)
        self.legal_validator = None
        self.ethical_validator = None
        self.safety_validator = None
        self.sovereignty_validator = None

        # Compliance statistics
        self.stats = {
            "total_validations": 0,
            "approvals": 0,
            "blocks": 0,
            "conditional_approvals": 0,
            "avg_risk_score": 0.0,
        }

        logger.info(f"AiUCRM initialized with frameworks: {self.legal_frameworks}")
        logger.info(f"Risk threshold: {self.risk_threshold}, Strict mode: {self.strict_mode}")

    def validate(self, request: dict[str, Any]) -> ComplianceResult:
        """Validate AI operation request against AiUCRM framework

        Args:
            request: AI operation request containing:
                - operation_type: str (e.g., "medical_diagnosis", "content_moderation")
                - data_region: str (e.g., "EU", "US", "CHINA")
                - user_consent: bool
                - purpose: str (mission statement)
                - content: Optional[str] (content to validate)
                - metadata: Optional[Dict] (additional context)

        Returns:
            ComplianceResult with validation outcome

        """
        self.stats["total_validations"] += 1
        start_time = datetime.utcnow()

        # Step 1: Legal Compliance Check
        legal_result = self._check_legal_compliance(request)

        # Step 2: Ethical Compliance Check (Purpose/Reasons/Brakes)
        ethical_result = self._check_ethical_compliance(request)

        # Step 3: Operational Safety Check
        safety_result = self._check_operational_safety(request)

        # Step 4: Data Sovereignty Check
        sovereignty_result = self._check_data_sovereignty(request)

        # Step 5: Calculate aggregated risk score
        risk_score = self._calculate_risk_score(
            legal_result, ethical_result, safety_result, sovereignty_result,
        )

        # Step 6: Determine risk level
        risk_level = self._classify_risk_level(risk_score)

        # Step 7: Determine final compliance status
        status = self._determine_status(
            legal_result["compliant"],
            ethical_result["compliant"],
            safety_result["compliant"],
            sovereignty_result["compliant"],
            risk_score,
        )

        # Step 8: Generate explanation and recommendations
        explanation = self._generate_explanation(
            status, legal_result, ethical_result, safety_result, sovereignty_result,
        )
        recommendations = self._generate_recommendations(
            legal_result, ethical_result, safety_result, sovereignty_result,
        )

        # Step 9: Build audit trail
        audit_trail = {
            "legal_check": legal_result,
            "ethical_check": ethical_result,
            "safety_check": safety_result,
            "sovereignty_check": sovereignty_result,
            "validation_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
            "frameworks_applied": self.legal_frameworks,
        }

        # Step 10: Update statistics
        if status == ComplianceStatus.APPROVED:
            self.stats["approvals"] += 1
        elif status == ComplianceStatus.CONDITIONAL:
            self.stats["conditional_approvals"] += 1
        else:
            self.stats["blocks"] += 1

        self.stats["avg_risk_score"] = (
            self.stats["avg_risk_score"] * (self.stats["total_validations"] - 1) + risk_score
        ) / self.stats["total_validations"]

        result = ComplianceResult(
            status=status,
            risk_level=risk_level,
            risk_score=risk_score,
            legal_compliant=legal_result["compliant"],
            ethical_compliant=ethical_result["compliant"],
            safety_compliant=safety_result["compliant"],
            sovereignty_compliant=sovereignty_result["compliant"],
            explanation=explanation,
            recommendations=recommendations,
            audit_trail=audit_trail if self.audit_enabled else {},
        )

        logger.info(
            f"AiUCRM validation: {status.value} (risk={risk_level.value}, score={risk_score:.3f})",
        )

        return result

    def _check_legal_compliance(self, request: dict[str, Any]) -> dict[str, Any]:
        """Check legal compliance against configured frameworks"""
        if self.legal_validator:
            return self.legal_validator.validate(request, self.legal_frameworks)

        # Default implementation (will be replaced by injected validator)
        return {
            "compliant": True,
            "violations": [],
            "score": 1.0,
            "frameworks_checked": self.legal_frameworks,
        }

    def _check_ethical_compliance(self, request: dict[str, Any]) -> dict[str, Any]:
        """Check ethical compliance (Purpose/Reasons/Brakes)"""
        if self.ethical_validator:
            return self.ethical_validator.validate(request)

        # Default implementation
        purpose_valid = request.get("purpose") is not None
        user_consent = request.get("user_consent", False)

        return {
            "compliant": purpose_valid and user_consent,
            "purpose_valid": purpose_valid,
            "user_consent": user_consent,
            "score": 1.0 if (purpose_valid and user_consent) else 0.5,
        }

    def _check_operational_safety(self, request: dict[str, Any]) -> dict[str, Any]:
        """Check operational safety risks"""
        if self.safety_validator:
            return self.safety_validator.validate(request)

        # Default implementation
        operation_type = request.get("operation_type", "")
        high_risk_operations = ["medical_diagnosis", "financial_advice", "legal_decision"]

        is_high_risk = operation_type in high_risk_operations

        return {
            "compliant": True,  # Default allow
            "high_risk": is_high_risk,
            "risk_factors": [],
            "score": 0.7 if is_high_risk else 1.0,
        }

    def _check_data_sovereignty(self, request: dict[str, Any]) -> dict[str, Any]:
        """Check data sovereignty compliance"""
        if self.sovereignty_validator:
            return self.sovereignty_validator.validate(request)

        # Default implementation
        data_region = request.get("data_region", "US")
        operation_region = request.get("operation_region", data_region)

        # Simple check: data and operation in same region
        compliant = data_region == operation_region

        return {
            "compliant": compliant,
            "data_region": data_region,
            "operation_region": operation_region,
            "cross_border_transfer": not compliant,
            "score": 1.0 if compliant else 0.6,
        }

    def _calculate_risk_score(
        self,
        legal_result: dict[str, Any],
        ethical_result: dict[str, Any],
        safety_result: dict[str, Any],
        sovereignty_result: dict[str, Any],
    ) -> float:
        """Calculate aggregated risk score (0.0-1.0)
        Lower score = higher risk
        """
        weights = {"legal": 0.35, "ethical": 0.25, "safety": 0.25, "sovereignty": 0.15}

        score = (
            legal_result["score"] * weights["legal"]
            + ethical_result["score"] * weights["ethical"]
            + safety_result["score"] * weights["safety"]
            + sovereignty_result["score"] * weights["sovereignty"]
        )

        # Invert: 1.0 = minimal risk, 0.0 = maximum risk
        return score

    def _classify_risk_level(self, risk_score: float) -> RiskLevel:
        """Classify risk based on score"""
        if risk_score >= 0.95:
            return RiskLevel.MINIMAL
        if risk_score >= 0.85:
            return RiskLevel.LOW
        if risk_score >= 0.70:
            return RiskLevel.MODERATE
        if risk_score >= 0.50:
            return RiskLevel.HIGH
        return RiskLevel.CRITICAL

    def _determine_status(
        self,
        legal_compliant: bool,
        ethical_compliant: bool,
        safety_compliant: bool,
        sovereignty_compliant: bool,
        risk_score: float,
    ) -> ComplianceStatus:
        """Determine final compliance status"""
        # Check for blocking violations
        if not legal_compliant:
            return ComplianceStatus.BLOCKED_LEGAL
        if not ethical_compliant:
            return ComplianceStatus.BLOCKED_ETHICAL
        if not safety_compliant:
            return ComplianceStatus.BLOCKED_SAFETY
        if not sovereignty_compliant and self.strict_mode:
            return ComplianceStatus.BLOCKED_SOVEREIGNTY

        # Check risk threshold
        if risk_score < self.risk_threshold:
            if self.strict_mode:
                return ComplianceStatus.BLOCKED_SAFETY
            return ComplianceStatus.CONDITIONAL

        # All checks passed
        return ComplianceStatus.APPROVED

    def _generate_explanation(
        self,
        status: ComplianceStatus,
        legal_result: dict[str, Any],
        ethical_result: dict[str, Any],
        safety_result: dict[str, Any],
        sovereignty_result: dict[str, Any],
    ) -> str:
        """Generate human-readable explanation"""
        if status == ComplianceStatus.APPROVED:
            return (
                f"Operation approved. All compliance checks passed "
                f"(legal: {legal_result['score']:.2f}, "
                f"ethical: {ethical_result['score']:.2f}, "
                f"safety: {safety_result['score']:.2f}, "
                f"sovereignty: {sovereignty_result['score']:.2f})"
            )
        if status == ComplianceStatus.CONDITIONAL:
            return (
                "Operation approved with conditions. "
                "Risk score below threshold but all compliance checks passed. "
                "Enhanced monitoring recommended."
            )
        if status == ComplianceStatus.BLOCKED_LEGAL:
            violations = legal_result.get("violations", [])
            return f"Blocked: Legal compliance violations detected: {', '.join(violations)}"
        if status == ComplianceStatus.BLOCKED_ETHICAL:
            return "Blocked: Ethical compliance failure (Purpose/Reasons/Brakes validation failed)"
        if status == ComplianceStatus.BLOCKED_SAFETY:
            risk_factors = safety_result.get("risk_factors", [])
            return f"Blocked: Operational safety risks detected: {', '.join(risk_factors)}"
        if status == ComplianceStatus.BLOCKED_SOVEREIGNTY:
            return (
                f"Blocked: Data sovereignty violation "
                f"(data region: {sovereignty_result['data_region']}, "
                f"operation region: {sovereignty_result['operation_region']})"
            )
        return "Unknown compliance status"

    def _generate_recommendations(
        self,
        legal_result: dict[str, Any],
        ethical_result: dict[str, Any],
        safety_result: dict[str, Any],
        sovereignty_result: dict[str, Any],
    ) -> list[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Legal recommendations
        if not legal_result["compliant"]:
            violations = legal_result.get("violations", [])
            for violation in violations:
                recommendations.append(f"Address legal violation: {violation}")

        # Ethical recommendations
        if not ethical_result["compliant"]:
            if not ethical_result.get("purpose_valid"):
                recommendations.append("Define clear purpose statement for this operation")
            if not ethical_result.get("user_consent"):
                recommendations.append("Obtain explicit user consent before proceeding")

        # Safety recommendations
        if safety_result.get("high_risk"):
            recommendations.append("Implement additional safety monitoring for high-risk operation")
            recommendations.append("Enable enhanced audit logging")

        # Sovereignty recommendations
        if not sovereignty_result["compliant"]:
            recommendations.append(
                f"Migrate operation to {sovereignty_result['data_region']} region "
                f"or obtain cross-border transfer approval",
            )

        return recommendations

    def get_statistics(self) -> dict[str, Any]:
        """Get compliance statistics"""
        return {
            **self.stats,
            "approval_rate": (
                self.stats["approvals"] / self.stats["total_validations"]
                if self.stats["total_validations"] > 0
                else 0.0
            ),
            "block_rate": (
                self.stats["blocks"] / self.stats["total_validations"]
                if self.stats["total_validations"] > 0
                else 0.0
            ),
        }
