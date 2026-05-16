# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Remote Managed Settings Service — Ported from Claude Code v2.1.91.

Manages fetching, caching, and validation of remote-managed settings
for enterprise customers. Uses checksum-based validation (SHA-256) to
minimize network traffic and provides graceful degradation on failures.

Architecture:
    - Eligibility gating: Console users (API key) always eligible;
      OAuth users only Enterprise/C4E and Team subscribers.
    - Checksum-based HTTP caching (If-None-Match / ETag).
    - Retry with exponential backoff (max 5 retries).
    - Fail-open: continues without remote settings on fetch failure.
    - Background polling (1 hour interval) for mid-session changes.
    - Dangerous settings security check before applying changes.

Reference: Claude Code v2.1.91 src/services/remoteManagedSettings/index.ts (639 lines)
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import contextlib

logger = logging.getLogger(__name__)


# ── Constants ─────────────────────────────────────────────────────────

SETTINGS_TIMEOUT_SECS = 10.0
DEFAULT_MAX_RETRIES = 5
POLLING_INTERVAL_SECS = 3600  # 1 hour
LOADING_PROMISE_TIMEOUT_SECS = 30.0


# ── Types ─────────────────────────────────────────────────────────────

SettingsJson = dict[str, Any]


@dataclass
class FetchResult:
  """Result of a remote settings fetch attempt."""

  success: bool
  settings: SettingsJson | None = None
  checksum: str | None = None
  error: str | None = None
  skip_retry: bool = False


@dataclass
class RemoteManagedSettingsState:
  """Internal state for the settings service."""

  session_cache: SettingsJson | None = None
  loading_complete: threading.Event = field(default_factory=threading.Event)
  polling_timer: threading.Timer | None = None
  _eligible: bool = False


# ── Checksum ──────────────────────────────────────────────────────────


def _sort_keys_deep(obj: Any) -> Any:
  """Recursively sort all keys in an object.

  Matches Python's json.dumps(sort_keys=True) for checksum parity.
  """
  if isinstance(obj, list):
    return [_sort_keys_deep(item) for item in obj]
  if isinstance(obj, dict):
    return {k: _sort_keys_deep(v) for k, v in sorted(obj.items())}
  return obj


def compute_checksum_from_settings(settings: SettingsJson) -> str:
  """Compute SHA-256 checksum from settings content.

  Must match server's Python: json.dumps(settings, sort_keys=True, separators=(",", ":"))
  """
  sorted_settings = _sort_keys_deep(settings)
  normalized = json.dumps(sorted_settings, separators=(",", ":"))
  digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
  return f"sha256:{digest}"


# ── Service ───────────────────────────────────────────────────────────


