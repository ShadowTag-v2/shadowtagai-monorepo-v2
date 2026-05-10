# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Unit tests for Batch 7 ported services.

Covers: oauth_service, remote_managed_settings, lsp_client,
        voice_service, tool_orchestration.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import tempfile
from pathlib import Path


# ── oauth_service ─────────────────────────────────────────────────────


class TestOAuthService:
  """Test PKCE helpers and OAuthService protocol logic."""

  def test_generate_code_verifier_length(self):
    from packages.agnt_services.oauth_service import generate_code_verifier

    v = generate_code_verifier()
    assert len(v) <= 128
    assert len(v) >= 43  # min per RFC 7636

  def test_generate_code_verifier_unique(self):
    from packages.agnt_services.oauth_service import generate_code_verifier

    v1 = generate_code_verifier()
    v2 = generate_code_verifier()
    assert v1 != v2

  def test_generate_code_challenge_s256(self):
    """Verify S256 challenge matches RFC 7636 §4.2 spec."""
    from packages.agnt_services.oauth_service import (
      generate_code_challenge,
    )

    verifier = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
    challenge = generate_code_challenge(verifier)
    # Manual calculation
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    expected = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    assert challenge == expected

  def test_generate_state_uniqueness(self):
    from packages.agnt_services.oauth_service import generate_state

    s1 = generate_state()
    s2 = generate_state()
    assert s1 != s2
    assert len(s1) > 20

  def test_oauth_service_build_auth_url(self):
    from packages.agnt_services.oauth_service import OAuthConfig, OAuthService

    config = OAuthConfig(
      base_api_url="https://api.example.com",
      client_id="test-client",
      authorize_url="https://auth.example.com/authorize",
      token_url="https://auth.example.com/token",
      profile_url="https://api.example.com/profile",
    )
    svc = OAuthService(config)
    url = svc.build_auth_url(port=9876)
    assert "https://auth.example.com/authorize?" in url
    assert "client_id=test-client" in url
    assert "redirect_uri=http%3A%2F%2Flocalhost%3A9876%2Foauth%2Fcallback" in url
    assert "code_challenge_method=S256" in url
    assert f"state={svc.state}" in url

  def test_oauth_service_build_auth_url_manual(self):
    from packages.agnt_services.oauth_service import OAuthConfig, OAuthService

    config = OAuthConfig(
      base_api_url="https://api.example.com",
      client_id="test",
      authorize_url="https://auth.example.com/authorize",
      token_url="https://auth.example.com/token",
      profile_url="https://api.example.com/profile",
    )
    svc = OAuthService(config)
    url = svc.build_auth_url(port=9876, is_manual=True)
    assert "prompt=manual" in url

  def test_oauth_service_build_token_request(self):
    from packages.agnt_services.oauth_service import OAuthConfig, OAuthService

    config = OAuthConfig(
      base_api_url="https://api.example.com",
      client_id="test-client",
      authorize_url="https://a.com",
      token_url="https://t.com",
      profile_url="https://p.com",
    )
    svc = OAuthService(config)
    req = svc.build_token_request("auth-code-123", port=9876)
    assert req["grant_type"] == "authorization_code"
    assert req["code"] == "auth-code-123"
    assert req["code_verifier"] == svc.code_verifier
    assert req["client_id"] == "test-client"

  def test_oauth_format_tokens(self):
    from packages.agnt_services.oauth_service import OAuthService, SubscriptionType

    tokens = OAuthService.format_tokens(
      access_token="at-123",
      refresh_token="rt-456",
      expires_in=3600,
      scope="read write",
      subscription_type=SubscriptionType.PRO,
    )
    assert tokens.access_token == "at-123"
    assert tokens.refresh_token == "rt-456"
    assert tokens.scopes == ["read", "write"]
    assert tokens.subscription_type == SubscriptionType.PRO
    assert tokens.expires_at > 0

  def test_oauth_parse_scopes(self):
    from packages.agnt_services.oauth_service import OAuthService

    assert OAuthService.parse_scopes("read write admin") == ["read", "write", "admin"]
    assert OAuthService.parse_scopes("") == []

  def test_oauth_cleanup_resets_state(self):
    from packages.agnt_services.oauth_service import OAuthConfig, OAuthService

    config = OAuthConfig(
      base_api_url="x", client_id="x", authorize_url="x", token_url="x", profile_url="x"
    )
    svc = OAuthService(config)
    old_verifier = svc.code_verifier
    old_state = svc.state
    svc.cleanup()
    assert svc.code_verifier != old_verifier
    assert svc.state != old_state


