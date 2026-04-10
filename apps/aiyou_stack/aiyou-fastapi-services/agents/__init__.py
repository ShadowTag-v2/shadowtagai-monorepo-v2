"""TDD Agents - Hybrid architecture with embedded validation."""

from .tdd_red_phase import (
    COMPLIANCE_THRESHOLD,
    FAIL_FAST_THRESHOLD,
    MAX_ITERATIONS,
    TIMEOUT_SECONDS,
    ComplianceReport,
    Severity,
    TDDRedPhaseAgent,
    TestOutput,
    Violation,
    run_tdd_red_phase,
)

__all__ = [
    "TDDRedPhaseAgent",
    "run_tdd_red_phase",
    "ComplianceReport",
    "TestOutput",
    "Violation",
    "Severity",
    "COMPLIANCE_THRESHOLD",
    "MAX_ITERATIONS",
    "TIMEOUT_SECONDS",
    "FAIL_FAST_THRESHOLD",
]
