"""Policy Limits Service — Organization-level policy enforcement.

Ported from Claude Code policyLimits/index.ts (664L).
Fetches organization-level policy restrictions and enforces them
within the tool gateway. Follows fail-open semantics with ETag
caching, background polling, and retry with exponential backoff.

Architecture:
  - Session cache (in-memory) → File cache (persistent) → Remote API
  - Fail-open: if fetch fails and no cache exists, policies are allowed
  - HIPAA deny-on-miss: certain policies fail closed when essential-traffic-only
  - Background polling every 60 minutes for mid-session updates
  - ETag/checksum-based 304 Not Modified optimization

Integration with Tool Gateway:
  The ClassifiedGateway checks is_policy_allowed() before executing
  tools that have organization-level restrictions (e.g. product_feedback,
  remote_sessions, file_sharing).
"""

from __future__ import annotations

import contextlib

import hashlib
import json
import logging
import os
import threading
import time
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# --- Constants ---

CACHE_FILENAME = "policy-limits.json"
FETCH_TIMEOUT_SECONDS = 10
DEFAULT_MAX_RETRIES = 5
POLLING_INTERVAL_SECONDS = 3600  # 1 hour
LOADING_TIMEOUT_SECONDS = 30

# Policies that default to denied when essential-traffic-only mode is active
# and the policy cache is unavailable. Without this, a cache miss or network
# timeout would silently re-enable these features for compliance-sensitive orgs.
ESSENTIAL_TRAFFIC_DENY_ON_MISS = frozenset({"allow_product_feedback"})


class PolicyVerdict(StrEnum):
    """Result of a policy evaluation."""

    ALLOWED = "allowed"
    DENIED = "denied"
    UNKNOWN = "unknown"  # Policy not found in restrictions


@dataclass
class PolicyRestriction:
    """Single policy restriction from the API."""

    allowed: bool
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyFetchResult:
    """Result of a policy limits fetch attempt."""

    success: bool
    restrictions: dict[str, PolicyRestriction] | None = None
    etag: str | None = None
    error: str | None = None
    skip_retry: bool = False


