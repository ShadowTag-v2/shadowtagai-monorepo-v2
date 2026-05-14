# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
SLA Moat + Pinkln Intelligence - Resilient AI Infrastructure

This package combines:

1. SLA MOAT (Infrastructure Resilience):
   4-layer failover system enabling p99≤90ms SLA guarantees
   - Layer 1: Gemini (primary)
   - Layer 2: Claude (backup)
   - Layer 3: GPT-5 (emergency)
   - Layer 4: Local PyTorch (deterministic)

2. PINKLN INTELLIGENCE (Self-Evolving AI):
   Multi-agent debates, Glicko-2 ratings, DTE evolution
   - Glicko-2: Dynamic provider ranking based on performance
   - DTE: Self-evolution loop (+3.7% accuracy per iteration)
   - MAD: Multi-agent debates for critical decisions
   - Cheat Sheet Fusion: Provider-optimized prompts

Key insight: An SLA is only as strong as its failover architecture.
Google can't offer SLAs (Gemini-only). Pnkln can (4-layer + intelligence).
"""

# Core failover engine
from .failover_engine import JREngineWithFailover, JudgeDecision, ProviderType, FailoverReason, FailoverEvent, TimeoutError, APIError

# Glicko-2 rating system
from .glicko2 import Glicko2Player, create_provider_ratings, update_provider_rating, get_ranked_providers, get_allocation_percentages

# DTE self-evolution framework
from .dte_evolution import DTEEvolutionEngine, BenchmarkType, BenchmarkResult, EvolutionIteration

# MAD multi-agent consensus
from .mad_consensus import MADEngine, MADConsensus, AgentVote, DebateRound, DecisionType

# Cheat sheet fusion (provider-optimized prompts)
from .cheat_sheet_fusion import CheatSheet, CheatSheetLibrary, CheatSheetFusion, GEMINI_PROFILE, CLAUDE_PROFILE, GPT5_PROFILE, LOCAL_PROFILE

# Integrated components (Month 1 integration)
from .glicko_failover import GlickoEnhancedFailover
from .dte_local_trainer import DTELocalModelTrainer, ModelCheckpoint
from .mad_decision_engine import MADDecisionEngine
from .integrated_judge import IntegratedJudge, IntegratedDecisionMetrics

__version__ = "2.1.0"  # Minor version bump for Month 1 integration
__author__ = "Pnkln Engineering Team"

__all__ = [
    # Failover engine
    "JREngineWithFailover",
    "JudgeDecision",
    "ProviderType",
    "FailoverReason",
    "FailoverEvent",
    "TimeoutError",
    "APIError",
    # Glicko-2 ratings
    "Glicko2Player",
    "create_provider_ratings",
    "update_provider_rating",
    "get_ranked_providers",
    "get_allocation_percentages",
    # DTE evolution
    "DTEEvolutionEngine",
    "BenchmarkType",
    "BenchmarkResult",
    "EvolutionIteration",
    # MAD consensus
    "MADEngine",
    "MADConsensus",
    "AgentVote",
    "DebateRound",
    "DecisionType",
    # Cheat sheet fusion
    "CheatSheet",
    "CheatSheetLibrary",
    "CheatSheetFusion",
    "GEMINI_PROFILE",
    "CLAUDE_PROFILE",
    "GPT5_PROFILE",
    "LOCAL_PROFILE",
    # Integrated components (Month 1)
    "GlickoEnhancedFailover",
    "DTELocalModelTrainer",
    "ModelCheckpoint",
    "MADDecisionEngine",
    "IntegratedJudge",
    "IntegratedDecisionMetrics",
]
