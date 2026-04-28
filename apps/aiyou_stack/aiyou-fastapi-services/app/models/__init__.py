# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Data models for kernel chain."""

from .decision import DecisionContext, DecisionResult, RiskTier, Violation
from .intel_event import (
    ChangeType,
    DeltaResult,
    DocumentType,
    Impact,
    IntelEvent,
    IntelEventBatch,
    JRHints,
    RiskTag,
)
from .kernel import KernelInput, KernelMetrics, KernelOutput

__all__ = [
    "KernelInput",
    "KernelOutput",
    "KernelMetrics",
    "DecisionContext",
    "Violation",
    "RiskTier",
    "DecisionResult",
    # Intel Event models
    "IntelEvent",
    "IntelEventBatch",
    "DeltaResult",
    "DocumentType",
    "ChangeType",
    "RiskTag",
    "JRHints",
    "Impact",
]
