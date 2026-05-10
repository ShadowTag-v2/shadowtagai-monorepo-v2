# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# Copyright 2026 ShadowTagAI. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Tool Bridge — the execution dispatch core for Firebase AI Logic.

This module implements the critical loop:
  1. Receive function call from Firebase SDK
  2. Validate against FunctionRegistry
  3. Gate on confirmation if risk requires it
  4. Execute the approved callable
  5. Log evidence
  6. Return structured response for the model

Architecture:
    Model proposes → Bridge validates → Confirmation gate → App executes → Evidence logs → SDK returns

The bridge NEVER executes unregistered functions. Every call is evidence-logged.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

from firebase_tool_bridge.evidence import EvidenceLogger
from firebase_tool_bridge.registry import FunctionRegistry, RiskTier

logger = logging.getLogger(__name__)


class CallStatus(StrEnum):
  """Outcome status for a bridge call."""

  SUCCESS = "success"
  REJECTED_UNREGISTERED = "rejected_unregistered"
  REJECTED_CONFIRMATION = "rejected_confirmation"
  ERROR = "error"


@dataclass(frozen=True, slots=True)
class BridgeResult:
  """Result of a bridge function call dispatch."""

  status: CallStatus
  function_name: str
  result: Any = None
  error: str | None = None

  def to_function_response(self) -> dict[str, Any]:
    """Format as a Firebase function response payload.

    Returns a dict suitable for passing back to the Firebase SDK
    as a FunctionResponse content part.
    """
    if self.status == CallStatus.SUCCESS:
      return {"result": self.result}
    return {
      "error": self.error or self.status.value,
      "status": self.status.value,
    }


class ConfirmationProvider:
  """Abstract confirmation gate.

  Subclass this to implement real confirmation UIs
  (modal dialogs, Slack approvals, etc.).

  The default implementation auto-approves everything,
  which is appropriate only for development/testing.
  """

  def request_confirmation(
    self,
    function_name: str,
    args: dict[str, Any],
    risk_tier: RiskTier,
    action_tags: frozenset[str],
  ) -> bool:
    """Request user confirmation for a high-risk call.

    Args:
        function_name: Name of the function requiring confirmation.
        args: The arguments to be passed (for display, NOT execution).
        risk_tier: The risk classification.
        action_tags: Tags triggering confirmation.

    Returns:
        True if confirmed, False if denied.
    """
    logger.warning(
      "Auto-approving '%s' (risk=%s) — override ConfirmationProvider for production",
      function_name,
      risk_tier.value,
    )
    return True


