# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""ShadowTagAi Core Orchestration Components
====================================

SK-inspired patterns adapted for ShadowTagAi constraints:
- Pattern 1: Sequential Pipeline (Judge 6 validation)
- Pattern 2: Concurrent Execution (Monte Carlo risk)
- Pattern 3: Plugin Schema Standardization (LangGraph tools)
"""

from __future__ import annotations


def __getattr__(name: str):
    """Lazy re-exports to break circular imports with pnkln.core."""
    _lazy_map = {
        "JudgeSixPipeline": ("pnkln.core.judge_six_pipeline", "JudgeSixPipeline"),
        "ValidationResult": ("pnkln.core.judge_six_pipeline", "ValidationResult"),
        "CorOrchestrator": ("pnkln.core.cor_orchestrator", "CorOrchestrator"),
        "ExecutionContext": ("pnkln.core.cor_orchestrator", "ExecutionContext"),
        "JREngine": ("shadowtagai.core.jr_engine", "JREngine"),
        "ProbabilityLevel": ("shadowtagai.core.jr_engine", "ProbabilityLevel"),
        "RiskLevel": ("shadowtagai.core.jr_engine", "RiskLevel"),
        "SeverityLevel": ("shadowtagai.core.jr_engine", "SeverityLevel"),
        "MonteCarloRiskAssessment": (
            "shadowtagai.core.monte_carlo_risk",
            "MonteCarloRiskAssessment",
        ),
    }
    if name in _lazy_map:
        import importlib

        mod_path, attr = _lazy_map[name]
        mod = importlib.import_module(mod_path)
        return getattr(mod, attr)
    raise AttributeError(f"module 'shadowtagai.core' has no attribute {name!r}")


__all__ = [
    "CorOrchestrator",
    "ExecutionContext",
    "JREngine",
    "JudgeSixPipeline",
    "MonteCarloRiskAssessment",
    "ProbabilityLevel",
    "RiskLevel",
    "SeverityLevel",
    "ValidationResult",
]
