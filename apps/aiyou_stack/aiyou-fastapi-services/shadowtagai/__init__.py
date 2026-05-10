# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""SHADOWTAGAI - Precision AI Orchestration Platform
============================================

Core modules:
- core.cor_orchestrator: Event-driven orchestration engine (<1ms p99)
- core.jr_engine: ATP 5-19 risk assessment framework (<500μs)
- core.judge_six: Hybrid validation pipeline (p99≤90ms SLA)
- tools: Standardized LangGraph tool schemas

Version: 1.0.0
Architecture: SK-inspired patterns adapted for GKE/Python/MCP stack
"""

from __future__ import annotations

__version__ = "1.0.0"
__author__ = "ShadowTagAi Architecture Team"


def __getattr__(name: str):
    """Lazy re-exports to break circular imports with pnkln.core."""
    if name == "JudgeSixPipeline":
        from pnkln.core.judge_six_pipeline import JudgeSixPipeline

        return JudgeSixPipeline
    if name == "CorOrchestrator":
        from pnkln.core.cor_orchestrator import CorOrchestrator

        return CorOrchestrator
    if name == "JREngine":
        from shadowtagai.core.jr_engine import JREngine

        return JREngine
    raise AttributeError(f"module 'shadowtagai' has no attribute {name!r}")


__all__ = [
    "CorOrchestrator",
    "JREngine",
    "JudgeSixPipeline",
]