class ToolBridge:
  """Execution dispatch core for Firebase AI Logic function calls.

  Usage:
      registry = FunctionRegistry()
      registry.register("get_weather", get_weather, RiskTier.LOW)

      bridge = ToolBridge(registry)
      result = bridge.handle("get_weather", {"city": "Boston"})
      # result.to_function_response() → {"result": {"temp": 38, "unit": "F"}}

  Production usage with confirmation gate:
      class SlackConfirmation(ConfirmationProvider):
          def request_confirmation(self, fn, args, risk, tags):
              return slack_approval_flow(fn, args)

      bridge = ToolBridge(registry, confirmation=SlackConfirmation())
  """

  def __init__(
    self,
    registry: FunctionRegistry,
    *,
    evidence: EvidenceLogger | None = None,
    confirmation: ConfirmationProvider | None = None,
    repo_root: Path | None = None,
  ) -> None:
    """Initialize the tool bridge.

    Args:
        registry: The function registry to validate calls against.
        evidence: Evidence logger instance. Created automatically if None.
        confirmation: Confirmation provider for high-risk calls.
        repo_root: Path to monorepo root for evidence logging.
    """
    self._registry = registry
    self._evidence = evidence or EvidenceLogger(repo_root=repo_root, async_writes=True)
    self._confirmation = confirmation or ConfirmationProvider()
    self._pre_hooks: list[Callable[..., None]] = []
    self._post_hooks: list[Callable[..., None]] = []

  def add_pre_hook(self, hook: Callable[..., None]) -> None:
    """Register a hook called before function execution.

    Pre-hooks receive (function_name, args, risk_tier).
    Use for rate limiting, audit logging, or argument enrichment.
    """
    self._pre_hooks.append(hook)

  def add_post_hook(self, hook: Callable[..., None]) -> None:
    """Register a hook called after function execution.

    Post-hooks receive (function_name, result, duration_ms).
    Use for metrics, caching, or downstream notifications.
    """
    self._post_hooks.append(hook)

  def handle(
    self,
    function_name: str,
    args: dict[str, Any] | None = None,
  ) -> BridgeResult:
    """Dispatch a function call through the bridge.

    This is the primary entry point. Every call is:
    1. Validated against the registry
    2. Gated on confirmation if required
    3. Executed
    4. Evidence-logged

    Args:
        function_name: The function name from the model's FunctionCall.
        args: The arguments dict from the model's FunctionCall.

    Returns:
        BridgeResult with status, result data, and any error.
    """
    args = args or {}
    start = self._evidence.timer()

    # --- Step 1: Registry lookup ---
    registered = self._registry.get(function_name)
    if registered is None:
      logger.warning("REJECTED: '%s' is not registered", function_name)
      self._evidence.log(
        function_name=function_name,
        args=args,
        risk_tier="unknown",
        confirmation_required=False,
        confirmation_received=None,
        result_summary="rejected: unregistered function",
        duration_ms=self._evidence.elapsed_ms(start),
        success=False,
        error="Function not registered",
      )
      return BridgeResult(
        status=CallStatus.REJECTED_UNREGISTERED,
        function_name=function_name,
        error=f"Function '{function_name}' is not registered.",
      )

    # --- Step 2: Confirmation gate ---
    requires_confirmation = registered.requires_confirmation
    confirmation_received: bool | None = None

    if requires_confirmation:
      confirmation_received = self._confirmation.request_confirmation(
        function_name=function_name,
        args=args,
        risk_tier=registered.risk_tier,
        action_tags=registered.action_tags,
      )
      if not confirmation_received:
        logger.info(
          "DENIED: '%s' confirmation rejected (risk=%s)",
          function_name,
          registered.risk_tier.value,
        )
        self._evidence.log(
          function_name=function_name,
          args=args,
          risk_tier=registered.risk_tier.value,
          confirmation_required=True,
          confirmation_received=False,
          result_summary="rejected: user denied confirmation",
          duration_ms=self._evidence.elapsed_ms(start),
          success=False,
          error="User denied confirmation",
        )
        return BridgeResult(
          status=CallStatus.REJECTED_CONFIRMATION,
          function_name=function_name,
          error="User denied confirmation for this action.",
        )

    # --- Step 3: Pre-hooks ---
    for hook in self._pre_hooks:
      try:
        hook(function_name, args, registered.risk_tier)
      except Exception:
        logger.exception("Pre-hook failed for '%s'", function_name)

    # --- Step 4: Execute ---
    try:
      result = registered.callable(**args)

      # Summarize result for evidence (never raw data)
      result_summary = _summarize_result(result)

      duration_ms = self._evidence.elapsed_ms(start)

      # --- Step 5: Post-hooks ---
      for hook in self._post_hooks:
        try:
          hook(function_name, result, duration_ms)
        except Exception:
          logger.exception("Post-hook failed for '%s'", function_name)

      # --- Step 6: Evidence ---
      self._evidence.log(
        function_name=function_name,
        args=args,
        risk_tier=registered.risk_tier.value,
        confirmation_required=requires_confirmation,
        confirmation_received=confirmation_received,
        result_summary=result_summary,
        duration_ms=duration_ms,
        success=True,
      )

      logger.info(
        "EXECUTED: '%s' (risk=%s, %.1fms)",
        function_name,
        registered.risk_tier.value,
        duration_ms,
      )
      return BridgeResult(
        status=CallStatus.SUCCESS,
        function_name=function_name,
        result=result,
      )

    except Exception as exc:
      duration_ms = self._evidence.elapsed_ms(start)
      error_msg = f"{type(exc).__name__}: {exc}"

      self._evidence.log(
        function_name=function_name,
        args=args,
        risk_tier=registered.risk_tier.value,
        confirmation_required=requires_confirmation,
        confirmation_received=confirmation_received,
        result_summary=f"error: {type(exc).__name__}",
        duration_ms=duration_ms,
        success=False,
        error=error_msg,
      )

      logger.exception("ERROR: '%s' failed after %.1fms", function_name, duration_ms)
      return BridgeResult(
        status=CallStatus.ERROR,
        function_name=function_name,
        error=error_msg,
      )

  def handle_batch(
    self,
    calls: list[tuple[str, dict[str, Any]]],
  ) -> list[BridgeResult]:
    """Dispatch multiple function calls sequentially.

    Firebase AI Logic can return parallel function calls.
    This dispatches them in order with full evidence.

    Args:
        calls: List of (function_name, args) tuples.

    Returns:
        List of BridgeResult, one per call, in order.
    """
    return [self.handle(name, args) for name, args in calls]

  @property
  def registry(self) -> FunctionRegistry:
    """Access the underlying function registry."""
    return self._registry


def _summarize_result(result: Any, *, max_len: int = 200) -> str:
  """Create a safe summary of a function result for evidence logging.

  NEVER stores raw result data — only type and truncated repr.
  """
  if result is None:
    return "None"
  if isinstance(result, dict):
    keys = list(result.keys())[:5]
    return f"dict({len(result)} keys: {keys})"
  if isinstance(result, list):
    return f"list({len(result)} items)"
  if isinstance(result, str):
    if len(result) <= max_len:
      return f"str({len(result)})"
    return f"str({len(result)} chars, truncated)"
  if isinstance(result, (int, float, bool)):
    return f"{type(result).__name__}={result}"
  return f"{type(result).__name__}(len={len(str(result))})"
