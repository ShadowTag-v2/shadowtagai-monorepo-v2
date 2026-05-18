# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Tests for sandbox_adapter and VCR replay modules."""

from __future__ import annotations

import json

import pytest

from packages.shadowtag_os.gates.sandbox_adapter import (
  SandboxConfig,
  SandboxResult,
  execute_python_sandboxed,
  execute_sandboxed,
)
from packages.shadowtag_os.testing.vcr_replay import (
  VCRCassette,
  VCRInteraction,
  VCRMatcher,
  _redact_headers,
  _request_fingerprint,
  get_vcr_mode,
)


# =========================================================================
# Sandbox Adapter Tests
# =========================================================================


class TestSandboxAdapter:
  """Tests for sandbox_adapter module."""

  @pytest.mark.asyncio
  async def test_execute_echo(self):
    """Simple echo command should succeed."""
    result = await execute_sandboxed(["echo", "hello"])
    assert result.exit_code == 0
    assert "hello" in result.stdout
    assert result.duration_ms > 0

  @pytest.mark.asyncio
  async def test_execute_timeout(self):
    """Commands exceeding timeout should be killed."""
    config = SandboxConfig(timeout_seconds=0.5)
    result = await execute_sandboxed(["sleep", "10"], config)
    assert result.timed_out is True
    assert result.exit_code == -1

  @pytest.mark.asyncio
  async def test_execute_nonexistent_command(self):
    """Missing commands should return exit code 127."""
    result = await execute_sandboxed(["nonexistent_command_xyz"])
    assert result.exit_code == 127
    assert "not found" in result.stderr.lower()

  @pytest.mark.asyncio
  async def test_execute_python_sandboxed(self):
    """Python code should execute in sandbox."""
    result = await execute_python_sandboxed("print('sandbox works')")
    assert result.exit_code == 0
    assert "sandbox works" in result.stdout

  @pytest.mark.asyncio
  async def test_output_truncation(self):
    """Output exceeding max_output_bytes should be truncated."""
    config = SandboxConfig(max_output_bytes=50)
    result = await execute_sandboxed(["python3", "-c", "print('x' * 200)"], config)
    assert len(result.stdout) <= 50
    assert result.truncated is True

  @pytest.mark.asyncio
  async def test_restricted_env(self):
    """Sandbox should restrict environment variables."""
    result = await execute_sandboxed(
      ["python3", "-c", "import os; print(os.environ.get('SECRET_KEY', 'MISSING'))"]
    )
    assert "MISSING" in result.stdout

  def test_sandbox_config_defaults(self):
    """Default config should have sane values."""
    config = SandboxConfig()
    assert config.timeout_seconds == 300
    assert config.max_output_bytes == 1_048_576
    assert config.allow_network is False
    assert "PATH" in config.env_allowlist

  def test_sandbox_result_defaults(self):
    """Default result should indicate failure."""
    result = SandboxResult()
    assert result.exit_code == -1
    assert result.timed_out is False
    assert result.truncated is False


# =========================================================================
# VCR Replay Tests
# =========================================================================