# ── remote_managed_settings ───────────────────────────────────────────


class TestRemoteManagedSettings:
  """Test checksum computation and cache lifecycle."""

  def test_compute_checksum_deterministic(self):
    from packages.agnt_services.remote_managed_settings import (
      compute_checksum_from_settings,
    )

    settings = {"foo": "bar", "nested": {"a": 1, "b": 2}}
    c1 = compute_checksum_from_settings(settings)
    c2 = compute_checksum_from_settings(settings)
    assert c1 == c2
    assert c1.startswith("sha256:")

  def test_compute_checksum_key_order_independent(self):
    from packages.agnt_services.remote_managed_settings import (
      compute_checksum_from_settings,
    )

    s1 = {"z": 1, "a": 2}
    s2 = {"a": 2, "z": 1}
    assert compute_checksum_from_settings(s1) == compute_checksum_from_settings(s2)

  def test_settings_service_save_and_load(self):
    from packages.agnt_services.remote_managed_settings import (
      RemoteManagedSettingsService,
    )

    with tempfile.TemporaryDirectory() as tmpdir:
      path = Path(tmpdir) / "settings.json"
      svc = RemoteManagedSettingsService(settings_path=path, eligible=True)
      settings = {"tools": {"enabled": True}, "limits": {"max_tokens": 100000}}
      svc.save_settings(settings)
      assert path.exists()
      loaded = svc.load_cached_settings()
      assert loaded == settings

  def test_settings_service_clear_cache(self):
    from packages.agnt_services.remote_managed_settings import (
      RemoteManagedSettingsService,
    )

    with tempfile.TemporaryDirectory() as tmpdir:
      path = Path(tmpdir) / "settings.json"
      svc = RemoteManagedSettingsService(settings_path=path, eligible=True)
      svc.save_settings({"k": "v"})
      svc.set_session_cache({"k": "v"})
      svc.clear_cache()
      assert svc.session_cache is None
      assert not path.exists()

  def test_retry_delay_exponential(self):
    from packages.agnt_services.remote_managed_settings import get_retry_delay

    assert get_retry_delay(1) == 1.0
    assert get_retry_delay(2) == 2.0
    assert get_retry_delay(3) == 4.0
    assert get_retry_delay(7) == 60.0  # capped at 60s

  def test_apply_settings_fail_open(self):
    from packages.agnt_services.remote_managed_settings import (
      FetchResult,
      RemoteManagedSettingsService,
    )

    with tempfile.TemporaryDirectory() as tmpdir:
      path = Path(tmpdir) / "settings.json"
      svc = RemoteManagedSettingsService(settings_path=path, eligible=True)
      cached = {"old": "data"}
      svc.set_session_cache(cached)
      # Simulate fetch failure
      result = FetchResult(success=False, error="network error")
      active = svc.apply_settings(result)
      assert active == cached  # fail-open: stale cache used


# ── lsp_client ────────────────────────────────────────────────────────


class TestLSPClient:
  """Test LSP client lifecycle."""

  def test_lsp_client_init(self):
    from packages.agnt_services.lsp_client import LSPClient

    client = LSPClient("test-server")
    assert client.server_name == "test-server"
    assert not client.is_initialized
    assert client.capabilities is None

  def test_lsp_client_notification_queues(self):
    from packages.agnt_services.lsp_client import LSPClient

    client = LSPClient("test")
    called = []
    client.on_notification("textDocument/didSave", lambda: called.append(1))
    assert len(client._pending_handlers) == 1
    # cleanup resets connection state but preserves handlers for reconnection
    client.cleanup()
    assert client._process is None
    assert not client.is_initialized
    assert len(client._pending_handlers) == 1  # handlers persist

  def test_server_capabilities_from_dict(self):
    from packages.agnt_services.lsp_client import ServerCapabilities

    caps = ServerCapabilities.from_dict(
      {"hoverProvider": True, "definitionProvider": False, "extra": 42}
    )
    assert caps.hover_provider is True
    assert caps.definition_provider is False
    assert caps.raw["extra"] == 42


