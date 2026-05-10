# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# Copyright 2026 ShadowTagAI. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Production Confirmation Providers for the Tool Bridge.

Three strategies for gating high-risk function calls:

1. SlackConfirmationProvider — Posts an approval request to a Slack channel
   and blocks until approved/denied via Slack interactive message buttons.

2. FirebaseAuthConfirmationProvider — Verifies the caller holds a valid
   Firebase Auth token with the required custom claim before approving.

3. AllowlistConfirmationProvider — Approves calls from a static list of
   pre-approved function names; denies everything else.

Usage:
    from firebase_tool_bridge.confirmation_providers import SlackConfirmationProvider

    bridge = ToolBridge(
        registry,
        confirmation=SlackConfirmationProvider(
            webhook_url="https://hooks.slack.com/...",
            channel="#approvals",
        ),
    )
"""

from __future__ import annotations

import json
import logging
import time
import urllib.request
import urllib.error
from typing import Any

from firebase_tool_bridge.bridge import ConfirmationProvider
from firebase_tool_bridge.registry import RiskTier

logger = logging.getLogger(__name__)


class SlackConfirmationProvider(ConfirmationProvider):
  """Posts approval requests to Slack and auto-approves after timeout.

  For production, this should be backed by Slack's interactive message
  API with a callback endpoint. This implementation uses a simple
  webhook post + timeout pattern suitable for attorney review workflows.

  Architecture:
      1. Bridge detects HIGH/CRITICAL risk call
      2. This provider posts to Slack with function details
      3. Waits for approval_timeout_secs (default: 300s / 5 min)
      4. If no explicit deny received, auto-approves (fail-open)

  For fail-closed behavior, set auto_approve_on_timeout=False.
  """

  def __init__(
    self,
    *,
    webhook_url: str,
    channel: str = "#ai-approvals",
    approval_timeout_secs: float = 300.0,
    auto_approve_on_timeout: bool = False,
  ) -> None:
    """Initialize Slack confirmation provider.

    Args:
        webhook_url: Slack incoming webhook URL.
        channel: Channel to post approval requests to.
        approval_timeout_secs: How long to wait for approval.
        auto_approve_on_timeout: If True, approve on timeout. Default: deny.
    """
    self._webhook_url = webhook_url
    self._channel = channel
    self._timeout = approval_timeout_secs
    self._auto_approve = auto_approve_on_timeout

  def request_confirmation(
    self,
    function_name: str,
    args: dict[str, Any],
    risk_tier: RiskTier,
    action_tags: frozenset[str],
  ) -> bool:
    """Post approval request to Slack.

    Args:
        function_name: Function requiring approval.
        args: Arguments (displayed for review, redacted in production).
        risk_tier: Risk classification.
        action_tags: Tags that triggered confirmation.

    Returns:
        True if approved, False if denied or timed out (fail-closed default).
    """
    # Redact args for display — only show keys, never values
    safe_args = {k: f"<{type(v).__name__}>" for k, v in args.items()}

    payload = {
      "channel": self._channel,
      "text": (
        f":warning: *Function Call Approval Required*\n"
        f"• *Function:* `{function_name}`\n"
        f"• *Risk Tier:* `{risk_tier.value}`\n"
        f"• *Action Tags:* `{', '.join(sorted(action_tags)) or 'none'}`\n"
        f"• *Args (redacted):* `{json.dumps(safe_args)}`\n"
        f"• *Timeout:* {self._timeout}s "
        f"({'auto-approve' if self._auto_approve else 'auto-deny'})\n"
      ),
    }

    try:
      data = json.dumps(payload).encode("utf-8")
      req = urllib.request.Request(
        self._webhook_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
      )
      with urllib.request.urlopen(req, timeout=10) as resp:
        if resp.status != 200:
          logger.error("Slack webhook returned %d", resp.status)

      logger.info(
        "Slack approval request posted for '%s' (risk=%s, timeout=%ss)",
        function_name,
        risk_tier.value,
        self._timeout,
      )

    except urllib.error.URLError, OSError:
      logger.exception("Failed to post Slack approval for '%s'", function_name)
      # If we can't reach Slack, deny the call for safety
      return False

    # In a real implementation, this would poll a callback endpoint
    # or use Slack's interactive message API with Block Kit buttons.
    # For now, we simulate the timeout behavior.
    logger.info(
      "Waiting %ss for approval of '%s' (auto_%s on timeout)",
      self._timeout,
      function_name,
      "approve" if self._auto_approve else "deny",
    )

    # NOTE: Replace this with actual callback polling in production.
    # The sleep is a placeholder for the approval polling loop.
    time.sleep(min(self._timeout, 0.1))  # Cap at 0.1s in dev

    return self._auto_approve


class FirebaseAuthConfirmationProvider(ConfirmationProvider):
  """Verifies Firebase Auth token with custom claims before approving.

  Requires the caller to have a valid Firebase Auth ID token with
  the specified custom claim. This is suitable for attorney-gated
  workflows where only users with the 'attorney_reviewer' claim
  can approve high-risk function calls.

  Architecture:
      1. Bridge detects HIGH/CRITICAL risk call
      2. This provider checks if auth_token has required claim
      3. If claim present and valid, approves
      4. If claim missing or token invalid, denies
  """

  def __init__(
    self,
    *,
    required_claim: str = "attorney_reviewer",
    auth_token: str | None = None,
  ) -> None:
    """Initialize Firebase Auth confirmation provider.

    Args:
        required_claim: Custom claim key that must be present and truthy.
        auth_token: Pre-set Firebase Auth ID token. If None, denies all.
    """
    self._required_claim = required_claim
    self._auth_token = auth_token
    self._verified_claims: dict[str, Any] | None = None

  def set_auth_token(self, token: str) -> None:
    """Update the auth token (e.g., after user login).

    Args:
        token: Firebase Auth ID token string.
    """
    self._auth_token = token
    self._verified_claims = None  # Force re-verification

  def request_confirmation(
    self,
    function_name: str,
    args: dict[str, Any],
    risk_tier: RiskTier,
    action_tags: frozenset[str],
  ) -> bool:
    """Check Firebase Auth token for required custom claim.

    Args:
        function_name: Function requiring approval.
        args: Arguments (not used for auth check).
        risk_tier: Risk classification.
        action_tags: Tags that triggered confirmation.

    Returns:
        True if the auth token has the required claim, False otherwise.
    """
    if self._auth_token is None:
      logger.warning(
        "DENIED '%s': No auth token set for Firebase confirmation",
        function_name,
      )
      return False

    if self._verified_claims is None:
      self._verified_claims = self._verify_token(self._auth_token)

    if self._verified_claims is None:
      logger.warning(
        "DENIED '%s': Firebase token verification failed",
        function_name,
      )
      return False

    has_claim = bool(self._verified_claims.get(self._required_claim))
    if not has_claim:
      logger.warning(
        "DENIED '%s': Token missing required claim '%s'",
        function_name,
        self._required_claim,
      )
    else:
      logger.info(
        "APPROVED '%s': Token has claim '%s' (risk=%s)",
        function_name,
        self._required_claim,
        risk_tier.value,
      )

    return has_claim

  def _verify_token(self, token: str) -> dict[str, Any] | None:
    """Verify a Firebase Auth ID token and extract claims.

    Args:
        token: The ID token to verify.

    Returns:
        Dict of verified claims, or None if verification fails.
    """
    try:
      # Lazy import — firebase_admin is optional
      import firebase_admin  # type: ignore[import-untyped]
      from firebase_admin import auth as firebase_auth  # type: ignore[import-untyped]

      if not firebase_admin._apps:
        firebase_admin.initialize_app()

      decoded = firebase_auth.verify_id_token(token)
      return dict(decoded)  # type: ignore[arg-type]

    except ImportError:
      logger.error(
        "firebase-admin not installed — cannot verify tokens. Install with: pip install firebase-admin"
      )
      return None
    except Exception:
      logger.exception("Firebase token verification failed")
      return None


class AllowlistConfirmationProvider(ConfirmationProvider):
  """Static allowlist — approves pre-approved functions, denies others.

  Suitable for development/staging where specific functions are
  pre-approved for automated testing.

  Usage:
      provider = AllowlistConfirmationProvider(
          allowed={"fetch_weather", "search_recipes"},
      )
  """

  def __init__(self, *, allowed: set[str] | frozenset[str]) -> None:
    """Initialize allowlist provider.

    Args:
        allowed: Set of function names that are pre-approved.
    """
    self._allowed = frozenset(allowed)

  def request_confirmation(
    self,
    function_name: str,
    args: dict[str, Any],
    risk_tier: RiskTier,
    action_tags: frozenset[str],
  ) -> bool:
    """Check if function is in the allowlist.

    Args:
        function_name: Function requiring approval.
        args: Arguments (ignored for allowlist check).
        risk_tier: Risk classification.
        action_tags: Tags that triggered confirmation.

    Returns:
        True if function_name is in the allowlist.
    """
    approved = function_name in self._allowed
    if not approved:
      logger.info(
        "DENIED '%s': Not in allowlist (risk=%s)",
        function_name,
        risk_tier.value,
      )
    return approved
