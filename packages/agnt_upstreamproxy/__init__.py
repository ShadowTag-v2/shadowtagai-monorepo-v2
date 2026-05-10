"""agnt_upstreamproxy — Hardened Egress Gateway.

All outbound HTTP must pass through this gateway. URL allowlist
enforcement, circuit breaker integration, prompt dump logging.
"""

from .allowlist import EgressAllowlist
from .dump import PromptDumper
from .proxy import EgressProxy

__all__ = [
  "EgressAllowlist",
  "EgressProxy",
  "PromptDumper",
]
