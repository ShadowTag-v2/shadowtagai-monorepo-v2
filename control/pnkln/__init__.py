# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
pnkln - Ultrathink Framework
Re-exports from shadowtagai.core for backwards compatibility.
Gracefully degrades when shadowtagai namespace is not installed.
"""

try:
  from shadowtagai.core.orchestrator import (
    MonetizationMetrics,
    ReasoningFramework,
    RiskLevel,
    create_orchestrator,
    pnklnOrchestrator,
  )

  __all__ = [
    "pnklnOrchestrator",
    "create_orchestrator",
    "RiskLevel",
    "ReasoningFramework",
    "MonetizationMetrics",
  ]
except (ImportError, ModuleNotFoundError):
  # shadowtagai namespace not available — submodules (legal, jurisdiction)
  # remain importable directly via control.pnkln.pnkln_core.*
  __all__ = []
