# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Gemini Deep Research API — Autonomous research sweep client.

Wraps the Interactions API's Deep Research agent endpoints with:
  - Collaborative planning (plan → refine → execute)
  - Background execution with polling + streaming
  - Automatic reconnection for long-running research tasks
  - Visualization support (charts, graphs)
  - MCP server integration for private data
  - Multimodal input (images, PDFs)

Agents:
  - deep-research-preview-04-2026:     Fast/efficient (~$1-3/task)
  - deep-research-max-preview-04-2026: Maximum depth (~$3-7/task)

Architecture:
  This is a HIGH-LEVEL orchestrator that uses InteractionsClient internally.
  Deep Research tasks are async by nature (background=True), so all methods
  use polling or streaming with reconnection.

Public API:
  - DeepResearchClient: Main client (research, plan, stream_research)
  - ResearchTask: Represents a running research task with status polling
  - ResearchReport: Typed final report with text + images + citations
  - PlanResult: Research plan from collaborative planning
"""

from gemini_deep_research.client import (
    DeepResearchClient,
    ResearchTask,
    ResearchReport,
    PlanResult,
)

__all__ = [
    "DeepResearchClient",
    "ResearchTask",
    "ResearchReport",
    "PlanResult",
]
