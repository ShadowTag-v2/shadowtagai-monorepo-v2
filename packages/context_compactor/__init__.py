# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""AGNT 4-Layer Context Compaction Pipeline.

Ported from Claude Code v2.1.91 forensic audit (AGNT STATE B Spec P1.1).
Implements a 4-layer progressive compaction strategy:

  L1: Cached Microcompaction — Prune old tool results without breaking prompt cache
  L2: Time-Based MC          — Replace stale results after idle threshold
  L3: API Context Management  — Server-side context window manipulation
  L4: Full Compaction         — Circuit-breaker + LLM summarization fallback

Reference: agnt_state_b_implementation_spec.md P1.1
"""

from packages.context_compactor.compactor import ContextCompactor
from packages.context_compactor.layers import (
    Layer1CachedMC,
    Layer2TimeBased,
    Layer3APIManagement,
    Layer4FullCompaction,
)

__all__ = [
    "ContextCompactor",
    "Layer1CachedMC",
    "Layer2TimeBased",
    "Layer3APIManagement",
    "Layer4FullCompaction",
]
