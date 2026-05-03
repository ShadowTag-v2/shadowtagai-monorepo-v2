# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""agnt_compact — Thin re-export shim for the Context Compaction pipeline.

The full implementation lives in ``packages/context_compactor/``.
This package provides the ``agnt_compact`` namespace for backward
compatibility with scaffolding references and import paths.

4-Layer Context Compaction Pipeline (ported from Claude Code v2.1.91):
  Layer 1: Strip — Remove non-essential whitespace and comments
  Layer 2: Summarize — PTL-powered abstract summarization
  Layer 3: Evict — LRU eviction of least-recently-used context blocks
  Layer 4: Truncate — Hard token budget enforcement

Usage:
    from agnt_compact import ContextCompactor, CompactionResult
    compactor = ContextCompactor(max_tokens=128_000)
    result = compactor.compact(messages)
"""

from __future__ import annotations

try:
    from context_compactor.compactor import ContextCompactor
    from context_compactor.conversation_compact import (
        CompactionConfig,
        CompactionResult,
        compact_conversation,
    )
except ImportError:
    # Graceful degradation if context_compactor not importable
    ContextCompactor = None  # type: ignore[assignment, misc]
    CompactionConfig = None  # type: ignore[assignment, misc]
    CompactionResult = None  # type: ignore[assignment, misc]
    compact_conversation = None  # type: ignore[assignment]

__all__ = [
    "CompactionConfig",
    "CompactionResult",
    "ContextCompactor",
    "compact_conversation",
]
