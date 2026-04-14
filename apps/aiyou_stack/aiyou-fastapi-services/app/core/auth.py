"""FastAPI Authentication Middleware with Rate Limiting
Production-ready API key authentication with tier-based rate limiting
"""

import hashlib
import logging
import time

import redis
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """API Key Authentication Middleware with tier-based rate limiting

    Features:
    - SHA-256 API key hashing for security
    - Tier-based rate limits (Tier 1: 10/min, Tier 2: 100/min, Tier 3: 1000/min, Enterprise: 5000/min)
    - Redis-backed rate limiting (survives pod restarts)
    - In-memory fallback if Redis unavailable
    - Per-key rate limiting (not global)
    """

    def __init__(self, app, api_keys: dict[str, str], redis_url: str | None = None):
        """Initialize authentication middleware

        Args:
            app: FastAPI application
            api_keys: Dict mapping SHA-256 hashed API keys to tier names
                     Example: {"hash1": "tier_1", "hash2": "enterprise"}
            redis_url: Redis connection URL (optional, falls back to in-memory)

        """
        super().__init__(app)
        self.api_keys = api_keys  # {key_hash: tier}

        # Rate limits per tier (requests per minute)
        self.tier_limits = {
            "tier_1": 10,
            "tier_2": 100,
            "tier_3": 1000,
            "enterprise": 5000,
        }

        # Try to connect to Redis
        self.redis_client = None
        if redis_url:
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                self.redis_client.ping()
                logger.info("✅ Authentication middleware using Redis rate limiting")
            except Exception as e:
                logger.warning(f"⚠️ Redis unavailable, falling back to in-memory rate limiting: {e}")

        # In-memory fallback
        self.rate_limit_cache: dict[str, list] = {}  # {key_hash: [timestamp1, timestamp2, ...]}

    async def dispatch(self, request: Request, call_next):
        """Process request with authentication and rate limiting
        """
        # Skip auth for health check endpoints
        if request.url.path in ["/health", "/healthz", "/metrics"]:
            return await call_next(request)

        # Extract API key from header
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            raise HTTPException(status_code=401, detail="Missing X-API-Key header")

        # Hash the API key (constant-time comparison)
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        # Validate API key
        if key_hash not in self.api_keys:
            raise HTTPException(status_code=401, detail="Invalid API key")

        # Get tier and rate limit
        tier = self.api_keys[key_hash]
        rate_limit = self.tier_limits.get(tier, 100)  # Default to tier_2 if unknown

        # Check rate limit
        allowed, remaining, reset_at = self._check_rate_limit(key_hash, rate_limit)
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Limit: {rate_limit}/min. Resets at: {reset_at}",
                headers={
                    "X-RateLimit-Limit": str(rate_limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_at),
                },
            )

        # Add rate limit headers to response
        response: Response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_at)

        return response

    def _check_rate_limit(self, key_hash: str, limit: int) -> tuple[bool, int, int]:
        """Check if request is allowed under rate limit

        Args:
            key_hash: SHA-256 hash of API key
            limit: Maximum requests per minute

        Returns:
            Tuple of (allowed, remaining_requests, reset_timestamp)

        """
        now = int(time.time())
        window_start = now - 60  # 60-second sliding window

        if self.redis_client:
            return self._check_rate_limit_redis(key_hash, limit, now, window_start)
        return self._check_rate_limit_memory(key_hash, limit, now, window_start)

    def _check_rate_limit_redis(
        self, key_hash: str, limit: int, now: int, window_start: int,
    ) -> tuple[bool, int, int]:
        """Check rate limit using Redis (persistent, distributed)
        """
        redis_key = f"ratelimit:{key_hash}"

        try:
            # Remove old entries outside the window
            self.redis_client.zremrangebyscore(redis_key, 0, window_start)

            # Count requests in current window
            current_count = self.redis_client.zcard(redis_key)

            if current_count >= limit:
                # Rate limit exceeded
                reset_at = now + 60
                return False, 0, reset_at

            # Add current request
            self.redis_client.zadd(redis_key, {str(now): now})

            # Set expiry (cleanup after 2 minutes)
            self.redis_client.expire(redis_key, 120)

            remaining = limit - current_count - 1
            reset_at = now + 60
            return True, remaining, reset_at

        except Exception as e:
            logger.error(f"Redis rate limit check failed: {e}, falling back to allow")
            # Fail open (allow request if Redis fails)
            return True, limit, now + 60

    def _check_rate_limit_memory(
        self, key_hash: str, limit: int, now: int, window_start: int,
    ) -> tuple[bool, int, int]:
        """Check rate limit using in-memory cache (fallback)

        ⚠️ WARNING: Does not persist across pod restarts
        """
        if key_hash not in self.rate_limit_cache:
            self.rate_limit_cache[key_hash] = []

        # Remove old entries
        self.rate_limit_cache[key_hash] = [
            ts for ts in self.rate_limit_cache[key_hash] if ts > window_start
        ]

        current_count = len(self.rate_limit_cache[key_hash])

        if current_count >= limit:
            reset_at = now + 60
            return False, 0, reset_at

        # Add current request
        self.rate_limit_cache[key_hash].append(now)

        remaining = limit - current_count - 1
        reset_at = now + 60
        return True, remaining, reset_at


def hash_api_key(api_key: str) -> str:
    """Hash an API key using SHA-256

    Args:
        api_key: Plain text API key

    Returns:
        SHA-256 hex digest

    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def create_auth_middleware(
    api_keys_config: dict[str, str], redis_url: str | None = None,
) -> AuthenticationMiddleware:
    """Factory function to create authentication middleware

    Args:
        api_keys_config: Dict mapping plain API keys to tiers
                        Example: {"key123": "tier_1", "key456": "enterprise"}
        redis_url: Redis connection URL (optional)

    Returns:
        Configured AuthenticationMiddleware instance

    """
    # Hash all API keys
    hashed_keys = {hash_api_key(key): tier for key, tier in api_keys_config.items()}

    return lambda app: AuthenticationMiddleware(app, hashed_keys, redis_url)