class PolicyLimitsService:
    """Organization-level policy enforcement with caching and polling.

    Usage:
        service = PolicyLimitsService.get_instance()
        service.load()  # Called during CLI init

        # Check if a tool action is policy-allowed
        if service.is_policy_allowed("allow_remote_sessions"):
            # proceed
        else:
            # deny with explanation
    """

    _instance: PolicyLimitsService | None = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._session_cache: dict[str, PolicyRestriction] | None = None
        self._polling_thread: threading.Timer | None = None
        self._loading_event = threading.Event()
        self._essential_traffic_only = False
        self._config_home: Path | None = None
        self._initialized = False

    @classmethod
    def get_instance(cls) -> PolicyLimitsService:
        """Singleton accessor."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_for_testing(cls) -> None:
        """Test-only reset. Clears singleton and all state."""
        with cls._lock:
            if cls._instance is not None:
                cls._instance.stop_polling()
                cls._instance._session_cache = None
                cls._instance._loading_event.clear()
            cls._instance = None

    # --- Configuration ---

    def configure(
        self,
        config_home: Path | None = None,
        essential_traffic_only: bool = False,
    ) -> None:
        """Configure the service before loading."""
        self._config_home = config_home or Path.home() / ".config" / "tool_gateway"
        self._essential_traffic_only = essential_traffic_only

    @property
    def cache_path(self) -> Path:
        """Path to the persistent policy cache file."""
        base = self._config_home or Path.home() / ".config" / "tool_gateway"
        return base / CACHE_FILENAME

    # --- Core API ---

    def is_policy_allowed(self, policy: str) -> bool:
        """Check if a specific policy is allowed.

        Returns True if the policy is unknown, unavailable, or explicitly
        allowed (fail open). Exception: policies in ESSENTIAL_TRAFFIC_DENY_ON_MISS
        fail closed when essential-traffic-only mode is active and the cache
        is unavailable.
        """
        restrictions = self._get_restrictions_from_cache()
        if restrictions is None:
            return not (
                self._essential_traffic_only and policy in ESSENTIAL_TRAFFIC_DENY_ON_MISS
            )

        restriction = restrictions.get(policy)
        if restriction is None:
            return True  # unknown policy = allowed

        return restriction.allowed

    def get_policy_verdict(self, policy: str) -> PolicyVerdict:
        """Get a structured verdict for a policy."""
        restrictions = self._get_restrictions_from_cache()
        if restrictions is None:
            if self._essential_traffic_only and policy in ESSENTIAL_TRAFFIC_DENY_ON_MISS:
                return PolicyVerdict.DENIED
            return PolicyVerdict.UNKNOWN

        restriction = restrictions.get(policy)
        if restriction is None:
            return PolicyVerdict.UNKNOWN

        return PolicyVerdict.ALLOWED if restriction.allowed else PolicyVerdict.DENIED

    # --- Loading & Polling ---

    def load(self) -> None:
        """Load policy limits during initialization.

        Fails open - if fetch fails, continues without restrictions.
        Also starts background polling for mid-session updates.
        """
        try:
            self._fetch_and_load()
            self._start_polling()
        finally:
            self._loading_event.set()
            self._initialized = True

    def wait_for_load(self, timeout: float = LOADING_TIMEOUT_SECONDS) -> bool:
        """Wait for initial policy limits loading to complete.

        Returns True if loading completed within timeout.
        """
        return self._loading_event.wait(timeout=timeout)

    def refresh(self) -> None:
        """Refresh policy limits after auth state changes."""
        self.clear_cache()
        self._fetch_and_load()
        logger.debug("Policy limits: Refreshed after auth change")

    def clear_cache(self) -> None:
        """Clear all policy limits (session + persistent) and stop polling."""
        self.stop_polling()
        self._session_cache = None
        self._loading_event.clear()
        with contextlib.suppress(OSError):
            self.cache_path.unlink(missing_ok=True)

    def stop_polling(self) -> None:
        """Stop background polling."""
        if self._polling_thread is not None:
            self._polling_thread.cancel()
            self._polling_thread = None

    # --- Internal ---

    def _get_restrictions_from_cache(self) -> dict[str, PolicyRestriction] | None:
        """Get restrictions synchronously from session cache or file."""
        if self._session_cache is not None:
            return self._session_cache

        cached = self._load_cached_restrictions()
        if cached is not None:
            self._session_cache = cached
            return cached

        return None

    def _fetch_and_load(self) -> dict[str, PolicyRestriction] | None:
        """Fetch and load policy limits with file caching.

        Fails open - returns None if fetch fails and no cache exists.
        """
        cached_restrictions = self._load_cached_restrictions()
        cached_checksum = self._compute_checksum(cached_restrictions) if cached_restrictions else None

        result = self._fetch_with_retry(cached_checksum)

        if not result.success:
            if cached_restrictions:
                logger.debug("Policy limits: Using stale cache after fetch failure")
                self._session_cache = cached_restrictions
                return cached_restrictions
            return None

        # Handle 304 Not Modified
        if result.restrictions is None and cached_restrictions:
            logger.debug("Policy limits: Cache still valid (304 Not Modified)")
            self._session_cache = cached_restrictions
            return cached_restrictions

        new_restrictions = result.restrictions or {}
        has_content = len(new_restrictions) > 0

        if has_content:
            self._session_cache = new_restrictions
            self._save_cached_restrictions(new_restrictions)
            logger.debug("Policy limits: Applied new restrictions successfully")
            return new_restrictions

        # Empty restrictions — delete cached file
        self._session_cache = new_restrictions
        try:
            self.cache_path.unlink(missing_ok=True)
            logger.debug("Policy limits: Deleted cached file (empty response)")
        except OSError:
            pass
        return new_restrictions

    def _fetch_with_retry(self, cached_checksum: str | None = None) -> PolicyFetchResult:
        """Fetch policy limits with retry logic and exponential backoff."""
        last_result: PolicyFetchResult | None = None

        for attempt in range(1, DEFAULT_MAX_RETRIES + 2):
            last_result = self._fetch_policy_limits(cached_checksum)

            if last_result.success:
                return last_result

            if last_result.skip_retry:
                return last_result

            if attempt > DEFAULT_MAX_RETRIES:
                return last_result

            delay = self._get_retry_delay(attempt)
            logger.debug(
                "Policy limits: Retry %d/%d after %.1fs",
                attempt,
                DEFAULT_MAX_RETRIES,
                delay,
            )
            time.sleep(delay)

        return last_result  # type: ignore[return-value]

    def _fetch_policy_limits(self, cached_checksum: str | None = None) -> PolicyFetchResult:
        """Fetch policy limits (single attempt, no retries).

        In the sovereign stack, this reads from a local config file
        rather than calling Anthropic's API. The pattern is preserved
        for future integration with a remote policy server.
        """
        try:
            # Sovereign mode: read from local policy file if it exists
            policy_file = self._config_home
            if policy_file is None:
                policy_file = Path.home() / ".config" / "tool_gateway"
            policy_file = policy_file / "org_policies.json"

            if not policy_file.exists():
                return PolicyFetchResult(
                    success=True,
                    restrictions={},
                )

            content = policy_file.read_text(encoding="utf-8")
            data = json.loads(content)

            # Validate structure
            restrictions: dict[str, PolicyRestriction] = {}
            raw_restrictions = data.get("restrictions", {})
            for key, value in raw_restrictions.items():
                if isinstance(value, dict):
                    restrictions[key] = PolicyRestriction(
                        allowed=value.get("allowed", True),
                        reason=value.get("reason", ""),
                        metadata=value.get("metadata", {}),
                    )

            # Check ETag
            new_checksum = self._compute_checksum(restrictions)
            if cached_checksum and new_checksum == cached_checksum:
                return PolicyFetchResult(
                    success=True,
                    restrictions=None,  # Signal cache is valid
                    etag=cached_checksum,
                )

            return PolicyFetchResult(
                success=True,
                restrictions=restrictions,
            )

        except json.JSONDecodeError as e:
            return PolicyFetchResult(
                success=False,
                error=f"Invalid policy limits format: {e}",
            )
        except OSError as e:
            return PolicyFetchResult(
                success=False,
                error=f"Cannot read policy file: {e}",
            )

    def _load_cached_restrictions(self) -> dict[str, PolicyRestriction] | None:
        """Load restrictions from cache file."""
        try:
            content = self.cache_path.read_text(encoding="utf-8")
            data = json.loads(content)
            restrictions: dict[str, PolicyRestriction] = {}
            for key, value in data.get("restrictions", {}).items():
                if isinstance(value, dict):
                    restrictions[key] = PolicyRestriction(
                        allowed=value.get("allowed", True),
                        reason=value.get("reason", ""),
                        metadata=value.get("metadata", {}),
                    )
            return restrictions
        except (OSError, json.JSONDecodeError, KeyError):
            return None

    def _save_cached_restrictions(self, restrictions: dict[str, PolicyRestriction]) -> None:
        """Save restrictions to cache file."""
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "restrictions": {
                    key: {
                        "allowed": r.allowed,
                        "reason": r.reason,
                        "metadata": r.metadata,
                    }
                    for key, r in restrictions.items()
                }
            }
            self.cache_path.write_text(
                json.dumps(data, indent=2, sort_keys=True),
                encoding="utf-8",
            )
            # Set restrictive permissions (0o600)
            os.chmod(self.cache_path, 0o600)
            logger.debug("Policy limits: Saved to %s", self.cache_path)
        except OSError as e:
            logger.debug("Policy limits: Failed to save — %s", e)

    def _start_polling(self) -> None:
        """Start background polling for policy limits."""
        if self._polling_thread is not None:
            return

        def _poll() -> None:
            previous_cache = (
                json.dumps(
                    {k: r.allowed for k, r in self._session_cache.items()},
                    sort_keys=True,
                )
                if self._session_cache
                else None
            )

            try:
                self._fetch_and_load()
                new_cache = (
                    json.dumps(
                        {k: r.allowed for k, r in self._session_cache.items()},
                        sort_keys=True,
                    )
                    if self._session_cache
                    else None
                )
                if new_cache != previous_cache:
                    logger.info("Policy limits: Changed during background poll")
            except Exception:
                pass  # Don't fail closed for background polling

            # Schedule next poll
            self._polling_thread = threading.Timer(POLLING_INTERVAL_SECONDS, _poll)
            self._polling_thread.daemon = True
            self._polling_thread.start()

        self._polling_thread = threading.Timer(POLLING_INTERVAL_SECONDS, _poll)
        self._polling_thread.daemon = True
        self._polling_thread.start()

    @staticmethod
    def _compute_checksum(
        restrictions: dict[str, PolicyRestriction] | None,
    ) -> str | None:
        """Compute a checksum from restrictions for caching."""
        if restrictions is None:
            return None
        sorted_data = json.dumps(
            {k: {"allowed": r.allowed, "reason": r.reason} for k, r in sorted(restrictions.items())},
            sort_keys=True,
        )
        digest = hashlib.sha256(sorted_data.encode()).hexdigest()
        return f"sha256:{digest}"

    @staticmethod
    def _get_retry_delay(attempt: int) -> float:
        """Exponential backoff delay for retries."""
        base = min(2**attempt, 60)
        # Add jitter (±25%)
        import random

        jitter = base * 0.25 * (2 * random.random() - 1)
        return base + jitter
