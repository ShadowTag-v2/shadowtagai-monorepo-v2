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

__version__ = "1.0.0"
__author__ = "ShadowTagAi Architecture Team"

from pnkln.core.judge_six_pipeline import JudgeSixPipeline

from pnkln.core.cor_orchestrator import CorOrchestrator
from shadowtagai.core.jr_engine import JREngine

__all__ = [
    "CorOrchestrator",
    "JREngine",
    "JudgeSixPipeline",
]
