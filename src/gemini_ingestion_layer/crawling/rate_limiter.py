# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Rate Limiter Implementation

Implements token bucket algorithm for ethical rate limiting across domains.
Aligned with PNKLN Core Stack 2025 best practices.
"""

import time
import asyncio
from typing import Dict, Optional
from dataclasses import dataclass, field


@dataclass
class TokenBucket:
    """Token bucket for rate limiting"""

    capacity: int  # Maximum tokens
    refill_rate: float  # Tokens per second
    tokens: float = field(init=False)
    last_refill: float = field(init=False, default_factory=time.time)

    def __post_init__(self):
        self.tokens = float(self.capacity)

    def _refill(self) -> None:
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill
        refill_amount = elapsed * self.refill_rate

        self.tokens = min(self.capacity, self.tokens + refill_amount)
        self.last_refill = now

    def consume(self, tokens: int = 1) -> bool:
        """
        Attempt to consume tokens.

        Returns:
            True if tokens were consumed, False if insufficient tokens
        """
        self._refill()

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    async def wait_for_token(self, tokens: int = 1) -> None:
        """Wait until tokens are available"""
        while not self.consume(tokens):
            # Calculate wait time
            tokens_needed = tokens - self.tokens
            wait_seconds = tokens_needed / self.refill_rate
            await asyncio.sleep(min(wait_seconds, 1.0))  # Check at least every second


class RateLimiter:
    """
    Global rate limiter for the ingestion layer.

    Implements per-minute rate limiting with configurable limits.
    Default: 60 requests per minute (1 req/sec)
    """

    def __init__(self, requests_per_minute: int = 60):
        """
        Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests allowed per minute
        """
        self.requests_per_minute = requests_per_minute
        self.requests_per_second = requests_per_minute / 60.0

        self.bucket = TokenBucket(capacity=requests_per_minute, refill_rate=self.requests_per_second)

        # Statistics
        self.total_requests = 0
        self.total_waits = 0
        self.total_wait_time = 0.0

    async def acquire(self, tokens: int = 1) -> None:
        """
        Acquire permission to make a request.

        Args:
            tokens: Number of tokens to consume (default 1)
        """
        if not self.bucket.consume(tokens):
            self.total_waits += 1
            wait_start = time.time()
            await self.bucket.wait_for_token(tokens)
            self.total_wait_time += time.time() - wait_start

        self.total_requests += 1

    def get_stats(self) -> dict:
        """Get rate limiter statistics"""
        return {
            "total_requests": self.total_requests,
            "total_waits": self.total_waits,
            "total_wait_time_seconds": round(self.total_wait_time, 2),
            "average_wait_time_seconds": (round(self.total_wait_time / self.total_waits, 3) if self.total_waits > 0 else 0.0),
            "current_tokens": round(self.bucket.tokens, 2),
            "requests_per_minute": self.requests_per_minute,
        }


class DomainRateLimiter:
    """
    Per-domain rate limiting for ethical crawling.

    Maintains separate rate limits for each domain to avoid
    overwhelming any single source.
    """

    def __init__(self, default_rpm: int = 60):
        """
        Initialize domain-specific rate limiter.

        Args:
            default_rpm: Default requests per minute for unknown domains
        """
        self.default_rpm = default_rpm
        self.limiters: dict[str, RateLimiter] = {}
        self.domain_configs: dict[str, int] = {}

    def configure_domain(self, domain: str, requests_per_minute: int) -> None:
        """
        Configure custom rate limit for a specific domain.

        Args:
            domain: Domain name (e.g., 'example.com')
            requests_per_minute: Custom RPM limit for this domain
        """
        self.domain_configs[domain] = requests_per_minute

        # Update existing limiter if present
        if domain in self.limiters:
            self.limiters[domain] = RateLimiter(requests_per_minute)

    def _get_limiter(self, domain: str) -> RateLimiter:
        """Get or create rate limiter for domain"""
        if domain not in self.limiters:
            rpm = self.domain_configs.get(domain, self.default_rpm)
            self.limiters[domain] = RateLimiter(rpm)

        return self.limiters[domain]

    async def acquire(self, domain: str, tokens: int = 1) -> None:
        """
        Acquire permission to make request to domain.

        Args:
            domain: Target domain
            tokens: Number of tokens to consume
        """
        limiter = self._get_limiter(domain)
        await limiter.acquire(tokens)

    def get_domain_stats(self, domain: str) -> dict | None:
        """Get statistics for a specific domain"""
        if domain in self.limiters:
            return self.limiters[domain].get_stats()
        return None

    def get_all_stats(self) -> dict[str, dict]:
        """Get statistics for all domains"""
        return {domain: limiter.get_stats() for domain, limiter in self.limiters.items()}
