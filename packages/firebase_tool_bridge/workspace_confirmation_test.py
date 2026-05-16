# Copyright 2026 ShadowTagAI. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Tests for WorkspaceCLI and Sovereign confirmation providers."""

from __future__ import annotations

import json
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from firebase_tool_bridge.registry import RiskTier
from firebase_tool_bridge.workspace_confirmation import (
  OfflineConfirmationProvider,
  SovereignConfirmationProvider,
  WorkspaceCLIConfirmationProvider,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def workspace_provider() -> WorkspaceCLIConfirmationProvider:
  """Workspace CLI provider with fast polling for tests."""
  return WorkspaceCLIConfirmationProvider(
    space_id="spaces/test-space",
    poll_interval_secs=0.01,
    poll_timeout_secs=0.05,
    gws_binary="gws",
  )


@pytest.fixture()
def offline_provider() -> OfflineConfirmationProvider:
  """Offline IPC provider."""
  return OfflineConfirmationProvider(ipc_socket_path="/tmp/test_agnt.sock")


@pytest.fixture()
def sovereign_provider() -> SovereignConfirmationProvider:
  """Sovereign provider with fast timeouts."""
  return SovereignConfirmationProvider(
    space_id="spaces/test-space",
    ipc_socket_path="/tmp/test_agnt.sock",
    poll_timeout_secs=0.05,
  )


SAMPLE_ARGS = {"document_id": "doc123", "action": "delete"}
SAMPLE_TAGS = frozenset({"destructive", "write"})


# ---------------------------------------------------------------------------
# WorkspaceCLIConfirmationProvider Tests
# ---------------------------------------------------------------------------


class TestWorkspaceCLIConfirmationProvider:
  """Tests for the Google Workspace CLI confirmation provider."""

  def test_deny_when_gws_not_found(
    self, workspace_provider: WorkspaceCLIConfirmationProvider
  ) -> None:
    """FAIL-CLOSED: deny when gws binary is not installed."""
    with patch("shutil.which", return_value=None):
      result = workspace_provider.request_confirmation(
        "delete_document",
        SAMPLE_ARGS,
        RiskTier.CRITICAL,
        SAMPLE_TAGS,
      )
    assert result is False

  def test_deny_when_post_fails(
    self, workspace_provider: WorkspaceCLIConfirmationProvider
  ) -> None:
    """FAIL-CLOSED: deny when gws chat create fails."""
    with (
      patch("shutil.which", return_value="/usr/local/bin/gws"),
      patch("subprocess.run") as mock_run,
    ):
      mock_run.return_value = subprocess.CompletedProcess(
        args=[],
        returncode=1,
        stdout="",
        stderr="API error",
      )
      result = workspace_provider.request_confirmation(
        "delete_document",
        SAMPLE_ARGS,
        RiskTier.HIGH,
        SAMPLE_TAGS,
      )
    assert result is False

  def test_deny_when_response_missing_thread(
    self, workspace_provider: WorkspaceCLIConfirmationProvider
  ) -> None:
    """FAIL-CLOSED: deny when gws response lacks thread name."""
    with (
      patch("shutil.which", return_value="/usr/local/bin/gws"),
      patch("subprocess.run") as mock_run,
    ):
      mock_run.return_value = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout=json.dumps({"name": "msg1"}),
        stderr="",
      )
      result = workspace_provider.request_confirmation(
        "delete_document",
        SAMPLE_ARGS,
        RiskTier.HIGH,
        SAMPLE_TAGS,
      )
    assert result is False

  def test_approve_when_attorney_approves(
    self, workspace_provider: WorkspaceCLIConfirmationProvider
  ) -> None:
    """APPROVE: attorney replies APPROVE in the thread."""
    create_response = json.dumps(
      {
        "name": "spaces/test/messages/msg1",
        "thread": {"name": "spaces/test/threads/thread1"},
      }
    )
    list_response = json.dumps(
      {
        "messages": [{"text": "APPROVE"}],
      }
    )

    with (
      patch("shutil.which", return_value="/usr/local/bin/gws"),
      patch("subprocess.run") as mock_run,
    ):
      mock_run.side_effect = [
        subprocess.CompletedProcess(
          args=[], returncode=0, stdout=create_response, stderr=""
        ),
        subprocess.CompletedProcess(
          args=[], returncode=0, stdout=list_response, stderr=""
        ),
      ]
      result = workspace_provider.request_confirmation(
        "delete_document",
        SAMPLE_ARGS,
        RiskTier.HIGH,
        SAMPLE_TAGS,
      )
    assert result is True

  def test_deny_when_attorney_denies(
    self, workspace_provider: WorkspaceCLIConfirmationProvider
  ) -> None:
    """DENY: attorney replies DENY in the thread."""
    create_response = json.dumps(
      {
        "name": "spaces/test/messages/msg1",
        "thread": {"name": "spaces/test/threads/thread1"},
      }
    )
    list_response = json.dumps({"messages": [{"text": "DENY this action"}]})

    with (
      patch("shutil.which", return_value="/usr/local/bin/gws"),
      patch("subprocess.run") as mock_run,
    ):
      mock_run.side_effect = [
        subprocess.CompletedProcess(
          args=[], returncode=0, stdout=create_response, stderr=""
        ),
        subprocess.CompletedProcess(
          args=[], returncode=0, stdout=list_response, stderr=""
        ),
      ]
      result = workspace_provider.request_confirmation(
        "delete_document",
        SAMPLE_ARGS,
        RiskTier.CRITICAL,
        SAMPLE_TAGS,
      )
    assert result is False

  def test_deny_on_poll_timeout(
    self, workspace_provider: WorkspaceCLIConfirmationProvider
  ) -> None:
    """FAIL-CLOSED: deny when poll times out without response."""
    create_response = json.dumps(
      {
        "name": "spaces/test/messages/msg1",
        "thread": {"name": "spaces/test/threads/thread1"},
      }
    )
    # No APPROVE/DENY in any response
    list_response = json.dumps({"messages": [{"text": "I'll review later"}]})

    with (
      patch("shutil.which", return_value="/usr/local/bin/gws"),
      patch("subprocess.run") as mock_run,
    ):
      mock_run.side_effect = [
        subprocess.CompletedProcess(
          args=[], returncode=0, stdout=create_response, stderr=""
        ),
        *[
          subprocess.CompletedProcess(
            args=[], returncode=0, stdout=list_response, stderr=""
          )
          for _ in range(50)
        ],
      ]
      result = workspace_provider.request_confirmation(
        "update_case",
        SAMPLE_ARGS,
        RiskTier.HIGH,
        SAMPLE_TAGS,
      )
    assert result is False

  def test_deny_on_subprocess_timeout(
    self, workspace_provider: WorkspaceCLIConfirmationProvider
  ) -> None:
    """FAIL-CLOSED: deny when subprocess times out."""
    with (
      patch("shutil.which", return_value="/usr/local/bin/gws"),
      patch("subprocess.run", side_effect=subprocess.TimeoutExpired("gws", 30)),
    ):
      result = workspace_provider.request_confirmation(
        "delete_document",
        SAMPLE_ARGS,
        RiskTier.HIGH,
        SAMPLE_TAGS,
      )
    assert result is False

  def test_deny_on_os_error(
    self, workspace_provider: WorkspaceCLIConfirmationProvider
  ) -> None:
    """FAIL-CLOSED: deny when OS error occurs."""
    with (
      patch("shutil.which", return_value="/usr/local/bin/gws"),
      patch("subprocess.run", side_effect=OSError("Permission denied")),
    ):
      result = workspace_provider.request_confirmation(
        "delete_document",
        SAMPLE_ARGS,
        RiskTier.HIGH,
        SAMPLE_TAGS,
      )
    assert result is False

  def test_args_are_redacted_in_message(
    self, workspace_provider: WorkspaceCLIConfirmationProvider
  ) -> None:
    """Verify args values are never sent — only types."""
    with (
      patch("shutil.which", return_value="/usr/local/bin/gws"),
      patch("subprocess.run") as mock_run,
    ):
      mock_run.return_value = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout=json.dumps({"thread": {"name": "t1"}}),
        stderr="",
      )
      workspace_provider._poll_timeout = 0.0  # Skip polling
      workspace_provider.request_confirmation(
        "sensitive_fn",
        {"secret_key": "s3cr3t", "patient_id": 12345},
        RiskTier.CRITICAL,
        SAMPLE_TAGS,
      )

      call_args = mock_run.call_args_list[0]
      # The text argument should contain type names, never values
      text_arg = call_args[0][0][-1] if call_args[0] else ""
      assert "s3cr3t" not in text_arg
      assert "12345" not in text_arg

  def test_repr(self, workspace_provider: WorkspaceCLIConfirmationProvider) -> None:
    """Repr includes configuration details."""
    r = repr(workspace_provider)
    assert "spaces/test-space" in r
    assert "gws" in r


