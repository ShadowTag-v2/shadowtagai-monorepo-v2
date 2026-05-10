# Copyright 2026 ShadowTagAI. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Sovereign Workspace Confirmation Providers.

Three-tier fail-closed confirmation hierarchy for attorney-gated
function call approval:

1. WorkspaceCLIConfirmationProvider — Posts approval requests via the
   Google Workspace CLI (`gws`) to a Google Chat space and polls for
   APPROVE/DENY responses from authorized reviewers.

2. OfflineConfirmationProvider — Falls back to a local Unix domain
   socket IPC channel for environments without network access.

3. SovereignConfirmationProvider — Two-tier cascade: tries GWS CLI
   first, falls back to local IPC. If both fail, denies (fail-closed).

All providers follow fail-closed semantics: ambiguity → denial.
"""

from __future__ import annotations

import json
import logging
import shutil
import socket
import subprocess
import time
from typing import Any

from firebase_tool_bridge.bridge import ConfirmationProvider
from firebase_tool_bridge.registry import RiskTier

logger = logging.getLogger(__name__)


class WorkspaceCLIConfirmationProvider(ConfirmationProvider):
  """Posts approval requests to Google Chat via the GWS CLI.

  Uses the `gws` binary (Google Workspace CLI) to post a message
  to a Chat space and poll the thread for APPROVE/DENY responses.

  Fail-closed: if `gws` is not installed, the subprocess fails,
  or polling times out without a clear APPROVE, the call is denied.
  """

  def __init__(
    self,
    *,
    space_id: str,
    poll_interval_secs: float = 5.0,
    poll_timeout_secs: float = 300.0,
    gws_binary: str = "gws",
  ) -> None:
    """Initialize GWS Chat confirmation provider.

    Args:
        space_id: Google Chat space resource name (e.g. 'spaces/xxx').
        poll_interval_secs: Seconds between poll attempts.
        poll_timeout_secs: Maximum time to wait for a response.
        gws_binary: Name or path of the gws CLI binary.
    """
    self._space_id = space_id
    self._poll_interval = poll_interval_secs
    self._poll_timeout = poll_timeout_secs
    self._gws_binary = gws_binary

  def _gws_available(self) -> bool:
    """Check if the gws binary is installed."""
    return shutil.which(self._gws_binary) is not None

  def request_confirmation(
    self,
    function_name: str,
    args: dict[str, Any],
    risk_tier: RiskTier,
    action_tags: frozenset[str],
  ) -> bool:
    """Post approval request to Google Chat and poll for response.

    Args:
        function_name: Function requiring approval.
        args: Arguments (redacted — only types are shown).
        risk_tier: Risk classification.
        action_tags: Tags that triggered confirmation.

    Returns:
        True if APPROVE received, False otherwise (fail-closed).
    """
    if not self._gws_available():
      logger.warning(
        "DENIED '%s': gws binary not found — fail-closed",
        function_name,
      )
      return False

    # Redact args — only expose types, never values
    safe_args = json.dumps({k: f"<{type(v).__name__}>" for k, v in args.items()})

    message_text = (
      f"⚠️ *Function Call Approval Required*\n"
      f"• *Function:* `{function_name}`\n"
      f"• *Risk Tier:* `{risk_tier.value}`\n"
      f"• *Tags:* `{', '.join(sorted(action_tags)) or 'none'}`\n"
      f"• *Args (types only):* `{safe_args}`\n"
      f"Reply APPROVE or DENY within {self._poll_timeout}s."
    )

    # Post message to Chat space
    thread_name = self._post_message(message_text)
    if thread_name is None:
      return False

    # Poll for APPROVE/DENY
    return self._poll_thread(thread_name)

  def _post_message(self, text: str) -> str | None:
    """Post a message to the Chat space via gws CLI.

    Returns the thread name for polling, or None on failure.
    """
    try:
      result = subprocess.run(
        [
          self._gws_binary,
          "chat",
          "messages",
          "create",
          "--space",
          self._space_id,
          "--text",
          text,
        ],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
      )

      if result.returncode != 0:
        logger.error(
          "gws chat create failed (rc=%d): %s",
          result.returncode,
          result.stderr,
        )
        return None

      data = json.loads(result.stdout)
      thread = data.get("thread", {})
      thread_name = thread.get("name")

      if not thread_name:
        logger.error(
          "gws response missing thread name: %s",
          result.stdout[:200],
        )
        return None

      return thread_name

    except subprocess.TimeoutExpired:
      logger.error("gws chat create timed out after 30s")
      return None
    except OSError:
      logger.exception("OS error executing gws binary")
      return None
    except json.JSONDecodeError:
      logger.exception("Failed to parse gws response as JSON")
      return None

  def _poll_thread(self, thread_name: str) -> bool:
    """Poll the Chat thread for APPROVE/DENY response.

    Returns True only if an explicit APPROVE is found.
    """
    deadline = time.monotonic() + self._poll_timeout

    while time.monotonic() < deadline:
      try:
        result = subprocess.run(
          [
            self._gws_binary,
            "chat",
            "messages",
            "list",
            "--thread",
            thread_name,
          ],
          capture_output=True,
          text=True,
          timeout=15,
          check=False,
        )

        if result.returncode == 0:
          data = json.loads(result.stdout)
          messages = data.get("messages", [])
          for msg in messages:
            text = msg.get("text", "").upper()
            if "APPROVE" in text:
              logger.info(
                "APPROVED via Chat thread: %s",
                thread_name,
              )
              return True
            if "DENY" in text:
              logger.info(
                "DENIED via Chat thread: %s",
                thread_name,
              )
              return False

      except subprocess.TimeoutExpired, json.JSONDecodeError, OSError:
        logger.debug("Poll error on thread %s", thread_name)

      time.sleep(self._poll_interval)

    logger.warning(
      "Poll timeout (%ss) for thread %s — fail-closed DENY",
      self._poll_timeout,
      thread_name,
    )
    return False

  def __repr__(self) -> str:
    return f"WorkspaceCLIConfirmationProvider(space_id='{self._space_id}', gws_binary='{self._gws_binary}')"


class OfflineConfirmationProvider(ConfirmationProvider):
  """Local Unix domain socket IPC fallback for offline environments.

  Sends a confirmation request to a local AGNT daemon listening
  on a Unix socket. If the socket doesn't exist or connection
  is refused, the request is denied (fail-closed).
  """

  def __init__(self, *, ipc_socket_path: str = "/tmp/agnt.sock") -> None:
    """Initialize offline IPC provider.

    Args:
        ipc_socket_path: Path to the Unix domain socket.
    """
    self._socket_path = ipc_socket_path

  def request_confirmation(
    self,
    function_name: str,
    args: dict[str, Any],
    risk_tier: RiskTier,
    action_tags: frozenset[str],
  ) -> bool:
    """Request confirmation via local Unix socket.

    Args:
        function_name: Function requiring approval.
        args: Arguments (sent to local daemon only).
        risk_tier: Risk classification.
        action_tags: Tags that triggered confirmation.

    Returns:
        True if daemon approves, False otherwise.
    """
    import os

    if not os.path.exists(self._socket_path):
      logger.warning(
        "DENIED '%s': IPC socket %s not found — fail-closed",
        function_name,
        self._socket_path,
      )
      return False

    try:
      with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.settimeout(5.0)
        sock.connect(self._socket_path)

        request = json.dumps(
          {
            "type": "confirmation_request",
            "function": function_name,
            "risk_tier": risk_tier.value,
            "tags": sorted(action_tags),
          }
        ).encode("utf-8")

        sock.sendall(request + b"\n")

        response = sock.recv(1024).decode("utf-8").strip()
        return response.upper() == "APPROVE"

    except ConnectionRefusedError:
      logger.warning(
        "DENIED '%s': IPC connection refused at %s",
        function_name,
        self._socket_path,
      )
      return False
    except OSError:
      logger.exception(
        "DENIED '%s': IPC socket error at %s",
        function_name,
        self._socket_path,
      )
      return False

  def __repr__(self) -> str:
    return f"OfflineConfirmationProvider(socket='{self._socket_path}')"


class SovereignConfirmationProvider(ConfirmationProvider):
  """Two-tier sovereign confirmation cascade.

  Tier 1: Google Workspace CLI (GWS Chat) — requires ADC auth
  Tier 2: Local Unix IPC — fallback for offline environments

  If both fail, the request is denied (fail-closed).
  """

  def __init__(
    self,
    *,
    space_id: str = "spaces/default",
    ipc_socket_path: str = "/tmp/agnt.sock",
    poll_timeout_secs: float = 300.0,
  ) -> None:
    """Initialize sovereign two-tier provider.

    Args:
        space_id: Google Chat space for GWS tier.
        ipc_socket_path: Unix socket path for IPC tier.
        poll_timeout_secs: Timeout for GWS polling.
    """
    self._primary = WorkspaceCLIConfirmationProvider(
      space_id=space_id,
      poll_timeout_secs=poll_timeout_secs,
    )
    self._fallback = OfflineConfirmationProvider(
      ipc_socket_path=ipc_socket_path,
    )

  def request_confirmation(
    self,
    function_name: str,
    args: dict[str, Any],
    risk_tier: RiskTier,
    action_tags: frozenset[str],
  ) -> bool:
    """Cascade through confirmation tiers.

    Args:
        function_name: Function requiring approval.
        args: Arguments to pass through.
        risk_tier: Risk classification.
        action_tags: Tags that triggered confirmation.

    Returns:
        True if any tier approves, False if all deny.
    """
    # Tier 1: Try GWS Chat if available
    if self._primary._gws_available():
      logger.info(
        "Sovereign: routing '%s' to GWS Chat (Tier 1)",
        function_name,
      )
      return self._primary.request_confirmation(
        function_name,
        args,
        risk_tier,
        action_tags,
      )

    # Tier 2: Fallback to local IPC
    logger.info(
      "Sovereign: GWS unavailable, falling back to IPC (Tier 2) for '%s'",
      function_name,
    )
    return self._fallback.request_confirmation(
      function_name,
      args,
      risk_tier,
      action_tags,
    )

  def __repr__(self) -> str:
    return f"SovereignConfirmationProvider(primary={self._primary!r}, fallback={self._fallback!r})"
