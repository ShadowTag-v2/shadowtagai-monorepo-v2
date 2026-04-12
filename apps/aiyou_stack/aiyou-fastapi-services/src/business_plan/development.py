"""
Development Constraints & Operational Frameworks
SOPs, coding standards, and shipping philosophy
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DevelopmentConstraints:
    """Code quality & architecture constraints"""

    max_function_length: int = 20  # lines
    external_libraries_approval: bool = True  # Require approval
    test_coverage_minimum: float = 0.80  # 80% on critical paths
    output_format: str = "monospace for all technical content"

    shipping_philosophy: list[str] = field(
        default_factory=lambda: [
            "Stupid simple > fancy",
            "Ship fast > perfect",
            "Real utility > general-purpose",
            "Evidence-only decisions",
        ]
    )

    guardrails: list[str] = field(
        default_factory=lambda: [
            "No feature without user interview (n≥10)",
            "No new vertical without $5K+ pilot demand",
            "No hire without founder doing job 3+ months first",
        ]
    )

    def validate_function(self, lines: int) -> bool:
        """Check if function meets length constraint"""
        return lines <= self.max_function_length

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_func_lines": self.max_function_length,
            "require_lib_approval": self.external_libraries_approval,
            "test_coverage": self.test_coverage_minimum,
            "philosophy": self.shipping_philosophy,
            "guardrails": self.guardrails,
        }


@dataclass
class Frameworks:
    """Referenced operational frameworks & SOPs"""

    sop_a: str = "Upload Triage (2× speed, −90% errors)"
    sop_b: str = "Change & Release (2× cadence, clearer audits)"
    sop_c: str = "Decision Protocol (2× faster, +1.8× robustness)"
    sop_d: str = "Code Review (+2× defect capture)"

    atp_5_19: str = "Military risk management (probability × severity → gates)"
    business_judgment_rule: str = "Defensible decisions under uncertainty"
    boy_scout_rule: str = "Leave code cleaner than you found it"
    reality_distortion_field: str = "Treat impossibles as invitations to innovate"

    def to_dict(self) -> dict[str, str]:
        return {
            "sop_a": self.sop_a,
            "sop_b": self.sop_b,
            "sop_c": self.sop_c,
            "sop_d": self.sop_d,
            "atp_5_19": self.atp_5_19,
            "business_judgment": self.business_judgment_rule,
            "boy_scout": self.boy_scout_rule,
            "reality_distortion": self.reality_distortion_field,
        }


@dataclass
class OperatingPrinciples:
    """Core operating tenets"""

    iq_baseline: int = 160  # Board-level strategic thinking
    mode: str = "Strict (default)"
    security_posture: str = "100% operational gate (non-negotiable)"

    principles: list[str] = field(
        default_factory=lambda: [
            "Purpose=ShadowTag-v2JR • Reason=Doctrine • Brakes=Army RM",
            "Evidence-only (n≥10 user interviews before features)",
            "Bootstrap discipline: ROI ≥3× (18mo), LTV:CAC ≥4:1 (12mo)",
            "Revenue doctrine: Every feature = 'Does this make money faster?'",
            "Boy Scout Rule: Ship clean, war-game architectures, document beautifully",
            "Reality Distortion: Impossibles are invitations to innovate",
        ]
    )

    research_deltas: list[str] = field(
        default_factory=lambda: [
            "RoT: retrieval-of-thought (40% token↓ / 59% cost↓)",
            "GAIN-RL: train on useful examples first (≈2.5× faster)",
            "RLAD/Abstractions: two-stage RL (invent + reuse hints)",
            "RLP (NVIDIA): dense per-token rewards (up to +35%)",
            "Set-RL: entropy collapse guard via trajectory sets",
            "Bridge/Interdependent: ~2.8–5.1% params → +50% accuracy",
            "ICoT: implicit chain-of-thought (100% on 4×4 multiplication)",
            "MoE economics: expert-parallel + KV compression",
        ]
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "iq_baseline": self.iq_baseline,
            "mode": self.mode,
            "security": self.security_posture,
            "principles": self.principles,
            "research": self.research_deltas,
        }


@dataclass
class BootstrapDiscipline:
    """Financial constraints for unfunded operation"""

    roi_minimum: float = 3.0  # 3× ROI in 18 months
    ltv_cac_minimum: float = 4.0  # 4:1 ratio in 12 months
    payback_period_max_months: int = 6  # Max customer payback

    constraints: list[str] = field(
        default_factory=lambda: [
            "No funding until unit economics proven",
            "Kill-switches enforced at Month 3, 6, 12",
            "No hire without founder doing job 3+ months",
            "No feature without n≥10 user validation",
        ]
    )

    def validate_economics(self, ltv: float, cac: float) -> bool:
        """Check if unit economics meet threshold"""
        if cac == 0:
            return False
        return (ltv / cac) >= self.ltv_cac_minimum

    def to_dict(self) -> dict[str, Any]:
        return {
            "roi_min": self.roi_minimum,
            "ltv_cac_min": self.ltv_cac_minimum,
            "payback_max": self.payback_period_max_months,
            "constraints": self.constraints,
        }


# Singleton instances
DEV_CONSTRAINTS = DevelopmentConstraints()
FRAMEWORKS = Frameworks()
OPERATING_PRINCIPLES = OperatingPrinciples()
BOOTSTRAP_DISCIPLINE = BootstrapDiscipline()
