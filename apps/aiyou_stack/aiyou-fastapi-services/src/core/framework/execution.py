"""Operating System Execution Framework
Risk assessment, decision protocols, and development constraints

Author: ShadowTag-v2JR System
Date: 2025-11-17
"""

from dataclasses import dataclass, field
from enum import Enum


class RiskProbability(Enum):
    """ATP 5-19 Risk probability levels"""

    A_FREQUENT = "A"
    B_LIKELY = "B"
    C_OCCASIONAL = "C"
    D_SELDOM = "D"
    E_UNLIKELY = "E"


class RiskSeverity(Enum):
    """ATP 5-19 Risk severity levels"""

    I_CATASTROPHIC = "I"
    II_CRITICAL = "II"
    III_MODERATE = "III"
    IV_NEGLIGIBLE = "IV"


class RiskLevel(Enum):
    """Risk assessment levels"""

    EH_EXTREMELY_HIGH = "EH"
    H_HIGH = "H"
    M_MEDIUM = "M"
    L_LOW = "L"


@dataclass
class RiskAssessmentMatrix:
    """ATP 5-19 Risk assessment matrix"""

    def assess(self, probability: RiskProbability, severity: RiskSeverity) -> RiskLevel:
        """Assess risk level from probability × severity"""
        matrix = {
            (RiskProbability.A_FREQUENT, RiskSeverity.I_CATASTROPHIC): RiskLevel.EH_EXTREMELY_HIGH,
            (RiskProbability.A_FREQUENT, RiskSeverity.II_CRITICAL): RiskLevel.H_HIGH,
            (RiskProbability.A_FREQUENT, RiskSeverity.III_MODERATE): RiskLevel.H_HIGH,
            (RiskProbability.A_FREQUENT, RiskSeverity.IV_NEGLIGIBLE): RiskLevel.M_MEDIUM,
            (RiskProbability.B_LIKELY, RiskSeverity.I_CATASTROPHIC): RiskLevel.EH_EXTREMELY_HIGH,
            (RiskProbability.B_LIKELY, RiskSeverity.II_CRITICAL): RiskLevel.H_HIGH,
            (RiskProbability.B_LIKELY, RiskSeverity.III_MODERATE): RiskLevel.M_MEDIUM,
            (RiskProbability.B_LIKELY, RiskSeverity.IV_NEGLIGIBLE): RiskLevel.M_MEDIUM,
            (RiskProbability.C_OCCASIONAL, RiskSeverity.I_CATASTROPHIC): RiskLevel.H_HIGH,
            (RiskProbability.C_OCCASIONAL, RiskSeverity.II_CRITICAL): RiskLevel.H_HIGH,
            (RiskProbability.C_OCCASIONAL, RiskSeverity.III_MODERATE): RiskLevel.M_MEDIUM,
            (RiskProbability.C_OCCASIONAL, RiskSeverity.IV_NEGLIGIBLE): RiskLevel.L_LOW,
            (RiskProbability.D_SELDOM, RiskSeverity.I_CATASTROPHIC): RiskLevel.H_HIGH,
            (RiskProbability.D_SELDOM, RiskSeverity.II_CRITICAL): RiskLevel.M_MEDIUM,
            (RiskProbability.D_SELDOM, RiskSeverity.III_MODERATE): RiskLevel.L_LOW,
            (RiskProbability.D_SELDOM, RiskSeverity.IV_NEGLIGIBLE): RiskLevel.L_LOW,
            (RiskProbability.E_UNLIKELY, RiskSeverity.I_CATASTROPHIC): RiskLevel.M_MEDIUM,
            (RiskProbability.E_UNLIKELY, RiskSeverity.II_CRITICAL): RiskLevel.M_MEDIUM,
            (RiskProbability.E_UNLIKELY, RiskSeverity.III_MODERATE): RiskLevel.L_LOW,
            (RiskProbability.E_UNLIKELY, RiskSeverity.IV_NEGLIGIBLE): RiskLevel.L_LOW,
        }

        return matrix.get((probability, severity), RiskLevel.M_MEDIUM)

    def get_action_gate(self, risk_level: RiskLevel) -> str:
        """Get required action for risk level"""
        action_gates = {
            RiskLevel.EH_EXTREMELY_HIGH: "BLOCK (non-negotiable)",
            RiskLevel.H_HIGH: "CFO_approval_required",
            RiskLevel.M_MEDIUM: "Manager_approval",
            RiskLevel.L_LOW: "ALLOW",
        }
        return action_gates.get(risk_level, "Manager_approval")


