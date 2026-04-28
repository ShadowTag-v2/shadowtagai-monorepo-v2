# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

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
    "COMPLIANCE_THRESHOLD",
    "FAIL_FAST_THRESHOLD",
    "MAX_ITERATIONS",
    "TIMEOUT_SECONDS",
    "ComplianceReport",
    "Severity",
    "TDDRedPhaseAgent",
    "TestOutput",
    "Violation",
    "run_tdd_red_phase",
]
