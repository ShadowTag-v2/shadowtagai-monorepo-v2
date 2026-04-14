"""ATP 5-19: Composite Risk Management — Scaffolded Stubs
=========================================================

Provides the Army Doctrine constants for the Judge Architecture.
Based on ATP 5-19 (Composite Risk Management), FM 6-0, FM 7-8.

STATUS: Scaffold (Phase 1)
"""

from enum import Enum


class Probability(Enum):
    """ATP 5-19 Table 1-1: Probability levels."""

    FREQUENT = "A"
    LIKELY = "B"
    OCCASIONAL = "C"
    SELDOM = "D"
    UNLIKELY = "E"


class Severity(Enum):
    """ATP 5-19 Table 1-2: Severity categories."""

    CATASTROPHIC = "I"
    CRITICAL = "II"
    MARGINAL = "III"
    NEGLIGIBLE = "IV"


# Forward import to avoid circular — use the local RiskLevel
# This is resolved at init time from the parent package
def _get_risk_level():
    """Lazy import to break circular dependency."""
    from src.kosmos.doctrine import RiskLevel
    return RiskLevel


def _build_risk_matrix():
    """ATP 5-19 Figure 1-3: Risk Assessment Matrix.

    Maps (Probability, Severity) → RiskLevel.
    Lazily built to avoid circular imports.
    """
    RL = _get_risk_level()
    return {
        (Probability.FREQUENT, Severity.CATASTROPHIC): RL.EXTREMELY_HIGH,
        (Probability.FREQUENT, Severity.CRITICAL): RL.EXTREMELY_HIGH,
        (Probability.FREQUENT, Severity.MARGINAL): RL.HIGH,
        (Probability.FREQUENT, Severity.NEGLIGIBLE): RL.MEDIUM,
        (Probability.LIKELY, Severity.CATASTROPHIC): RL.EXTREMELY_HIGH,
        (Probability.LIKELY, Severity.CRITICAL): RL.HIGH,
        (Probability.LIKELY, Severity.MARGINAL): RL.HIGH,
        (Probability.LIKELY, Severity.NEGLIGIBLE): RL.MEDIUM,
        (Probability.OCCASIONAL, Severity.CATASTROPHIC): RL.EXTREMELY_HIGH,
        (Probability.OCCASIONAL, Severity.CRITICAL): RL.HIGH,
        (Probability.OCCASIONAL, Severity.MARGINAL): RL.MEDIUM,
        (Probability.OCCASIONAL, Severity.NEGLIGIBLE): RL.LOW,
        (Probability.SELDOM, Severity.CATASTROPHIC): RL.HIGH,
        (Probability.SELDOM, Severity.CRITICAL): RL.MEDIUM,
        (Probability.SELDOM, Severity.MARGINAL): RL.LOW,
        (Probability.SELDOM, Severity.NEGLIGIBLE): RL.LOW,
        (Probability.UNLIKELY, Severity.CATASTROPHIC): RL.MEDIUM,
        (Probability.UNLIKELY, Severity.CRITICAL): RL.MEDIUM,
        (Probability.UNLIKELY, Severity.MARGINAL): RL.LOW,
        (Probability.UNLIKELY, Severity.NEGLIGIBLE): RL.LOW,
    }


class _LazyRiskMatrix:
    """Lazy-loaded risk matrix to break import cycle."""

    def __init__(self):
        self._matrix = None

    def _load(self):
        if self._matrix is None:
            self._matrix = _build_risk_matrix()

    def get(self, key, default=None):
        self._load()
        return self._matrix.get(key, default)

    def __getitem__(self, key):
        self._load()
        return self._matrix[key]


class _LazyConsensusThresholds:
    """Lazy-loaded consensus thresholds to break import cycle."""

    def __init__(self):
        self._thresholds = None

    def _load(self):
        if self._thresholds is None:
            RL = _get_risk_level()
            self._thresholds = {
                RL.LOW: 0.50,
                RL.MEDIUM: 0.60,
                RL.HIGH: 0.75,
                RL.EXTREMELY_HIGH: 0.90,
            }

    def get(self, key, default=None):
        self._load()
        return self._thresholds.get(key, default)


class _LazyApprovalAuth:
    """Lazy-loaded approval authority to break import cycle."""

    def __init__(self):
        self._auth = None

    def _load(self):
        if self._auth is None:
            RL = _get_risk_level()
            self._auth = {
                RL.LOW: "Squad Leader",
                RL.MEDIUM: "Platoon Leader",
                RL.HIGH: "Company Commander",
                RL.EXTREMELY_HIGH: "Battalion Commander",
            }

    def get(self, key, default=None):
        self._load()
        return self._auth.get(key, default)


# Lazy singletons — no top-level RiskLevel import required
RISK_MATRIX = _LazyRiskMatrix()
CONSENSUS_THRESHOLDS = _LazyConsensusThresholds()
APPROVAL_AUTHORITY = _LazyApprovalAuth()