@dataclass
class DecisionProtocol:
    """Purpose/Reason/Brakes decision framework"""

    purpose: str = "ShadowTag-v2JR mission alignment check"
    reason: str = "Doctrine compliance (SOPs A-D)"
    brakes: str = "Army RM risk assessment (ATP 5-19)"
    human_in_loop: list[str] = field(
        default_factory=lambda: [
            "High-risk actions",
            "Financial >$50K",
            "Customer-facing edge cases",
        ],
    )

    def validate_decision(
        self, action: str, mission_aligned: bool, doctrine_compliant: bool, risk_level: RiskLevel,
    ) -> tuple[bool, str]:
        """Validate decision through protocol"""
        # Check purpose
        if not mission_aligned:
            return False, f"REJECTED: {action} not aligned with ShadowTag-v2JR mission"

        # Check reason
        if not doctrine_compliant:
            return False, f"REJECTED: {action} violates doctrine (SOPs A-D)"

        # Check brakes
        matrix = RiskAssessmentMatrix()
        action_gate = matrix.get_action_gate(risk_level)

        if action_gate == "BLOCK (non-negotiable)":
            return False, f"BLOCKED: {action} has extremely high risk"

        return True, f"APPROVED: {action} ({action_gate})"


@dataclass
class DevelopmentConstraints:
    """Code style and development constraints"""

    max_function_length: int = 20
    external_libraries_approval: bool = True
    test_coverage_min: float = 0.80
    output_format: str = "monospace"

    shipping_philosophy: list[str] = field(
        default_factory=lambda: [
            "Stupid simple > fancy",
            "Ship fast > perfect",
            "Real utility > general-purpose",
            "Evidence-only decisions",
        ],
    )

    guardrails: list[str] = field(
        default_factory=lambda: [
            "No feature without user interview (n≥10)",
            "No new vertical without $5K+ pilot demand",
            "No hire without founder doing job 3+ months first",
        ],
    )

    def validate_function(self, line_count: int) -> bool:
        """Validate function meets constraints"""
        return line_count <= self.max_function_length

    def validate_test_coverage(self, coverage: float) -> bool:
        """Validate test coverage meets minimum"""
        return coverage >= self.test_coverage_min


@dataclass
class FrameworkReference:
    """Core framework and SOP references"""

    sop_a: str = "Upload Triage (2× speed, −90% errors)"
    sop_b: str = "Change & Release (2× cadence, clearer audits)"
    sop_c: str = "Decision Protocol (2× faster, +1.8× robustness)"
    sop_d: str = "Code Review (+2× defect capture)"
    atp_5_19: str = "Military risk management (probability × severity → action gates)"
    business_judgment: str = "Defensible decisions under uncertainty with evidence"
    boy_scout_rule: str = "Leave code cleaner than you found it"
    reality_distortion: str = "Treat impossibles as invitations to innovate"

    def get_all_frameworks(self) -> dict[str, str]:
        """Get all framework references"""
        return {
            "SOP_A": self.sop_a,
            "SOP_B": self.sop_b,
            "SOP_C": self.sop_c,
            "SOP_D": self.sop_d,
            "ATP_5_19": self.atp_5_19,
            "Business_Judgment": self.business_judgment,
            "Boy_Scout_Rule": self.boy_scout_rule,
            "Reality_Distortion": self.reality_distortion,
        }


class OperatingFramework:
    """Main operating system execution framework"""

    def __init__(self):
        self.risk_matrix = RiskAssessmentMatrix()
        self.decision_protocol = DecisionProtocol()
        self.constraints = DevelopmentConstraints()
        self.frameworks = FrameworkReference()

    def assess_action(
        self,
        action: str,
        probability: RiskProbability,
        severity: RiskSeverity,
        mission_aligned: bool,
        doctrine_compliant: bool,
    ) -> dict[str, any]:
        """Complete action assessment"""
        # Risk assessment
        risk_level = self.risk_matrix.assess(probability, severity)
        action_gate = self.risk_matrix.get_action_gate(risk_level)

        # Decision validation
        approved, message = self.decision_protocol.validate_decision(
            action, mission_aligned, doctrine_compliant, risk_level,
        )

        return {
            "action": action,
            "risk_level": risk_level.value,
            "action_gate": action_gate,
            "approved": approved,
            "message": message,
            "probability": probability.value,
            "severity": severity.value,
        }

    def validate_code(self, function_lines: int, test_coverage: float) -> dict[str, bool]:
        """Validate code against constraints"""
        return {
            "function_length_valid": self.constraints.validate_function(function_lines),
            "test_coverage_valid": self.constraints.validate_test_coverage(test_coverage),
            "max_lines": self.constraints.max_function_length,
            "min_coverage": self.constraints.test_coverage_min,
        }