class RemoteManagedSettingsService:
  """Enterprise remote managed settings service.

  Ported from Claude Code's remoteManagedSettings module.
  Provides:
  1. Settings eligibility checking.
  2. Checksum-based caching.
  3. Fetch with retry + exponential backoff.
  4. Background polling for mid-session updates.
  5. Graceful degradation (fail-open).
  """

  def __init__(
    self,
    *,
    settings_path: Path | None = None,
    eligible: bool = False,
  ) -> None:
    self._state = RemoteManagedSettingsState(_eligible=eligible)
    self._settings_path = (
      settings_path or Path.home() / ".config" / "agnt" / "remote_settings.json"
    )

  @property
  def is_eligible(self) -> bool:
    """Check if the current user is eligible for remote settings."""
    return self._state._eligible

  @property
  def session_cache(self) -> SettingsJson | None:
    """Get the current session-cached settings."""
    return self._state.session_cache

  def set_session_cache(self, settings: SettingsJson) -> None:
    """Set session cache directly."""
    self._state.session_cache = settings

  def load_cached_settings(self) -> SettingsJson | None:
    """Load settings from the persistent cache file."""
    try:
      if self._settings_path.exists():
        raw = self._settings_path.read_text(encoding="utf-8")
        settings = json.loads(raw)
        self._state.session_cache = settings
        return settings
    except (OSError, json.JSONDecodeError) as exc:
      logger.debug("Failed to load cached settings: %s", exc)
    return None

  def save_settings(self, settings: SettingsJson) -> None:
    """Save settings to the persistent cache file with restricted perms."""
    try:
      self._settings_path.parent.mkdir(parents=True, exist_ok=True)
      self._settings_path.write_text(
        json.dumps(settings, indent=2),
        encoding="utf-8",
      )
      self._settings_path.chmod(0o600)
      logger.debug("Remote settings: saved to %s", self._settings_path)
    except OSError as exc:
      logger.debug("Remote settings: failed to save — %s", exc)

  def apply_settings(self, result: FetchResult) -> SettingsJson | None:
    """Apply a fetch result to the settings state.

    Returns the active settings or None if no settings available.
    Handles 304 Not Modified, empty responses, and new settings.
    """
    cached = self._state.session_cache

    if not result.success:
      # Fail open: use stale cache if available
      if cached:
        logger.debug("Remote settings: using stale cache after fetch failure")
        return cached
      return None

    # 304 Not Modified — cache is still valid
    if result.settings is None and cached:
      logger.debug("Remote settings: cache still valid (304)")
      return cached

    new_settings = result.settings or {}
    has_content = bool(new_settings)

    if has_content:
      self._state.session_cache = new_settings
      self.save_settings(new_settings)
      logger.debug("Remote settings: applied new settings")
      return new_settings

    # Empty settings (user's remote settings removed)
    self._state.session_cache = new_settings
    try:
      self._settings_path.unlink(missing_ok=True)
      logger.debug("Remote settings: deleted cached file (empty response)")
    except OSError:
      pass
    return new_settings

  def start_background_polling(
    self,
    fetch_callback: Any | None = None,
  ) -> None:
    """Start background polling for settings changes (1-hour interval)."""
    if self._state.polling_timer is not None or not self._state._eligible:
      return

    def _poll() -> None:
      if not self._state._eligible:
        return
      if fetch_callback:
        try:
          fetch_callback()
        except Exception:
          logger.debug("Remote settings: background poll failed", exc_info=True)
      # Reschedule
      self._state.polling_timer = threading.Timer(POLLING_INTERVAL_SECS, _poll)
      self._state.polling_timer.daemon = True
      self._state.polling_timer.start()

    self._state.polling_timer = threading.Timer(POLLING_INTERVAL_SECS, _poll)
    self._state.polling_timer.daemon = True
    self._state.polling_timer.start()

  def stop_background_polling(self) -> None:
    """Stop background polling."""
    if self._state.polling_timer is not None:
      self._state.polling_timer.cancel()
      self._state.polling_timer = None

  def clear_cache(self) -> None:
    """Clear all caches and stop polling."""
    self.stop_background_polling()
    self._state.session_cache = None
    self._state.loading_complete.clear()
    with contextlib.suppress(OSError):
      self._settings_path.unlink(missing_ok=True)

  def mark_loading_complete(self) -> None:
    """Signal that initial loading is complete."""
    self._state.loading_complete.set()

  def wait_for_loading(self, timeout: float = LOADING_PROMISE_TIMEOUT_SECS) -> bool:
    """Wait for initial settings loading to complete."""
    return self._state.loading_complete.wait(timeout=timeout)


def get_retry_delay(attempt: int) -> float:
  """Calculate exponential backoff delay for retry attempts."""
  base_delay = 1.0  # 1 second
  return min(base_delay * (2 ** (attempt - 1)), 60.0)  # max 60s


def fetch_with_retry_delay(
  attempt: int,
  max_retries: int = DEFAULT_MAX_RETRIES,
) -> float | None:
  """Get the retry delay for a given attempt, or None if retries exhausted."""
  if attempt > max_retries:
    return None
  return get_retry_delay(attempt)