# ---------------------------------------------------------------------------
# OfflineConfirmationProvider Tests
# ---------------------------------------------------------------------------


class TestOfflineConfirmationProvider:
  """Tests for the local IPC fallback provider."""

  def test_deny_when_socket_not_found(
    self, offline_provider: OfflineConfirmationProvider
  ) -> None:
    """FAIL-CLOSED: deny when Unix socket does not exist."""
    result = offline_provider.request_confirmation(
      "delete_case",
      SAMPLE_ARGS,
      RiskTier.HIGH,
      SAMPLE_TAGS,
    )
    assert result is False

  @patch("socket.socket")
  def test_deny_when_connection_refused(
    self, mock_socket_cls: MagicMock, offline_provider: OfflineConfirmationProvider
  ) -> None:
    """FAIL-CLOSED: deny when socket connection is refused."""
    mock_sock = MagicMock()
    mock_sock.__enter__ = MagicMock(return_value=mock_sock)
    mock_sock.__exit__ = MagicMock(return_value=False)
    mock_sock.connect.side_effect = ConnectionRefusedError()
    mock_socket_cls.return_value = mock_sock

    result = offline_provider.request_confirmation(
      "delete_case",
      SAMPLE_ARGS,
      RiskTier.HIGH,
      SAMPLE_TAGS,
    )
    assert result is False

  def test_repr(self, offline_provider: OfflineConfirmationProvider) -> None:
    """Repr includes socket path."""
    assert "test_agnt" in repr(offline_provider)


