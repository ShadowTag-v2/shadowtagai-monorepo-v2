# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Cor.53 Constitutional Layer - Immutable Governance Axioms

These axioms form the foundational governance rules that cannot be
overridden by user input, preferences, or runtime configuration.
"""

from Claude_Code_6.models import ConstitutionalAxiom, RiskLevel

# Cor.53 Constitutional Layer - IMMUTABLE
COR53_AXIOMS: list[ConstitutionalAxiom] = [
    ConstitutionalAxiom(
        axiom_id="A1",
        name="PURPOSE_REQUIRED",
        rule="All requests must declare explicit purpose before processing",
        enforcement_level="IMMUTABLE",
        violation_consequence=RiskLevel.RA_3,
    ),
    ConstitutionalAxiom(
        axiom_id="A2",
        name="HARM_PROHIBITION",
        rule="No output may facilitate harm per ATP 5-19 RA-3/RA-4 classification",
        enforcement_level="IMMUTABLE",
        violation_consequence=RiskLevel.RA_4,
    ),
    ConstitutionalAxiom(
        axiom_id="A3",
        name="PROVENANCE_MANDATORY",
        rule="All decisions require ShadowTag 2.0 cryptographic signature",
        enforcement_level="IMMUTABLE",
        violation_consequence=RiskLevel.RA_2,
    ),
    ConstitutionalAxiom(
        axiom_id="A4",
        name="REASONS_DOCUMENTED",
        rule="Reasoning chains must be embedded and cryptographically signed",
        enforcement_level="IMMUTABLE",
        violation_consequence=RiskLevel.RA_2,
    ),
    ConstitutionalAxiom(
        axiom_id="A5",
        name="AUDIT_TRAIL",
        rule="Full decision provenance must be retained for regulatory compliance",
        enforcement_level="IMMUTABLE",
        violation_consequence=RiskLevel.RA_3,
    ),
    ConstitutionalAxiom(
        axiom_id="A6",
        name="NO_USER_OVERRIDE",
        rule="User preferences/styles CANNOT override constitutional axioms",
        enforcement_level="IMMUTABLE",
        violation_consequence=RiskLevel.RA_4,
    ),
]


# Create axiom lookup dictionary for fast access
AXIOM_BY_ID = {axiom.axiom_id: axiom for axiom in COR53_AXIOMS}


def get_axiom(axiom_id: str) -> ConstitutionalAxiom:
    """Retrieve constitutional axiom by ID.

    Args:
        axiom_id: Axiom identifier (e.g., "A1")

    Returns:
        ConstitutionalAxiom instance

    Raises:
        KeyError: If axiom_id not found

    """
    if axiom_id not in AXIOM_BY_ID:
        raise KeyError(f"Unknown axiom ID: {axiom_id}")
    return AXIOM_BY_ID[axiom_id]


def get_immutable_axioms() -> list[ConstitutionalAxiom]:
    """Get all axioms with IMMUTABLE enforcement level.

    Returns:
        List of immutable constitutional axioms

    """
    return [ax for ax in COR53_AXIOMS if ax.enforcement_level == "IMMUTABLE"]


def get_axioms_by_risk_level(risk_level: RiskLevel) -> list[ConstitutionalAxiom]:
    """Get all axioms that result in specified risk level if violated.

    Args:
        risk_level: Target risk level

    Returns:
        List of matching constitutional axioms

    """
    return [ax for ax in COR53_AXIOMS if ax.violation_consequence == risk_level]
