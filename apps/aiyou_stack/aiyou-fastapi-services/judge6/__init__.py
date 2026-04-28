# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""PNKLN Judge 6 - AI Governance & Risk Management System
========================================================

A cryptographically-enforced AI governance framework implementing:
- Cor.53 Constitutional Axioms (immutable governance rules)
- ATP 5-19 Risk Stratification
- ShadowTag 2.0 Provenance System
- Six-Gate Evaluation Process

Author: Erik Bjontegard, Pnkln
Version: 2.0.0
"""

from judge6.constitutional import COR53_AXIOMS, ConstitutionalAxiom
from judge6.judgment import JudgmentRule
from judge6.models import JudgmentDecision, RiskLevel
from judge6.provenance import ProvenanceStamp, ShadowTagEngine
from judge6.risk_manager import YourRiskManager

__version__ = "2.0.0"
__author__ = "Erik Bjontegard, Pnkln"

__all__ = [
    "COR53_AXIOMS",
    "ConstitutionalAxiom",
    "JudgmentDecision",
    "JudgmentRule",
    "ProvenanceStamp",
    "RiskLevel",
    "ShadowTagEngine",
    "YourRiskManager",
]