class TestVCRReplay:
  """Tests for VCR replay module."""

  def test_cassette_save_load(self, tmp_path):
    """Cassettes should round-trip through save/load."""
    cassette = VCRCassette(
      name="test_cassette",
      record_mode="record",
      interactions=[
        VCRInteraction(
          request_method="GET",
          request_url="https://api.example.com/test",
          request_headers={"Accept": "application/json"},
          response_status=200,
          response_body='{"ok": true}',
        ),
      ],
    )

    path = cassette.save(tmp_path)
    assert path.exists()

    loaded = VCRCassette.load("test_cassette", tmp_path)
    assert loaded.name == "test_cassette"
    assert len(loaded.interactions) == 1
    assert loaded.interactions[0].response_status == 200
    assert loaded.interactions[0].response_body == '{"ok": true}'

  def test_cassette_load_not_found(self, tmp_path):
    """Loading a nonexistent cassette should raise FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
      VCRCassette.load("nonexistent", tmp_path)

  def test_header_redaction(self):
    """Sensitive headers should be redacted."""
    headers = {
      "Authorization": "Bearer sk-12345",
      "Accept": "application/json",
      "Cookie": "session=abc",
      "X-API-Key": "secret123",
    }
    redacted = _redact_headers(headers)
    assert redacted["Authorization"] == "[REDACTED]"
    assert redacted["Cookie"] == "[REDACTED]"
    assert redacted["X-API-Key"] == "[REDACTED]"
    assert redacted["Accept"] == "application/json"

  def test_request_fingerprint_deterministic(self):
    """Same inputs should produce same fingerprint."""
    fp1 = _request_fingerprint("GET", "https://api.example.com/test")
    fp2 = _request_fingerprint("GET", "https://api.example.com/test")
    assert fp1 == fp2
    assert len(fp1) == 16

  def test_request_fingerprint_unique(self):
    """Different inputs should produce different fingerprints."""
    fp1 = _request_fingerprint("GET", "https://api.example.com/a")
    fp2 = _request_fingerprint("GET", "https://api.example.com/b")
    assert fp1 != fp2

  def test_vcr_matcher(self):
    """Matcher should find recorded interactions."""
    cassette = VCRCassette(
      name="matcher_test",
      interactions=[
        VCRInteraction(
          request_method="GET",
          request_url="https://api.example.com/users",
          response_status=200,
          response_body='[{"id": 1}]',
        ),
        VCRInteraction(
          request_method="POST",
          request_url="https://api.example.com/users",
          request_body='{"name": "test"}',
          response_status=201,
        ),
      ],
    )

    matcher = VCRMatcher(cassette)

    # Should match GET
    match = matcher.find_match("GET", "https://api.example.com/users")
    assert match is not None
    assert match.response_status == 200

    # Should match POST with body
    match = matcher.find_match(
      "POST", "https://api.example.com/users", '{"name": "test"}'
    )
    assert match is not None
    assert match.response_status == 201

    # Should return None for unrecorded
    match = matcher.find_match("DELETE", "https://api.example.com/users")
    assert match is None

  def test_vcr_matcher_no_reuse(self):
    """Used interactions should not be returned again."""
    cassette = VCRCassette(
      name="reuse_test",
      interactions=[
        VCRInteraction(
          request_method="GET",
          request_url="https://api.example.com/once",
          response_status=200,
        ),
      ],
    )

    matcher = VCRMatcher(cassette)
    first = matcher.find_match("GET", "https://api.example.com/once")
    assert first is not None
    second = matcher.find_match("GET", "https://api.example.com/once")
    assert second is None  # Already used

  def test_get_vcr_mode_default(self, monkeypatch):
    """Default VCR mode should be passthrough."""
    monkeypatch.delenv("VCR_MODE", raising=False)
    assert get_vcr_mode() == "passthrough"

  def test_get_vcr_mode_record(self, monkeypatch):
    """VCR_MODE=record should return record."""
    monkeypatch.setenv("VCR_MODE", "record")
    assert get_vcr_mode() == "record"

  def test_get_vcr_mode_invalid(self, monkeypatch):
    """Invalid VCR_MODE should fallback to passthrough."""
    monkeypatch.setenv("VCR_MODE", "banana")
    assert get_vcr_mode() == "passthrough"

  def test_cassette_json_structure(self, tmp_path):
    """Saved cassette JSON should have expected structure."""
    cassette = VCRCassette(
      name="structure_test",
      interactions=[
        VCRInteraction(
          request_method="GET",
          request_url="https://example.com",
          response_status=200,
          response_body="ok",
        ),
      ],
    )
    path = cassette.save(tmp_path)
    data = json.loads(path.read_text())

    assert "name" in data
    assert "interactions" in data
    assert "record_mode" in data
    assert data["interactions"][0]["request"]["method"] == "GET"
    assert data["interactions"][0]["response"]["status"] == 200
