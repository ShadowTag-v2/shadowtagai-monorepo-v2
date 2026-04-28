# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# DOCTRINE: ATP 5-19 Risk Management (US Army / Judge 6)
# SOURCE: Drive Docs (ATP 5-19 Risk Management.pdf)
# PURPOSE: "Jr Engine" Risk Assessment (Physical / Kinetic / Operational Only)
# NOTE: Superseded for Cyber Risk (Use NIST/RMF for Cyber Domains)

from enum import Enum


class RiskLevel(Enum):
    EXTREMELY_HIGH = "EH"
    HIGH = "H"
    MEDIUM = "M"
    LOW = "L"


class Probability(Enum):
    FREQUENT = "A"
    LIKELY = "B"
    OCCASIONAL = "C"
    SELDOM = "D"
    UNLIKELY = "E"


class Severity(Enum):
    CATASTROPHIC = "I"
    CRITICAL = "II"
    MODERATE = "III"
    NEGLIGIBLE = "IV"


# The Matrix (Standard Army Risk Assessment Matrix)
RISK_MATRIX = {
    (Probability.FREQUENT, Severity.CATASTROPHIC): RiskLevel.EXTREMELY_HIGH,
    (Probability.FREQUENT, Severity.CRITICAL): RiskLevel.EXTREMELY_HIGH,
    (Probability.FREQUENT, Severity.MODERATE): RiskLevel.HIGH,
    (Probability.FREQUENT, Severity.NEGLIGIBLE): RiskLevel.MEDIUM,
    (Probability.LIKELY, Severity.CATASTROPHIC): RiskLevel.EXTREMELY_HIGH,
    (Probability.LIKELY, Severity.CRITICAL): RiskLevel.HIGH,
    (Probability.LIKELY, Severity.MODERATE): RiskLevel.HIGH,
    (Probability.LIKELY, Severity.NEGLIGIBLE): RiskLevel.LOW,
    # ... Simplified for code brevity, full matrix implemented in logic
}


def assess_risk(prob: Probability, sev: Severity) -> RiskLevel:
    """Calculates Risk Level based on ATP 5-19 Matrix."""
    if prob == Probability.FREQUENT:
        if sev == Severity.CATASTROPHIC or sev == Severity.CRITICAL:
            return RiskLevel.EXTREMELY_HIGH
        if sev == Severity.MODERATE:
            return RiskLevel.HIGH
        return RiskLevel.MEDIUM

    if prob == Probability.LIKELY:
        if sev == Severity.CATASTROPHIC:
            return RiskLevel.EXTREMELY_HIGH
        if sev == Severity.CRITICAL or sev == Severity.MODERATE:
            return RiskLevel.HIGH
        return RiskLevel.LOW

    if prob == Probability.OCCASIONAL:
        if sev == Severity.CATASTROPHIC:
            return RiskLevel.HIGH
        if sev == Severity.CRITICAL:
            return RiskLevel.HIGH
        if sev == Severity.MODERATE:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    if prob == Probability.SELDOM:
        if sev == Severity.CATASTROPHIC:
            return RiskLevel.HIGH
        if sev == Severity.CRITICAL:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    # UNLIKELY
    if sev == Severity.CATASTROPHIC:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


def judge_action(action_context: str) -> RiskLevel:
    """Mock function to map an agent action to a risk level.
    In a real system, Gemini classifies the text into Prob/Sev buckets.
    """
    # Placeholder logic
    if "deploy" in action_context or "delete" in action_context:
        return assess_risk(Probability.OCCASIONAL, Severity.CRITICAL)  # High Risk
    return assess_risk(Probability.UNLIKELY, Severity.NEGLIGIBLE)  # Low Risk
