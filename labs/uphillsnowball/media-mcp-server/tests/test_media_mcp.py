"""test_media_mcp.py — Tests for Media MCP Server + Slides Agent.

Tests:
  - Input validation (prompt length, GCS URI format)
  - Rate limiting
  - Image generation config
  - Video generation config
  - Signed URL generation
  - Slides agent configuration
"""

import pytest


# ===== INPUT VALIDATION TESTS =====


class TestInputValidation:
  """Tests for prompt and GCS URI validation."""

  def test_validate_prompt_empty(self):
    """Empty prompts should raise ValueError."""
    from media_mcp_server import _validate_prompt

    with pytest.raises(ValueError, match="cannot be empty"):
      _validate_prompt("")

  def test_validate_prompt_whitespace(self):
    """Whitespace-only prompts should raise ValueError."""
    from media_mcp_server import _validate_prompt

    with pytest.raises(ValueError, match="cannot be empty"):
      _validate_prompt("   ")

  def test_validate_prompt_too_long(self):
    """Prompts exceeding max length should raise ValueError."""
    from media_mcp_server import _validate_prompt

    long_prompt = "x" * 2001
    with pytest.raises(ValueError, match="exceeds max length"):
      _validate_prompt(long_prompt)

  def test_validate_prompt_valid(self):
    """Valid prompts should pass and be stripped."""
    from media_mcp_server import _validate_prompt

    result = _validate_prompt("  A cinematic hero shot  ")
    assert result == "A cinematic hero shot"

  def test_validate_gcs_uri_valid(self):
    """Valid GCS URIs should pass."""
    from media_mcp_server import _validate_gcs_uri

    uri = "gs://shadowtag-omega-v4-media/mcp-images/test.png"
    assert _validate_gcs_uri(uri) == uri

  def test_validate_gcs_uri_invalid_scheme(self):
    """Non-gs:// URIs should raise ValueError."""
    from media_mcp_server import _validate_gcs_uri

    with pytest.raises(ValueError, match="Invalid GCS URI"):
      _validate_gcs_uri("https://example.com/file.png")

  def test_validate_gcs_uri_path_traversal(self):
    """Path traversal attempts should raise ValueError."""
    from media_mcp_server import _validate_gcs_uri

    with pytest.raises(ValueError, match="invalid characters"):
      _validate_gcs_uri("gs://bucket/../../../etc/passwd")

  def test_validate_gcs_uri_newline_injection(self):
    """Newline injection should raise ValueError."""
    from media_mcp_server import _validate_gcs_uri

    with pytest.raises(ValueError, match="invalid characters"):
      _validate_gcs_uri("gs://bucket/path\ninjection")


# ===== RATE LIMITING TESTS =====


class TestRateLimiting:
  """Tests for rate limiter."""

  def test_rate_limit_allows_normal_traffic(self):
    """Normal traffic should not be rate limited."""
    from media_mcp_server import _check_rate_limit, _rate_limiter

    _rate_limiter.clear()
    # Should not raise for first request
    _check_rate_limit("test_normal")

  def test_rate_limit_blocks_excessive_traffic(self):
    """Excessive traffic should be blocked."""
    import time

    from media_mcp_server import (
      RATE_LIMIT_RPM,
      _check_rate_limit,
      _rate_limiter,
    )

    _rate_limiter.clear()
    client_id = "test_excess"

    # Fill up the rate limit
    _rate_limiter[client_id] = [time.time()] * RATE_LIMIT_RPM

    with pytest.raises(ValueError, match="Rate limit exceeded"):
      _check_rate_limit(client_id)


# ===== CONFIGURATION TESTS =====


class TestConfiguration:
  """Tests for server configuration."""

  def test_gcs_bucket_default(self):
    """Default GCS bucket should be set."""
    from media_mcp_server import GCS_BUCKET

    assert GCS_BUCKET == "shadowtag-omega-v4-media"

  def test_max_retries_configured(self):
    """MAX_RETRIES should be set to 5."""
    from media_mcp_server import MAX_RETRIES

    assert MAX_RETRIES == 5

  def test_tools_registered(self):
    """All tools should be registered."""
    from media_mcp_server import tools

    tool_names = [t.__name__ for t in tools]
    assert "generate_image" in tool_names
    assert "generate_video" in tool_names
    assert "get_signed_url" in tool_names

  def test_cors_origins_parsed(self):
    """CORS origins should be parsed from env."""
    from media_mcp_server import ALLOWED_ORIGINS

    assert isinstance(ALLOWED_ORIGINS, list)
    assert len(ALLOWED_ORIGINS) > 0


# ===== SLIDES AGENT TESTS =====


class TestSlidesAgentConfig:
  """Tests for slides agent configuration."""

  def test_agent_name(self):
    """Agent should have correct name."""
    from slides_agent import root_agent

    assert root_agent.name == "cinematic_content_agent"

  def test_agent_model(self):
    """Agent should use Gemini 3 Pro."""
    from slides_agent import root_agent

    assert "gemini" in root_agent.model.lower()

  def test_agent_has_tools(self):
    """Agent should have MCP tools configured."""
    from slides_agent import root_agent

    assert root_agent.tools is not None
    assert len(root_agent.tools) > 0

  def test_app_name(self):
    """App should have correct name."""
    from slides_agent import app

    assert app.name == "cinematic-content-agent"
