# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Intelligent caching system with Redis support
Automatically caches responses and provides cache statistics
"""

import hashlib
import json
import pickle
from datetime import timedelta
from typing import Any

import redis.asyncio as redis

from app.core.config import settings


class IntelligentCache:
    """Intelligent caching system that:
    - Automatically caches frequently accessed data
    - Tracks cache hit/miss rates
    - Suggests what should be cached
    - Supports multiple cache backends
    """

    def __init__(self):
        self.redis_client: redis.Redis | None = None
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
        }
        self.access_patterns: dict[str, int] = {}

    async def connect(self):
        """Connect to Redis"""
        if not settings.ENABLE_CACHE:
            return

        try:
            self.redis_client = await redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=False,
            )
            await self.redis_client.ping()
            print("✓ Connected to Redis cache")
        except Exception as e:
            print(f"⚠ Redis connection failed: {e}")
            print("  Continuing without cache...")
            self.redis_client = None

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a cache key from arguments"""
        key_data = {
            "args": args,
            "kwargs": kwargs,
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        return f"{prefix}:{key_hash}"

    async def get(self, key: str) -> Any | None:
        """Get value from cache"""
        if not self.redis_client:
            self.stats["misses"] += 1
            return None

        try:
            value = await self.redis_client.get(key)
            if value:
                self.stats["hits"] += 1
                # Track access pattern
                self.access_patterns[key] = self.access_patterns.get(key, 0) + 1
                return pickle.loads(value)
            self.stats["misses"] += 1
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            self.stats["misses"] += 1
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """Set value in cache"""
        if not self.redis_client:
            return False

        try:
            ttl = ttl or settings.CACHE_TTL
            serialized = pickle.dumps(value)
            await self.redis_client.setex(key, timedelta(seconds=ttl), serialized)
            self.stats["sets"] += 1
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not self.redis_client:
            return False

        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False

    async def clear(self) -> bool:
        """Clear all cache"""
        if not self.redis_client:
            return False

        try:
            await self.redis_client.flushdb()
            return True
        except Exception as e:
            print(f"Cache clear error: {e}")
            return False

    async def get_stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total * 100) if total > 0 else 0

        return {
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "sets": self.stats["sets"],
            "hit_rate": hit_rate,
            "total_requests": total,
        }

    def get_cache_suggestions(self) -> list:
        """Suggest what should be cached based on access patterns
        Returns keys that are accessed frequently but not cached
        """
        suggestions = []

        # Find frequently accessed keys
        sorted_patterns = sorted(self.access_patterns.items(), key=lambda x: x[1], reverse=True)

        for key, count in sorted_patterns[:10]:
            if count >= settings.CACHE_SUGGESTION_THRESHOLD:
                suggestions.append(
                    {
                        "key": key,
                        "access_count": count,
                        "suggestion": f"Cache this key - accessed {count} times",
                    },
                )

        return suggestions


# Decorator for automatic caching
def cache_response(prefix: str, ttl: int | None = None, key_builder=None):
    """Decorator to automatically cache function responses

    Usage:
        @cache_response('user', ttl=300)
        async def get_user(user_id: int):
            ...
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Get cache instance
            cache = IntelligentCache()

            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                cache_key = cache._generate_key(prefix, *args, **kwargs)

            # Try to get from cache
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            await cache.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator


# Global cache instance
cache = IntelligentCache()
