"""No-op analytics — absorbs all events without network egress.

Replaces upstream Datadog/Statsig/GrowthBook analytics with local
logging only. No metrics leave the machine.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class NoOpAnalytics:
  """Analytics sink that logs locally and never phones home.

  Safe Harbor: Every method is a no-op or local-only log.
  No HTTP requests, no WebSocket connections, no UDP datagrams.
  """

  __slots__ = ("_verbose",)

  def __init__(self, *, verbose: bool = False) -> None:
    self._verbose = verbose

  def log_event(self, name: str, **properties: Any) -> None:
    """Log an analytics event locally."""
    if self._verbose:
      logger.debug("[analytics:noop] %s %s", name, properties)

  def track(self, event: str, **props: Any) -> None:
    """Track an event (no-op)."""
    self.log_event(event, **props)

  def identify(self, user_id: str, **traits: Any) -> None:
    """Identify a user (no-op)."""
    if self._verbose:
      logger.debug("[analytics:noop] identify user=%s", user_id)

  def flush(self) -> None:
    """Flush pending events (no-op — nothing to flush)."""

  def shutdown(self) -> None:
    """Shut down the analytics client (no-op)."""
    logger.debug("[analytics:noop] shutdown")
