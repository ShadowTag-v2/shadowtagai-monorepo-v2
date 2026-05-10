"""Tests for DeepResearchClient — Interactions API wrapper.

All tests use mocked google-genai SDK to avoid real API calls.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.intelligence.deep_research_client import (
  DeepResearchClient,
  DeepResearchConfig,
  ResearchStatus,
  ResearchTier,
)


@pytest.fixture
def mock_genai():
  """Mock the google.genai module and Client."""
  with (
    patch.dict("os.environ", {"GEMINI_API_KEY": "test-key-fake"}),
    patch(
      "src.intelligence.deep_research_client.DeepResearchClient._create_client"
    ) as mock_create,
  ):
    mock_client = MagicMock()
    mock_create.return_value = mock_client
    yield mock_client


class TestDeepResearchClient:
  """Test suite for the Deep Research Interactions API client."""

  def test_init_missing_key_raises(self):
    """Should raise ValueError when no API key is available."""
    with (
      patch.dict("os.environ", {}, clear=True),
      pytest.raises(ValueError, match="GEMINI_API_KEY not set"),
    ):
      DeepResearchClient()

  def test_resolve_agent_standard(self, mock_genai):
    """Standard tier should use the base agent."""
    with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
      client = DeepResearchClient()
      assert (
        client._resolve_agent(ResearchTier.STANDARD) == "deep-research-preview-04-2026"
      )

  def test_resolve_agent_max(self, mock_genai):
    """Max tier should use the max agent."""
    with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
      client = DeepResearchClient()
      assert (
        client._resolve_agent(ResearchTier.MAX) == "deep-research-max-preview-04-2026"
      )

  @pytest.mark.asyncio
  async def test_research_completed(self, mock_genai):
    """Should return completed result when interaction succeeds."""
    # Setup mock interaction
    mock_interaction_start = MagicMock()
    mock_interaction_start.id = "test-interaction-123"

    mock_output = MagicMock()
    mock_output.text = "# Research Report\n\nTPUs were invented at Google..."

    mock_interaction_done = MagicMock()
    mock_interaction_done.status = "completed"
    mock_interaction_done.outputs = [mock_output]

    mock_genai.interactions.create.return_value = mock_interaction_start
    mock_genai.interactions.get.return_value = mock_interaction_done

    with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
      client = DeepResearchClient()
      result = await client.research("History of Google TPUs")

    assert result.status == ResearchStatus.COMPLETED
    assert "TPUs" in result.report
    assert result.interaction_id == "test-interaction-123"
    assert result.tier == ResearchTier.STANDARD

  @pytest.mark.asyncio
  async def test_research_failed(self, mock_genai):
    """Should return failed result when interaction fails."""
    mock_interaction_start = MagicMock()
    mock_interaction_start.id = "test-fail-456"

    mock_interaction_fail = MagicMock()
    mock_interaction_fail.status = "failed"
    mock_interaction_fail.error = "Rate limit exceeded"

    mock_genai.interactions.create.return_value = mock_interaction_start
    mock_genai.interactions.get.return_value = mock_interaction_fail

    with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
      client = DeepResearchClient()
      result = await client.research("Test query")

    assert result.status == ResearchStatus.FAILED
    assert result.error == "Rate limit exceeded"

  @pytest.mark.asyncio
  async def test_research_timeout(self, mock_genai):
    """Should timeout gracefully when polling exceeds max duration."""
    mock_interaction_start = MagicMock()
    mock_interaction_start.id = "test-timeout-789"

    mock_interaction_progress = MagicMock()
    mock_interaction_progress.status = "in_progress"

    mock_genai.interactions.create.return_value = mock_interaction_start
    mock_genai.interactions.get.return_value = mock_interaction_progress

    with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
      client = DeepResearchClient()
      config = DeepResearchConfig(max_poll_seconds=1)

      with patch("src.intelligence.deep_research_client._POLL_INTERVAL_SECONDS", 0.1):
        result = await client.research("Test query", config=config)

    assert result.status == ResearchStatus.FAILED
    assert "timeout" in result.error.lower()


class TestResearchConfig:
  """Test suite for DeepResearchConfig defaults."""

  def test_defaults(self):
    """Config should have sensible defaults."""
    cfg = DeepResearchConfig()
    assert cfg.tier == ResearchTier.STANDARD
    assert cfg.tools is None
    assert cfg.thinking_summaries == "none"
    assert cfg.visualization == "auto"
    assert cfg.max_poll_seconds == 600

  def test_max_tier(self):
    """Should accept max tier configuration."""
    cfg = DeepResearchConfig(tier=ResearchTier.MAX)
    assert cfg.tier == ResearchTier.MAX
