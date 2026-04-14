"""Redis-backed Rate Limiter
Persists rate limiting state across pod restarts
"""

import time

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class RedisRateLimiter:
    """Redis-backed rate limiter for distributed systems

    Uses sliding window algorithm for accurate rate limiting
    Persists state across application restarts
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        default_limit: int = 60,
        default_window: int = 3600,  # 1 hour in seconds
    ):
        if not REDIS_AVAILABLE:
            raise ImportError("redis not installed. Run: pip install redis")

        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.default_limit = default_limit
        self.default_window = default_window

    def is_allowed(self, key: str, limit: int | None = None, window: int | None = None) -> bool:
        """Check if action is allowed under rate limit

        Args:
            key: Rate limit key (e.g., 'domain:example.com')
            limit: Maximum requests allowed in window (default: 60)
            window: Time window in seconds (default: 3600 = 1 hour)

        Returns:
            True if allowed, False if rate limit exceeded

        """
        limit = limit or self.default_limit
        window = window or self.default_window

        now = time.time()
        window_start = now - window

        # Remove old entries outside window
        self.redis_client.zremrangebyscore(key, 0, window_start)

        # Count requests in current window
        current_count = self.redis_client.zcard(key)

        if current_count >= limit:
            return False

        # Add current request with timestamp as score
        self.redis_client.zadd(key, {str(now): now})

        # Set expiry on key (cleanup)
        self.redis_client.expire(key, window * 2)

        return True

    def record_request(self, key: str):
        """Record a request (for manual rate limiting)

        Args:
            key: Rate limit key

        """
        now = time.time()
        self.redis_client.zadd(key, {str(now): now})
        self.redis_client.expire(key, self.default_window * 2)

    def get_remaining(self, key: str, limit: int | None = None, window: int | None = None) -> int:
        """Get remaining requests in current window

        Args:
            key: Rate limit key
            limit: Maximum requests allowed
            window: Time window in seconds

        Returns:
            Number of remaining requests

        """
        limit = limit or self.default_limit
        window = window or self.default_window

        now = time.time()
        window_start = now - window

        # Remove old entries
        self.redis_client.zremrangebyscore(key, 0, window_start)

        current_count = self.redis_client.zcard(key)
        return max(0, limit - current_count)

    def reset(self, key: str):
        """Reset rate limit for a key

        Args:
            key: Rate limit key to reset

        """
        self.redis_client.delete(key)


class InMemoryRateLimiter:
    """Fallback in-memory rate limiter (for development/testing)

    WARNING: Does not persist across restarts
    Use RedisRateLimiter for production
    """

    def __init__(self, default_limit: int = 60, default_window: int = 3600):
        self.default_limit = default_limit
        self.default_window = default_window
        self.requests: dict[str, list[float]] = {}

    def is_allowed(self, key: str, limit: int | None = None, window: int | None = None) -> bool:
        """Check if action is allowed"""
        limit = limit or self.default_limit
        window = window or self.default_window

        now = time.time()
        window_start = now - window

        # Initialize key if not exists
        if key not in self.requests:
            self.requests[key] = []

        # Remove old entries
        self.requests[key] = [t for t in self.requests[key] if t > window_start]

        if len(self.requests[key]) >= limit:
            return False

        self.requests[key].append(now)
        return True

    def record_request(self, key: str):
        """Record a request"""
        now = time.time()
        if key not in self.requests:
            self.requests[key] = []
        self.requests[key].append(now)

    def get_remaining(self, key: str, limit: int | None = None, window: int | None = None) -> int:
        """Get remaining requests"""
        limit = limit or self.default_limit
        window = window or self.default_window

        now = time.time()
        window_start = now - window

        if key not in self.requests:
            return limit

        # Remove old entries
        self.requests[key] = [t for t in self.requests[key] if t > window_start]

        return max(0, limit - len(self.requests[key]))

    def reset(self, key: str):
        """Reset rate limit"""
        self.requests.pop(key, None)
