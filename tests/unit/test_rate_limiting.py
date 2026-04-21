# tests/unit/test_rate_limiting.py
"""Tests for attestation rate limiting (#9).

Validates the sliding window rate limiter on the Kovel attestation endpoint.
"""

from __future__ import annotations

import time
from unittest.mock import patch

import pytest


def _get_rate_limiter():
    """Import the rate limiter from the attestation module."""
    try:
        from apps.counselconduit.api.kovel_attestation import (
            _check_rate_limit,
            _rate_windows,
            _RATE_LIMIT_MAX,
            _RATE_LIMIT_WINDOW,
        )
    except ImportError:
        from api.kovel_attestation import (  # type: ignore[no-redef]
            _check_rate_limit,
            _rate_windows,
            _RATE_LIMIT_MAX,
            _RATE_LIMIT_WINDOW,
        )
    return _check_rate_limit, _rate_windows, _RATE_LIMIT_MAX, _RATE_LIMIT_WINDOW


class TestRateLimiting:
    """Tests for the per-firm sliding window rate limiter."""

    def setup_method(self):
        """Reset rate limiter state before each test."""
        _check_rate_limit, rate_windows, _, _ = _get_rate_limiter()
        rate_windows.clear()

    def test_allows_first_request(self):
        """First request should always pass."""
        _check_rate_limit, _, _, _ = _get_rate_limiter()
        assert _check_rate_limit("firm_001") is True

    def test_allows_up_to_max_requests(self):
        """Should allow exactly MAX requests within the window."""
        _check_rate_limit, _, max_requests, _ = _get_rate_limiter()
        for i in range(max_requests):
            assert _check_rate_limit("firm_002") is True, f"Request {i+1} should pass"

    def test_blocks_after_max_requests(self):
        """Should block after MAX requests within the window."""
        _check_rate_limit, _, max_requests, _ = _get_rate_limiter()
        # Fill up the window
        for _ in range(max_requests):
            _check_rate_limit("firm_003")
        # Next request should be blocked
        assert _check_rate_limit("firm_003") is False

    def test_different_firms_independent(self):
        """Rate limits should be independent per firm."""
        _check_rate_limit, _, max_requests, _ = _get_rate_limiter()
        # Fill firm_004 to max
        for _ in range(max_requests):
            _check_rate_limit("firm_004")
        # firm_005 should still work
        assert _check_rate_limit("firm_005") is True

    def test_window_expires_and_allows_again(self):
        """After window expires, requests should be allowed again."""
        _check_rate_limit, rate_windows, max_requests, window = _get_rate_limiter()
        # Fill up the window
        for _ in range(max_requests):
            _check_rate_limit("firm_006")
        assert _check_rate_limit("firm_006") is False
        # Manually expire all entries
        expired_time = time.monotonic() - window - 1
        rate_windows["firm_006"] = [expired_time] * max_requests
        assert _check_rate_limit("firm_006") is True

    def test_sliding_window_partial_expiry(self):
        """Partially expired entries should free up slots."""
        _check_rate_limit, rate_windows, max_requests, window = _get_rate_limiter()
        now = time.monotonic()
        # Add some expired and some fresh entries
        expired = [now - window - 1] * (max_requests - 2)
        fresh = [now] * 2
        rate_windows["firm_007"] = expired + fresh
        # Should allow since expired entries are purged
        assert _check_rate_limit("firm_007") is True

    def test_returns_bool(self):
        """Rate limiter should return bool, not truthy/falsy."""
        _check_rate_limit, _, _, _ = _get_rate_limiter()
        result = _check_rate_limit("firm_008")
        assert isinstance(result, bool)
