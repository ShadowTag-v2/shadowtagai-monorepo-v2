# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Kosmos Agent — Web-Grounded Research via Google Developer Knowledge MCP.

The Kosmos agent is the first stage of the Autoresearch Triad:
  Kosmos → BioAgents → n-autoresearch

It performs web-grounded research using the google-developer-knowledge MCP
server, producing structured intelligence products (MCOO, HPTL) that feed
into the BioAgents mutation engine.

References:
    - ATP 2-01.3: Intelligence Preparation of the Battlefield
    - src/intelligence/ipb_engine.py (IPB framework)
    - knowledge/adk-2-graph-workflows/artifacts/reference.md
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger("kosmos-agent")


class ResearchDomain(str, Enum):
  """Research domains the Kosmos agent can target."""

  GOOGLE_CLOUD = "google_cloud"
  FIREBASE = "firebase"
  ANDROID = "android"
  WEB_DEV = "web_dev"
  AI_ML = "ai_ml"
  SECURITY = "security"
  GENERAL = "general"


@dataclass
class ResearchQuery:
  """A structured research query for the Kosmos agent."""

  question: str
  domain: ResearchDomain = ResearchDomain.GENERAL
  max_documents: int = 5
  depth: int = 1  # 1 = surface, 2 = follow-up, 3 = exhaustive


@dataclass
class ResearchResult:
  """Structured output from a Kosmos research cycle."""

  query: ResearchQuery
  documents: list[dict[str, Any]] = field(default_factory=list)
  grounded_answer: str = ""
  confidence: float = 0.0
  sources: list[str] = field(default_factory=list)
  elapsed_ms: float = 0.0
  timestamp: float = field(default_factory=time.time)

  @property
  def is_high_confidence(self) -> bool:
    """Whether the result meets the confidence threshold for BioAgents."""
    return self.confidence >= 0.7


class KosmosAgent:
  """Web-grounded research agent using Google Developer Knowledge MCP.

  This agent does NOT execute MCP calls directly — it produces
  structured research plans that the Antigravity orchestrator executes.
  This maintains the MCP-first routing invariant from AGENTS.md.

  Usage::

      kosmos = KosmosAgent()
      plan = kosmos.plan_research(ResearchQuery(
          question="How to configure Cloud Run health checks?",
          domain=ResearchDomain.GOOGLE_CLOUD,
          depth=2,
      ))
      # plan.mcp_calls is then executed by the orchestrator
  """

  def __init__(self) -> None:
    self._research_history: list[ResearchResult] = []
    self._max_history = 100
    logger.info("🌐 Kosmos Agent initialized")

  def plan_research(self, query: ResearchQuery) -> dict[str, Any]:
    """Produce an MCP execution plan for a research query.

    Returns a dict with:
      - mcp_calls: ordered list of MCP tool invocations
      - follow_up_queries: depth-2+ queries to execute if depth > 1
      - ipb_context: structured IPB metadata for the intelligence cycle
    """
    plan: dict[str, Any] = {
      "agent": "kosmos",
      "query": query.question,
      "domain": query.domain.value,
      "depth": query.depth,
      "mcp_calls": [],
      "follow_up_queries": [],
      "ipb_context": {
        "oe_boundaries": query.domain.value,
        "collection_priority": "PRIMARY",
      },
    }

    # Primary search call
    plan["mcp_calls"].append(
      {
        "server": "google-developer-knowledge",
        "tool": "search_documents",
        "args": {"query": query.question},
        "priority": 1,
      }
    )

    # If depth >= 2, plan a grounded answer call
    if query.depth >= 2:
      plan["mcp_calls"].append(
        {
          "server": "google-developer-knowledge",
          "tool": "answer_query",
          "args": {"query": query.question},
          "priority": 2,
        }
      )

    # If depth >= 3, plan follow-up document retrieval
    if query.depth >= 3:
      plan["follow_up_queries"].append(
        {
          "type": "get_documents",
          "note": "Retrieve full docs from search results (names from search_documents)",
          "server": "google-developer-knowledge",
          "tool": "get_documents",
          "priority": 3,
        }
      )

    logger.info(
      "📋 Research plan: %d MCP calls, depth=%d, domain=%s",
      len(plan["mcp_calls"]),
      query.depth,
      query.domain.value,
    )
    return plan

  def record_result(self, result: ResearchResult) -> None:
    """Record a completed research result for triad handoff."""
    if len(self._research_history) >= self._max_history:
      self._research_history.pop(0)
    self._research_history.append(result)
    logger.info(
      "📝 Research recorded: confidence=%.2f, sources=%d",
      result.confidence,
      len(result.sources),
    )

  def get_handoff_payload(self) -> list[dict[str, Any]]:
    """Produce the handoff payload for BioAgents (Triad stage 2).

    Only includes high-confidence results that meet the threshold.
    """
    return [
      {
        "question": r.query.question,
        "answer": r.grounded_answer,
        "confidence": r.confidence,
        "sources": r.sources,
        "domain": r.query.domain.value,
      }
      for r in self._research_history
      if r.is_high_confidence
    ]

  def get_diagnostics(self) -> dict[str, Any]:
    """Return agent diagnostics for monitoring."""
    return {
      "agent": "kosmos",
      "total_queries": len(self._research_history),
      "high_confidence": sum(1 for r in self._research_history if r.is_high_confidence),
      "low_confidence": sum(
        1 for r in self._research_history if not r.is_high_confidence
      ),
      "domains_covered": list({r.query.domain.value for r in self._research_history}),
    }
