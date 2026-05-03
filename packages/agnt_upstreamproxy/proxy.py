"""Egress proxy — hardened outbound HTTP gateway.

All outbound HTTP requests MUST go through this proxy. Enforces:
1. URL allowlist (via EgressAllowlist)
2. Circuit breaker (via packages/circuit_breaker)
3. Prompt dumping (via PromptDumper)

Safe Harbor constraint: fail-closed. If the circuit breaker for a host
is OPEN, the request is rejected before any network I/O occurs.
"""

from __future__ import annotations

import logging
from urllib.parse import urlparse

from circuit_breaker import CircuitBreakerOpenError, CircuitBreakerRegistry

from .allowlist import EgressAllowlist
from .dump import PromptDumper

logger = logging.getLogger(__name__)


class EgressProxy:
    """Hardened HTTP egress gateway.

    All outbound requests must use proxy.request() instead of
    raw httpx/requests/urllib calls. This enforces the allowlist,
    integrates per-host circuit breakers, and dumps prompts when enabled.
    """

    __slots__ = ("_allowlist", "_dumper", "_registry")

    def __init__(
        self,
        allowlist: EgressAllowlist | None = None,
        dumper: PromptDumper | None = None,
        registry: CircuitBreakerRegistry | None = None,
    ) -> None:
        self._allowlist = allowlist or EgressAllowlist()
        self._dumper = dumper or PromptDumper()
        self._registry = registry or CircuitBreakerRegistry()

    @property
    def registry(self) -> CircuitBreakerRegistry:
        """Access the underlying circuit breaker registry."""
        return self._registry

    def _host_from_url(self, url: str) -> str:
        """Extract hostname for per-host circuit breaker lookup."""
        try:
            return urlparse(url).hostname or "unknown"
        except Exception:
            return "unknown"

    def check_allowed(self, url: str) -> bool:
        """Check if the URL is on the allowlist."""
        return self._allowlist.is_allowed(url)

    def pre_request(self, url: str, payload: dict | None = None) -> None:
        """Pre-request hook: validate allowlist, check circuit breaker, dump payload.

        Raises:
            PermissionError: URL not in allowlist.
            CircuitBreakerOpenError: Host circuit breaker is OPEN.
        """
        if not self._allowlist.is_allowed(url):
            msg = f"Egress blocked: {url} not in allowlist"
            raise PermissionError(msg)

        # Fail-closed: reject if circuit breaker is OPEN for this host
        host = self._host_from_url(url)
        breaker = self._registry.get_or_create(host)
        if not breaker.allow_request():
            raise CircuitBreakerOpenError(
                service_name=host,
                failure_count=breaker.consecutive_failures,
                seconds_until_probe=breaker.seconds_until_probe,
            )

        if payload and self._dumper.enabled:
            self._dumper.dump(url, payload)

    def post_request(self, url: str, status: int, success: bool) -> None:
        """Post-request hook: update circuit breaker state."""
        host = self._host_from_url(url)
        breaker = self._registry.get_or_create(host)
        try:
            if success:
                breaker.record_success()
            else:
                breaker.record_failure()
        except Exception:
            logger.debug("Circuit breaker update failed for %s", host)

    def health_report(self) -> dict:
        """Return circuit breaker health across all hosts."""
        return self._registry.health_report()

    def close(self) -> None:
        """Clean up resources."""
        self._dumper.close()
