"""URL allowlist enforcement for egress gateway.

Only URLs matching the allowlist are permitted. Everything else
is blocked with a clear error message.
"""

from __future__ import annotations

import fnmatch
import logging
import os
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Default allowlist — Google AI APIs and Firebase only.
_DEFAULT_ALLOWLIST: frozenset[str] = frozenset(
  {
    "generativelanguage.googleapis.com",
    "*.googleapis.com",
    "firestore.googleapis.com",
    "*.firebaseio.com",
    "*.run.app",
    "secretmanager.googleapis.com",
    "oauth2.googleapis.com",
    "accounts.google.com",
  }
)


class EgressAllowlist:
  """URL allowlist for outbound HTTP requests.

  Loads patterns from AGNT_EGRESS_ALLOWLIST env var (comma-separated
  glob patterns) with sensible defaults for Google APIs.
  """

  __slots__ = ("_patterns",)

  def __init__(self) -> None:
    custom = os.environ.get("AGNT_EGRESS_ALLOWLIST", "")
    if custom:
      self._patterns = frozenset(p.strip() for p in custom.split(",") if p.strip())
    else:
      self._patterns = _DEFAULT_ALLOWLIST

  def is_allowed(self, url: str) -> bool:
    """Check if a URL is on the allowlist."""
    try:
      parsed = urlparse(url)
      host = parsed.hostname or ""
    except Exception:
      return False

    for pattern in self._patterns:
      if fnmatch.fnmatch(host, pattern):
        return True

    logger.warning("[egress] Blocked: %s (not in allowlist)", host)
    return False

  @property
  def patterns(self) -> frozenset[str]:
    """Currently active allowlist patterns."""
    return self._patterns