# ---------------------------------------------------------------------------
# SovereignConfirmationProvider Tests
# ---------------------------------------------------------------------------


class TestSovereignConfirmationProvider:
  """Tests for the two-tier sovereign provider."""

  def test_uses_gws_when_available(
    self, sovereign_provider: SovereignConfirmationProvider
  ) -> None:
    """Routes to GWS CLI when binary is available."""
    with (
      patch.object(
        sovereign_provider._primary,
        "_gws_available",
        return_value=True,
      ),
      patch.object(
        sovereign_provider._primary,
        "request_confirmation",
        return_value=True,
      ) as mock_gws,
    ):
      result = sovereign_provider.request_confirmation(
        "approve_filing",
        SAMPLE_ARGS,
        RiskTier.HIGH,
        SAMPLE_TAGS,
      )
    assert result is True
    mock_gws.assert_called_once()

  def test_falls_back_to_ipc_when_gws_unavailable(
    self, sovereign_provider: SovereignConfirmationProvider
  ) -> None:
    """Falls back to local IPC when gws is not installed."""
    with (
      patch.object(
        sovereign_provider._primary,
        "_gws_available",
        return_value=False,
      ),
      patch.object(
        sovereign_provider._fallback,
        "request_confirmation",
        return_value=False,
      ) as mock_ipc,
    ):
      result = sovereign_provider.request_confirmation(
        "delete_case",
        SAMPLE_ARGS,
        RiskTier.CRITICAL,
        SAMPLE_TAGS,
      )
    assert result is False
    mock_ipc.assert_called_once()

  def test_repr(self, sovereign_provider: SovereignConfirmationProvider) -> None:
    """Repr shows both tiers."""
    r = repr(sovereign_provider)
    assert "Sovereign" in r
    assert "primary" in r
    assert "fallback" in r
