# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
# judge6_atp519_scoring.py — Public API re-export
# Canonical implementation: Cor_Claude_Code_6_atp519_scoring.py
# This module provides the stable import path used by the test suite.

from apps.counselconduit.Cor_Claude_Code_6_atp519_scoring import (
    PROBABILITY_LEVELS,
    RISK_MATRIX,
    SEVERITY_LEVELS,
    score_risk,
)

__all__ = [
    "score_risk",
    "RISK_MATRIX",
    "SEVERITY_LEVELS",
    "PROBABILITY_LEVELS",
]
