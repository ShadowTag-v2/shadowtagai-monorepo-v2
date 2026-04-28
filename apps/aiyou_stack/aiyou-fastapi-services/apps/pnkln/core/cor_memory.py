# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""COR MEMORY - Orchestrator Memory System
=========================================

Extracted from cor_orchestrator.py as part of the Rich Hickey refactor.

DeepAgent Pattern: Scalable memory mechanism
- Short-term: Recent execution contexts
- Long-term: Compressed summaries (thread_rollup style)
- Episodic: Key decision points

Author: Pnkln Architecture Team
"""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any

from .cor_context import ExecutionContext

logger = logging.getLogger(__name__)


class OrchestratorMemory:
    """Memory system for orchestrator context persistence.

    DeepAgent Pattern: Scalable memory mechanism
    - Short-term: Recent execution contexts
    - Long-term: Compressed summaries (thread_rollup style)
    - Episodic: Key decision points
    """

    def __init__(self, max_short_term: int = 100, compression_ratio: float = 0.02):
        self.short_term: list[dict[str, Any]] = []
        self.long_term: list[dict[str, Any]] = []
        self.episodic: dict[str, dict[str, Any]] = {}
        self.max_short_term = max_short_term
        self.compression_ratio = compression_ratio  # 47:1 = ~0.02

    def store(self, context: ExecutionContext, result: Any, importance: float = 0.5) -> None:
        """Store execution in memory."""
        memory_item = {
            "request_id": context.request_id,
            "timestamp": context.timestamp.isoformat(),
            "latency_ms": context.total_latency_ms,
            "stage_latencies": context.stage_latencies,
            "variables": context.variables,
            "result_summary": str(result)[:500],  # Truncate for efficiency
            "importance": importance,
        }

        self.short_term.append(memory_item)

        # Compress to long-term when short-term is full
        if len(self.short_term) >= self.max_short_term:
            self._compress_to_long_term()

        # Store episodic if high importance
        if importance > 0.8:
            self.episodic[context.request_id] = memory_item

    def _compress_to_long_term(self) -> None:
        """Compress short-term memories to long-term (47:1 ratio)."""
        if not self.short_term:
            return

        # Aggregate statistics
        total_latency = sum(m["latency_ms"] for m in self.short_term)
        avg_latency = total_latency / len(self.short_term)

        # Extract patterns
        stage_counts: dict[str, int] = defaultdict(int)
        for m in self.short_term:
            for stage in m["stage_latencies"]:
                stage_counts[stage] += 1

        compressed = {
            "period_start": self.short_term[0]["timestamp"],
            "period_end": self.short_term[-1]["timestamp"],
            "execution_count": len(self.short_term),
            "avg_latency_ms": avg_latency,
            "total_latency_ms": total_latency,
            "stage_frequency": dict(stage_counts),
            "compression_ratio": len(self.short_term),  # N:1 compression
        }

        self.long_term.append(compressed)
        self.short_term = []

    def retrieve_context(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Retrieve relevant memories for context.

        Simple keyword matching (replace with embeddings in production).
        """
        results = []

        # Search short-term
        for memory in self.short_term:
            if query.lower() in str(memory).lower():
                results.append(memory)

        # Search episodic
        for _rid, memory in self.episodic.items():
            if query.lower() in str(memory).lower():
                results.append(memory)

        return results[:top_k]

    def get_summary(self) -> dict[str, Any]:
        """Get memory system summary."""
        return {
            "short_term_count": len(self.short_term),
            "long_term_count": len(self.long_term),
            "episodic_count": len(self.episodic),
            "total_compressions": len(self.long_term),
        }
