# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Activity manager — ported from utils/activityManager.ts.

Tracks CLI vs. user activity time with automatic deduplication of
overlapping operations. Used for billing/telemetry reporting.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from collections.abc import Callable


@dataclass
class ActivityStates:
  """Snapshot of the current activity state."""

  is_user_active: bool = False
  is_cli_active: bool = False
  active_operation_count: int = 0


class ActivityManager:
  """Tracks CLI and user activity with timeout-based deduplication.

  This is a direct port of the upstream ActivityManager class.
  The ``record_callback`` is invoked each time a time delta is recorded
  (replaces the OTel counter from upstream).
  """

  USER_ACTIVITY_TIMEOUT_S = 5.0

  def __init__(
    self,
    *,
    get_now: Callable[[], float] | None = None,
    record_callback: Callable[[float, str], None] | None = None,
  ) -> None:
    self._get_now = get_now or time.monotonic
    self._record_callback = record_callback or (lambda _dt, _kind: None)

    self._active_operations: set[str] = set()
    self._last_user_activity_time: float = 0.0
    self._last_cli_recorded_time: float = self._get_now()
    self._is_cli_active: bool = False

    # Cumulative counters (testable without OTel)
    self.total_user_seconds: float = 0.0
    self.total_cli_seconds: float = 0.0

  # ── User activity ─────────────────────────────────────────────────────

  def record_user_activity(self) -> None:
    """Mark that the user just interacted (typing, commands, etc)."""
    if not self._is_cli_active and self._last_user_activity_time > 0:
      now = self._get_now()
      delta = now - self._last_user_activity_time
      if 0 < delta < self.USER_ACTIVITY_TIMEOUT_S:
        self.total_user_seconds += delta
        self._record_callback(delta, "user")

    self._last_user_activity_time = self._get_now()

  # ── CLI activity ──────────────────────────────────────────────────────

  def start_cli_activity(self, operation_id: str) -> None:
    """Start tracking a CLI operation (tool execution, AI response)."""
    if operation_id in self._active_operations:
      self.end_cli_activity(operation_id)

    was_empty = len(self._active_operations) == 0
    self._active_operations.add(operation_id)

    if was_empty:
      self._is_cli_active = True
      self._last_cli_recorded_time = self._get_now()

  def end_cli_activity(self, operation_id: str) -> None:
    """Stop tracking a CLI operation."""
    self._active_operations.discard(operation_id)

    if not self._active_operations:
      now = self._get_now()
      delta = now - self._last_cli_recorded_time
      if delta > 0:
        self.total_cli_seconds += delta
        self._record_callback(delta, "cli")
      self._last_cli_recorded_time = now
      self._is_cli_active = False

  # ── Introspection ─────────────────────────────────────────────────────

  def get_activity_states(self) -> ActivityStates:
    """Snapshot of current activity for testing/debugging."""
    now = self._get_now()
    delta = now - self._last_user_activity_time
    return ActivityStates(
      is_user_active=(delta < self.USER_ACTIVITY_TIMEOUT_S),
      is_cli_active=self._is_cli_active,
      active_operation_count=len(self._active_operations),
    )

  def reset(self) -> None:
    """Full reset for testing."""
    self._active_operations.clear()
    self._last_user_activity_time = 0.0
    self._last_cli_recorded_time = self._get_now()
    self._is_cli_active = False
    self.total_user_seconds = 0.0
    self.total_cli_seconds = 0.0