# ── voice_service ─────────────────────────────────────────────────────


class TestVoiceService:
  """Test voice recording availability checks."""

  def test_recording_availability_struct(self):
    from packages.agnt_services.voice_service import RecordingAvailability

    r = RecordingAvailability(available=True)
    assert r.available is True
    assert r.reason is None

  def test_voice_dependencies_struct(self):
    from packages.agnt_services.voice_service import VoiceDependencies

    d = VoiceDependencies(
      available=False, missing=["sox"], install_command="brew install sox"
    )
    assert not d.available
    assert d.missing == ["sox"]

  def test_voice_recorder_not_recording_initially(self):
    from packages.agnt_services.voice_service import VoiceRecorder

    r = VoiceRecorder()
    assert not r.is_recording

  def test_voice_recorder_stop_noop(self):
    from packages.agnt_services.voice_service import VoiceRecorder

    r = VoiceRecorder()
    r.stop_recording()  # Should not raise


# ── tool_orchestration ────────────────────────────────────────────────


class TestToolOrchestration:
  """Test batch partitioning and execution."""

  def test_partition_all_serial(self):
    from packages.agnt_services.tool_orchestration import (
      ToolUseBlock,
      partition_tool_calls,
    )

    blocks = [ToolUseBlock(id="1", name="bash"), ToolUseBlock(id="2", name="write")]
    batches = partition_tool_calls(blocks, lambda _: False)
    assert len(batches) == 2
    assert not batches[0].is_concurrency_safe
    assert not batches[1].is_concurrency_safe

  def test_partition_all_concurrent(self):
    from packages.agnt_services.tool_orchestration import (
      ToolUseBlock,
      partition_tool_calls,
    )

    blocks = [ToolUseBlock(id="1", name="read"), ToolUseBlock(id="2", name="read")]
    batches = partition_tool_calls(blocks, lambda _: True)
    assert len(batches) == 1
    assert batches[0].is_concurrency_safe
    assert len(batches[0].blocks) == 2

  def test_partition_mixed(self):
    from packages.agnt_services.tool_orchestration import (
      ToolUseBlock,
      partition_tool_calls,
    )

    blocks = [
      ToolUseBlock(id="1", name="read"),
      ToolUseBlock(id="2", name="read"),
      ToolUseBlock(id="3", name="bash"),
      ToolUseBlock(id="4", name="read"),
    ]
    batches = partition_tool_calls(blocks, lambda b: b.name == "read")
    assert len(batches) == 3
    assert batches[0].is_concurrency_safe  # read, read
    assert not batches[1].is_concurrency_safe  # bash
    assert batches[2].is_concurrency_safe  # read

  def test_run_tools_concurrently(self):
    from packages.agnt_services.tool_orchestration import (
      ToolUseBlock,
      ToolUseContext,
      run_tools_concurrently,
    )

    blocks = [ToolUseBlock(id=str(i), name="read") for i in range(5)]

    def executor(block, ctx):
      return f"result-{block.id}"

    results = asyncio.run(
      run_tools_concurrently(blocks, executor, ToolUseContext(), max_concurrency=3)
    )
    assert len(results) == 5
    assert all(r.error is None for r in results)
    ids = {r.tool_use_id for r in results}
    assert ids == {"0", "1", "2", "3", "4"}

  def test_run_tools_concurrently_error_handling(self):
    from packages.agnt_services.tool_orchestration import (
      ToolUseBlock,
      ToolUseContext,
      run_tools_concurrently,
    )

    blocks = [ToolUseBlock(id="1", name="fail")]

    def executor(block, ctx):
      raise ValueError("intentional")

    results = asyncio.run(run_tools_concurrently(blocks, executor, ToolUseContext()))
    assert len(results) == 1
    assert results[0].error == "intentional"

  def test_get_max_concurrency_default(self):
    from packages.agnt_services.tool_orchestration import get_max_tool_use_concurrency

    assert get_max_tool_use_concurrency() == 10
