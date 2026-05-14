# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
ATP 5-19 Risk Classification Engine

Implements US Army Risk Management framework for governance routing.
Every decision grounded in military-proven risk assessment methodology.

Risk Matrix (Probability × Severity):
           Severity →
Prob ↓    I        II       III      IV
A         EH       EH       H        M
B         EH       H        H        M
C         H        H        M        L
D         H        M        M        L
E         M        M        L        L

Routing Logic:
- EH/H → Fast Path (OPA) - Immediate deterministic control
- M    → Slow Path (Agent) - Contextual evaluation needed
- L    → Slow Path (Agent) - Async audit sufficient
"""

from typing import Dict, Tuple
from .models import GovernanceRequest, RiskLevel, RiskAssessment, DecisionPath


class ATP519RiskClassifier:
    """
    Military-grade risk classification.

    Zero ambiguity. Complete coverage. Battle-tested logic.
    """

    # ATP 5-19 Risk Matrix (probability, severity) -> risk_level
    RISK_MATRIX: dict[tuple[str, str], RiskLevel] = {
        # Probability A (Frequent: 1 in 500 exposures)
        ("A", "I"): RiskLevel.EXTREMELY_HIGH,
        ("A", "II"): RiskLevel.EXTREMELY_HIGH,
        ("A", "III"): RiskLevel.HIGH,
        ("A", "IV"): RiskLevel.MEDIUM,
        # Probability B (Likely: 1 in 1000 exposures)
        ("B", "I"): RiskLevel.EXTREMELY_HIGH,
        ("B", "II"): RiskLevel.HIGH,
        ("B", "III"): RiskLevel.HIGH,
        ("B", "IV"): RiskLevel.MEDIUM,
        # Probability C (Occasional: May occur sometime)
        ("C", "I"): RiskLevel.HIGH,
        ("C", "II"): RiskLevel.HIGH,
        ("C", "III"): RiskLevel.MEDIUM,
        ("C", "IV"): RiskLevel.LOW,
        # Probability D (Seldom: Unlikely but possible)
        ("D", "I"): RiskLevel.HIGH,
        ("D", "II"): RiskLevel.MEDIUM,
        ("D", "III"): RiskLevel.MEDIUM,
        ("D", "IV"): RiskLevel.LOW,
        # Probability E (Unlikely: Can assume will not occur)
        ("E", "I"): RiskLevel.MEDIUM,
        ("E", "II"): RiskLevel.MEDIUM,
        ("E", "III"): RiskLevel.LOW,
        ("E", "IV"): RiskLevel.LOW,
    }

    # Financial thresholds for severity classification
    SEVERITY_FINANCIAL: dict[str, tuple[float, float]] = {
        "I": (100_000, float("inf")),  # Catastrophic: >$100K
        "II": (10_000, 100_000),  # Critical: $10K-$100K
        "III": (1_000, 10_000),  # Moderate: $1K-$10K
        "IV": (0, 1_000),  # Negligible: <$1K
    }

    @classmethod
    def assess_risk(cls, request: GovernanceRequest) -> RiskAssessment:
        """
        Perform ATP 5-19 risk assessment.

        Returns probability, severity, and resulting risk level.
        """
        probability = cls._assess_probability(request)
        severity = cls._assess_severity(request)
        risk_level = cls.RISK_MATRIX[(probability, severity)]

        hazards = cls._identify_hazards(request)
        controls = cls._recommend_controls(request, risk_level)

        return RiskAssessment(
            probability=probability,
            severity=severity,
            risk_level=risk_level,
            hazards=hazards,
            controls=controls,
        )

    @classmethod
    def _assess_probability(cls, request: GovernanceRequest) -> str:
        """
        Assess probability of risk materialization (A-E scale).

        A = Frequent (1 in 500)
        B = Likely (1 in 1000)
        C = Occasional (may occur)
        D = Seldom (unlikely but possible)
        E = Unlikely (can assume will not occur)
        """
        # High-frequency actions
        if request.action in [
            "read_data",
            "list_resources",
            "view_dashboard",
        ]:
            return "E"  # Unlikely to cause harm

        # Medium-frequency with controls
        if request.action in [
            "approve_expense",
            "update_resource",
            "create_resource",
        ]:
            # Check if proper controls exist
            if cls._has_approval_controls(request):
                return "D"  # Seldom - controls in place
            return "C"  # Occasional - needs evaluation

        # Financial transactions
        if request.action in [
            "transfer_funds",
            "process_payment",
            "budget_allocation",
        ]:
            return "B"  # Likely - financial risk inherent

        # High-risk administrative actions
        if request.action in [
            "delete_resource",
            "grant_admin_access",
            "modify_security_policy",
        ]:
            return "A"  # Frequent - high-risk actions

        # Default: Occasional
        return "C"

    @classmethod
    def _assess_severity(cls, request: GovernanceRequest) -> str:
        """
        Assess severity of potential impact (I-IV scale).

        I  = Catastrophic (mission failure, >$100K loss)
        II = Critical (mission degradation, $10K-$100K loss)
        III = Moderate (mission impact, $1K-$10K loss)
        IV = Negligible (minimal impact, <$1K loss)
        """
        # Financial value assessment
        if request.financial_value is not None:
            for severity, (min_val, max_val) in cls.SEVERITY_FINANCIAL.items():
                if min_val <= request.financial_value < max_val:
                    return severity

        # Data sensitivity assessment
        data_sensitivity = request.data_sensitivity
        if data_sensitivity == "PHI":  # Protected Health Information
            return "I"  # Catastrophic - HIPAA violations
        elif data_sensitivity == "PII":  # Personally Identifiable Information
            return "II"  # Critical - GDPR/CCPA violations
        elif data_sensitivity == "confidential":
            return "III"  # Moderate - competitive harm
        elif data_sensitivity == "internal":
            return "IV"  # Negligible - internal only

        # Action-based severity
        if request.action in [
            "delete_production_data",
            "revoke_all_access",
            "shutdown_service",
        ]:
            return "I"  # Catastrophic

        if request.action in [
            "modify_production_config",
            "grant_admin_access",
        ]:
            return "II"  # Critical

        if request.action in [
            "update_resource",
            "create_resource",
        ]:
            return "III"  # Moderate

        # Default: Moderate
        return "III"

    @classmethod
    def _has_approval_controls(cls, request: GovernanceRequest) -> bool:
        """Check if proper approval controls are in place"""
        context = request.context
        return "approver_id" in context or "manager_approval" in context or "budget_approved" in context

    @classmethod
    def _identify_hazards(cls, request: GovernanceRequest) -> list[str]:
        """
        Identify specific hazards (ATP 5-19 Step 1).

        Uses METT-TC framework:
        - Mission: Nature and complexity
        - Enemy: Threat presence
        - Terrain/Weather: Environmental hazards
        - Troops: Training, equipment, morale
        - Time: Planning time available
        - Civil: Population, legal considerations
        """
        hazards = []

        # Financial hazards
        if request.financial_value and request.financial_value > 10_000:
            hazards.append("Budget overrun risk")

        # Access control hazards
        if "admin" in request.action.lower() or "grant" in request.action.lower():
            hazards.append("Unauthorized privilege escalation")

        # Data protection hazards
        if request.data_sensitivity in ["PII", "PHI"]:
            hazards.append("Regulatory compliance violation (GDPR/HIPAA)")

        # Operational hazards
        if "delete" in request.action.lower() or "shutdown" in request.action.lower():
            hazards.append("Service disruption or data loss")

        # Default hazard if none identified
        if not hazards:
            hazards.append("Standard operational risk")

        return hazards

    @classmethod
    def _recommend_controls(cls, request: GovernanceRequest, risk_level: RiskLevel) -> list[str]:
        """
        Recommend risk controls (ATP 5-19 Step 3).

        Controls reduce probability or severity to acceptable levels.
        """
        controls = []

        # Always require authentication
        controls.append("User authentication verified")

        if risk_level in [RiskLevel.EXTREMELY_HIGH, RiskLevel.HIGH]:
            controls.append("Immediate supervisor approval required")
            controls.append("Dual-person authorization")
            controls.append("Real-time monitoring and alerting")

        if risk_level == RiskLevel.MEDIUM:
            controls.append("Manager approval required")
            controls.append("Audit trail with 6-month retention")

        if risk_level == RiskLevel.LOW:
            controls.append("Asynchronous audit review")

        # Financial-specific controls
        if request.financial_value and request.financial_value > 5_000:
            controls.append("Budget availability check")
            controls.append("Spending authority verification")

        # Data-specific controls
        if request.data_sensitivity in ["PII", "PHI"]:
            controls.append("Data minimization enforced")
            controls.append("Encryption in transit and at rest")

        return controls

    @classmethod
    def determine_path(cls, risk_assessment: RiskAssessment) -> DecisionPath:
        """
        Determine routing path based on risk level.

        EH/H → Fast Path (OPA) - Deterministic blocking required
        M/L  → Slow Path (Agent) - Context evaluation needed
        """
        if risk_assessment.risk_level in [RiskLevel.EXTREMELY_HIGH, RiskLevel.HIGH]:
            return DecisionPath.FAST_PATH

        # Medium and Low risk benefit from agent reasoning
        return DecisionPath.SLOW_PATH

    @classmethod
    def estimate_latency(cls, path: DecisionPath) -> int:
        """
        Estimate processing latency in milliseconds.

        Fast Path (OPA): <10ms typical
        Slow Path (Agent): 1-2s simple, 2-5s complex
        """
        if path == DecisionPath.FAST_PATH:
            return 5  # OPA sub-millisecond, add network overhead

        # Agent path: TTFT + generation time
        # Gemini Flash: 162ms TTFT + 300 tokens @ 7.3ms/token ≈ 2.4s
        return 2400
