# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""COR Tools — Dynamic Tool Registry with Semantic Retrieval
==========================================================

Extracted from cor_orchestrator.py (Rich Hickey refactor).

DeepAgent Pattern: Scalable tool retrieval from large toolsets
- Embedding-based similarity search
- Performance-weighted ranking
- Usage tracking for RL optimization

Author: Pnkln Architecture Team
Version: 2.0.0 — Rich Hickey Refactor
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class Tool:
    """Tool definition with embedding for semantic retrieval."""

    name: str
    description: str
    func: Callable
    embedding: np.ndarray | None = None
    usage_count: int = 0
    success_rate: float = 1.0
    avg_latency_ms: float = 0.0

    def update_metrics(self, success: bool, latency_ms: float) -> None:
        """Update tool performance metrics."""
        self.usage_count += 1
        # Exponential moving average for success rate
        alpha = 0.1
        self.success_rate = (1 - alpha) * self.success_rate + alpha * (1.0 if success else 0.0)
        self.avg_latency_ms = (1 - alpha) * self.avg_latency_ms + alpha * latency_ms


class ToolRegistry:
    """Dynamic tool registry with semantic retrieval.

    DeepAgent Pattern: Scalable tool retrieval from large toolsets
    - Embedding-based similarity search
    - Performance-weighted ranking
    - Usage tracking for RL optimization
    """

    def __init__(self, embedding_dim: int = 384):
        self.tools: dict[str, Tool] = {}
        self.embedding_dim = embedding_dim
        self._embedding_matrix: np.ndarray | None = None
        self._tool_names: list[str] = []

    def register_tool(
        self,
        name: str,
        description: str,
        func: Callable,
        embedding: np.ndarray | None = None,
    ) -> None:
        """Register tool with optional embedding."""
        if embedding is None:
            embedding = self._simple_embedding(description)

        self.tools[name] = Tool(name=name, description=description, func=func, embedding=embedding)
        self._rebuild_index()
        logger.info(f"Registered tool: {name}")

    def _simple_embedding(self, text: str) -> np.ndarray:
        """Simple embedding placeholder (replace with real embeddings in production)."""
        np.random.seed(hash(text) % (2**32))
        return np.random.randn(self.embedding_dim).astype(np.float32)

    def _rebuild_index(self) -> None:
        """Rebuild embedding index for fast retrieval."""
        self._tool_names = list(self.tools.keys())
        if self._tool_names:
            from typing import cast

            self._embedding_matrix = np.vstack(
                cast("list[np.ndarray]", [self.tools[name].embedding for name in self._tool_names]),
            )

    def retrieve_tools(
        self,
        query: str,
        top_k: int = 5,
        min_similarity: float = 0.0,
    ) -> list[tuple[str, float]]:
        """Retrieve most relevant tools for query.

        Args:
            query: Natural language query
            top_k: Number of tools to return
            min_similarity: Minimum similarity threshold

        Returns:
            List of (tool_name, similarity_score) tuples

        """
        if not self._tool_names or self._embedding_matrix is None:
            return []

        query_embedding = self._simple_embedding(query)

        # Cosine similarity
        norms = np.linalg.norm(self._embedding_matrix, axis=1) * np.linalg.norm(query_embedding)
        similarities = np.dot(self._embedding_matrix, query_embedding) / (norms + 1e-8)

        # Performance-weighted ranking
        performance_weights = np.array(
            [
                self.tools[name].success_rate
                * (1.0 / (1.0 + self.tools[name].avg_latency_ms / 100))
                for name in self._tool_names
            ],
        )
        weighted_scores = similarities * 0.7 + performance_weights * 0.3

        # Get top-k
        top_indices = np.argsort(weighted_scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(weighted_scores[idx])
            if score >= min_similarity:
                results.append((self._tool_names[idx], score))

        return results

    def get_tool(self, name: str) -> Tool | None:
        """Get tool by name."""
        return self.tools.get(name)

    async def execute_tool(self, name: str, *args, **kwargs) -> tuple[Any, float]:
        """Execute tool and track metrics.

        Returns:
            Tuple of (result, latency_ms)

        """
        tool = self.tools.get(name)
        if not tool:
            raise KeyError(f"Tool {name} not found")

        start = time.perf_counter()
        success = True

        try:
            if asyncio.iscoroutinefunction(tool.func):
                result = await tool.func(*args, **kwargs)
            else:
                result = tool.func(*args, **kwargs)
        except Exception:
            success = False
            raise
        finally:
            latency_ms = (time.perf_counter() - start) * 1000
            tool.update_metrics(success, latency_ms)

        return result, latency_ms
