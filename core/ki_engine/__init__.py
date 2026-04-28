# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# Copyright 2026 ShadowTag AI. All rights reserved.
"""
KI Engine — Memory-Kernel-Inspired Knowledge Infrastructure
============================================================
Implements the 22-point adoption from mainion-ai/memory-kernel analysis.

Modules:
  schema     — Typed KI schema with confidence scoring, TTL, classification
  decay      — Temporal decay for recall ranking (ACT-R exponential)
  activation — Spreading activation (wander) for collision detection
  budget     — Token-budget-aware recall with type reservations
  views      — Auto-generated summary views (decisions, constraints, index)
  closure    — Operational closure metrics (Luhmann entanglement)
  events     — Event sourcing for KI mutations
  encrypt    — AES-256-GCM encryption for sensitive KIs
  isolation  — Per-agent isolation with shared namespace
  promotion  — Belief promotion pipeline (confidence → fact)
  conflict   — Conflict detection between contradicting KIs
  migration  — Migration script from KI format to memory-kernel atoms
"""

from core.ki_engine.schema import (
    KIType,
    KIStatus,
    KIClassification,
    KIMetadata,
    DEFAULT_TTLS,
    DEFAULT_TYPE_WEIGHTS,
)
from core.ki_engine.decay import temporal_decay, recall_score
from core.ki_engine.activation import spread_activation, detect_collisions
from core.ki_engine.budget import token_budget_recall
from core.ki_engine.closure import compute_closure, ClosureResult
from core.ki_engine.events import append_event, read_events, KIEvent

__all__ = [
    "KIType",
    "KIStatus",
    "KIClassification",
    "KIMetadata",
    "DEFAULT_TTLS",
    "DEFAULT_TYPE_WEIGHTS",
    "temporal_decay",
    "recall_score",
    "spread_activation",
    "detect_collisions",
    "token_budget_recall",
    "compute_closure",
    "ClosureResult",
    "append_event",
    "read_events",
    "KIEvent",
]
