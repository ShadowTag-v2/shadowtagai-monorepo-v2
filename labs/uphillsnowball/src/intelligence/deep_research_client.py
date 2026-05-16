"""Gemini Deep Research Client — Interactions API.

Wraps the official Gemini Deep Research agent
(``deep-research-preview-04-2026``) via the Interactions API.
This replaces ALL brittle Playwright OSINT scraping with a native,
server-side research loop that returns structured reports.

API Reference:
    https://ai.google.dev/gemini-api/docs/deep-research

Cost Model:
    - Standard (``deep-research-preview-04-2026``): ~$1–3 per task
    - Max (``deep-research-max-preview-04-2026``): ~$3–7 per task

Secrets:
    ``GEMINI_API_KEY`` must be set in the environment, sourced from
    GCP Secret Manager via ``scripts/load_mcp_secrets.sh``.
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from dataclasses import dataclass
from enum import StrEnum

logger = logging.getLogger("DeepResearch-Client")

# Default polling configuration
_POLL_INTERVAL_SECONDS = 10
_MAX_POLL_DURATION_SECONDS = 600  # 10 minutes max
_DEFAULT_AGENT = "deep-research-preview-04-2026"
_MAX_AGENT = "deep-research-max-preview-04-2026"


class ResearchStatus(StrEnum):
  """Status of a Deep Research interaction."""

  PENDING = "pending"
  IN_PROGRESS = "in_progress"
  COMPLETED = "completed"
  FAILED = "failed"


class ResearchTier(StrEnum):
  """Deep Research agent tiers with different cost profiles."""

  STANDARD = "standard"  # ~$1–3 per task
  MAX = "max"  # ~$3–7 per task


@dataclass(frozen=True)
class ResearchResult:
  """Structured result from a Deep Research interaction.

  Attributes:
      interaction_id: The unique ID of the research interaction.
      status: Final status of the research.
      report: The synthesized research report text.
      query: The original query that was researched.
      tier: Which agent tier was used.
      elapsed_seconds: Wall-clock time for the research.
  """

  interaction_id: str
  status: ResearchStatus
  report: str
  query: str
  tier: ResearchTier
  elapsed_seconds: float
  error: str | None = None


@dataclass
class DeepResearchConfig:
  """Configuration for Deep Research requests.

  Attributes:
      tier: Standard or Max research depth.
      tools: List of tool types to enable (default: all).
      thinking_summaries: Whether to include reasoning steps.
      visualization: Whether to include charts/graphs.
      max_poll_seconds: Maximum polling duration.
  """

  tier: ResearchTier = ResearchTier.STANDARD
  tools: list[dict] | None = None  # None = all defaults (search + url + code)
  thinking_summaries: str = "none"
  visualization: str = "auto"
  max_poll_seconds: int = _MAX_POLL_DURATION_SECONDS


class DeepResearchClient:
  """Client for the Gemini Deep Research Interactions API.

  Uses ``google-genai`` SDK's Interactions API — NOT ``generate_content``.
  The Deep Research agent autonomously plans, searches, reads, and
  synthesizes multi-step research tasks.

  Example::

      client = DeepResearchClient()
      result = await client.research("History of Google TPUs")
      print(result.report)
  """

  def __init__(self, api_key: str | None = None) -> None:
    """Initialize the Deep Research client.

    Args:
        api_key: Gemini API key. Falls back to ``GEMINI_API_KEY`` env var.

    Raises:
        RuntimeError: If ``google-genai`` is not installed.
        ValueError: If no API key is available.
    """
    self._api_key = api_key or os.environ.get("GEMINI_API_KEY")
    if not self._api_key:
      raise ValueError(
        "GEMINI_API_KEY not set. Source it from GCP Secret Manager: `source scripts/load_mcp_secrets.sh`"
      )
    self._client = self._create_client()

  def _create_client(self):
    """Lazily import and create the genai client.

    Returns:
        A ``google.genai.Client`` instance.

    Raises:
        RuntimeError: If ``google-genai`` is not installed.
    """
    try:
      from google import genai
    except ImportError as exc:
      raise RuntimeError(
        "google-genai SDK not installed. Run: pip install 'google-genai>=1.0.0'"
      ) from exc

    return genai.Client(api_key=self._api_key)

  def _resolve_agent(self, tier: ResearchTier) -> str:
    """Resolve the agent name from the tier.

    Args:
        tier: The research depth tier.

    Returns:
        The agent identifier string.
    """
    if tier == ResearchTier.MAX:
      return _MAX_AGENT
    return _DEFAULT_AGENT

  async def research(
    self,
    query: str,
    config: DeepResearchConfig | None = None,
  ) -> ResearchResult:
    """Execute a Deep Research task asynchronously.

    Starts a background research interaction and polls until
    completion or timeout.

    Args:
        query: The research query/prompt.
        config: Optional configuration overrides.

    Returns:
        A ``ResearchResult`` with the synthesized report.
    """
    cfg = config or DeepResearchConfig()
    agent = self._resolve_agent(cfg.tier)

    logger.info(
      "🔬 Deep Research: Starting %s-tier research for: %.80s...",
      cfg.tier.value,
      query,
    )

    start_time = time.monotonic()

    # Build the create kwargs
    create_kwargs: dict = {
      "input": query,
      "agent": agent,
      "background": True,
      "agent_config": {
        "type": "deep-research",
        "thinking_summaries": cfg.thinking_summaries,
        "visualization": cfg.visualization,
      },
    }
    if cfg.tools is not None:
      create_kwargs["tools"] = cfg.tools

    # Start the interaction (runs in executor to avoid blocking)
    interaction = await asyncio.to_thread(
      self._client.interactions.create,
      **create_kwargs,
    )

    interaction_id = interaction.id
    logger.info("  Research started: %s", interaction_id)

    # Poll for completion
    result = await self._poll_until_complete(
      interaction_id=interaction_id,
      query=query,
      tier=cfg.tier,
      start_time=start_time,
      max_seconds=cfg.max_poll_seconds,
    )

    return result

  async def _poll_until_complete(
    self,
    *,
    interaction_id: str,
    query: str,
    tier: ResearchTier,
    start_time: float,
    max_seconds: int,
  ) -> ResearchResult:
    """Poll the interaction until it completes or times out.

    Args:
        interaction_id: The interaction to poll.
        query: Original query for result metadata.
        tier: Which tier was used.
        start_time: Monotonic start time.
        max_seconds: Max polling duration.

    Returns:
        A ``ResearchResult`` with the final state.
    """
    while True:
      elapsed = time.monotonic() - start_time
      if elapsed > max_seconds:
        logger.warning(
          "⏰ Deep Research timed out after %.0fs: %s",
          elapsed,
          interaction_id,
        )
        return ResearchResult(
          interaction_id=interaction_id,
          status=ResearchStatus.FAILED,
          report="",
          query=query,
          tier=tier,
          elapsed_seconds=elapsed,
          error=f"Polling timeout after {max_seconds}s",
        )

      interaction = await asyncio.to_thread(
        self._client.interactions.get,
        interaction_id,
      )

      if interaction.status == "completed":
        report_text = ""
        if interaction.outputs:
          report_text = interaction.outputs[-1].text or ""

        elapsed = time.monotonic() - start_time
        logger.info(
          "✅ Deep Research completed in %.1fs: %s (%.0f chars)",
          elapsed,
          interaction_id,
          len(report_text),
        )
        return ResearchResult(
          interaction_id=interaction_id,
          status=ResearchStatus.COMPLETED,
          report=report_text,
          query=query,
          tier=tier,
          elapsed_seconds=elapsed,
        )

      if interaction.status == "failed":
        elapsed = time.monotonic() - start_time
        error_msg = getattr(interaction, "error", "Unknown error")
        logger.error(
          "❌ Deep Research failed after %.1fs: %s — %s",
          elapsed,
          interaction_id,
          error_msg,
        )
        return ResearchResult(
          interaction_id=interaction_id,
          status=ResearchStatus.FAILED,
          report="",
          query=query,
          tier=tier,
          elapsed_seconds=elapsed,
          error=str(error_msg),
        )

      await asyncio.sleep(_POLL_INTERVAL_SECONDS)

  async def follow_up(
    self,
    previous_interaction_id: str,
    question: str,
  ) -> str:
    """Ask a follow-up question on a completed research interaction.

    Uses ``gemini-3.1-flash-lite-preview-thinking`` (the authorized
    external runtime model) for follow-up synthesis.

    Args:
        previous_interaction_id: ID of the completed interaction.
        question: The follow-up question.

    Returns:
        The follow-up response text.
    """
    logger.info(
      "💬 Follow-up on %s: %.80s...",
      previous_interaction_id,
      question,
    )

    interaction = await asyncio.to_thread(
      self._client.interactions.create,
      input=question,
      model="gemini-3.1-flash-lite-preview-thinking",
      previous_interaction_id=previous_interaction_id,
    )

    if interaction.outputs:
      return interaction.outputs[-1].text or ""
    return ""
