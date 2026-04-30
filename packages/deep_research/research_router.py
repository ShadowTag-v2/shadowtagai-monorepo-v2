# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Research Router — MCP-aware query routing for deep research.

Routes research queries to the optimal MCP server based on query type:
  - Google Developer Knowledge: API docs, SDK references, best practices
  - Sequential Thinking: Multi-step reasoning, hypothesis verification
  - Web Search: General information, external resources
  - Local Codebase: File search, grep, directory listing

This follows the Capability Resolution Doctrine: if an operation CAN be
performed by an MCP server, it MUST be. No terminal fallbacks for
MCP-capable operations.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class QuerySource(StrEnum):
    """Target MCP server or tool for a research query."""

    GOOGLE_DEVELOPER_KNOWLEDGE = "google-developer-knowledge"
    SEQUENTIAL_THINKING = "sequential-thinking"
    WEB_SEARCH = "web-search"
    LOCAL_CODEBASE = "local-codebase"
    CHROME_DEVTOOLS = "chrome-devtools-mcp"
    STITCH_MCP = "stitch-mcp"
    FIREBASE_MCP = "firebase-mcp-server"


@dataclass
class ResearchQuery:
    """A typed research query with routing metadata."""

    query: str
    source: QuerySource
    priority: int = 1  # 1 = highest
    context: dict[str, Any] = field(default_factory=dict)
    max_results: int = 10
    # Set by router after classification.
    classified_by: str = "manual"

    def to_dict(self) -> dict[str, Any]:
        """Serialize for telemetry or logging."""
        return {
            "query": self.query[:200],
            "source": self.source.value,
            "priority": self.priority,
            "classified_by": self.classified_by,
            "max_results": self.max_results,
        }


# ── Classification Patterns ────────────────────────────────────

# Google Developer Knowledge — API docs, SDK, Firebase, Cloud, Android, etc.
_GOOGLE_DEV_PATTERNS = [
    r"\b(?:firebase|firestore|cloud\s?run|cloud\s?tasks)\b",
    r"\b(?:gcp|google\s?cloud|vertex\s?ai|gemini\s?api)\b",
    r"\b(?:android|flutter|chrome\s?extension)\b",
    r"\b(?:next\.?js|tailwind|shadcn)\b",
    r"\b(?:api|sdk|documentation|reference|guide)\b",
    r"\b(?:how\s+to|best\s+practice|pattern|architecture)\b",
]

# Sequential Thinking — multi-step reasoning, design decisions.
_THINKING_PATTERNS = [
    r"\b(?:compare|tradeoff|trade-off|pros?\s+and\s+cons?)\b",
    r"\b(?:design|architect|plan|strategy)\b",
    r"\b(?:should\s+(?:I|we)|which\s+is\s+better)\b",
    r"\b(?:break\s+down|decompose|analyze|evaluate)\b",
    r"\b(?:hypothesis|verify|validate)\b",
]

# Local Codebase — file search, grep, existing code inspection.
_LOCAL_PATTERNS = [
    r"\b(?:find|search|grep|locate)\s+(?:in\s+)?(?:file|code|function)\b",
    r"\b(?:existing|current|our)\s+(?:implementation|code|module)\b",
    r"\b(?:where\s+is|show\s+me|what\s+does)\b",
    r"(?:\.py|\.ts|\.tsx|\.js|\.go|\.rs|\.cs)\b",
]

# Firebase MCP — direct Firebase operations.
_FIREBASE_PATTERNS = [
    r"\b(?:firebase\s+(?:auth|hosting|storage|functions))\b",
    r"\b(?:firestore\s+(?:rules|index|document|collection))\b",
    r"\b(?:deploy|cloud\s+function)\b",
]


def _score_patterns(query: str, patterns: list[str]) -> int:
    """Count how many patterns match the query (case-insensitive)."""
    q_lower = query.lower()
    return sum(1 for p in patterns if re.search(p, q_lower, re.IGNORECASE))


def classify_query(query: str) -> QuerySource:
    """Classify a research query to its optimal MCP source.

    Uses pattern matching with tie-breaking priority order:
    1. Firebase MCP (most specific)
    2. Google Developer Knowledge (docs)
    3. Local Codebase (workspace)
    4. Sequential Thinking (reasoning)
    5. Web Search (fallback)
    """
    scores: dict[QuerySource, int] = {
        QuerySource.FIREBASE_MCP: _score_patterns(query, _FIREBASE_PATTERNS),
        QuerySource.GOOGLE_DEVELOPER_KNOWLEDGE: _score_patterns(query, _GOOGLE_DEV_PATTERNS),
        QuerySource.LOCAL_CODEBASE: _score_patterns(query, _LOCAL_PATTERNS),
        QuerySource.SEQUENTIAL_THINKING: _score_patterns(query, _THINKING_PATTERNS),
    }

    # Priority ordering for tie-breaking.
    priority_order = [
        QuerySource.FIREBASE_MCP,
        QuerySource.GOOGLE_DEVELOPER_KNOWLEDGE,
        QuerySource.LOCAL_CODEBASE,
        QuerySource.SEQUENTIAL_THINKING,
    ]

    best_source = QuerySource.WEB_SEARCH
    best_score = 0
    for source in priority_order:
        if scores[source] > best_score:
            best_score = scores[source]
            best_source = source

    return best_source


def route_query(query: str, **kwargs: Any) -> ResearchQuery:
    """Classify and route a research query to the optimal MCP source.

    Args:
        query: The raw research query string.
        **kwargs: Additional fields for ResearchQuery (priority, context, etc.).

    Returns:
        A classified ResearchQuery ready for execution.
    """
    source = classify_query(query)
    classified = ResearchQuery(
        query=query,
        source=source,
        classified_by="auto_router",
        **kwargs,
    )
    logger.debug(
        "[ResearchRouter] %s → %s (query: %s...)",
        classified.classified_by,
        source.value,
        query[:80],
    )
    return classified


def create_batch_queries(
    queries: list[str],
    default_priority: int = 1,
) -> list[ResearchQuery]:
    """Classify and route a batch of queries, sorted by priority.

    Args:
        queries: List of raw query strings.
        default_priority: Default priority for all queries.

    Returns:
        Sorted list of ResearchQuery objects (highest priority first).
    """
    routed = [route_query(q, priority=default_priority) for q in queries]
    return sorted(routed, key=lambda rq: rq.priority)
