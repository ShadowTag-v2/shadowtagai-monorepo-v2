# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Feature Flags Service for managing feature toggles.
"""

import hashlib
from typing import Any
from datetime import datetime, timezone

import redis.asyncio as redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logger import logger
from app.models.release import FeatureFlag, FeatureFlagStatus
from app.schemas.release import FeatureFlagCreate, FeatureFlagUpdate


class FeatureFlagService:
  """Service for managing feature flags with Redis caching."""

  def __init__(self):
    """Initialize feature flag service."""
    self.redis_client: redis.Redis | None = None
    self.cache_ttl = settings.FEATURE_FLAGS_CACHE_TTL

  async def init_redis(self) -> None:
    """Initialize Redis connection."""
    try:
      self.redis_client = redis.from_url(
        settings.REDIS_URL,
        db=settings.REDIS_FEATURE_FLAGS_DB,
        encoding="utf-8",
        decode_responses=True,
      )
      await self.redis_client.ping()
      logger.info("Redis connection established for feature flags")
    except Exception as e:
      logger.error(f"Failed to connect to Redis: {e}")
      self.redis_client = None

  async def close_redis(self) -> None:
    """Close Redis connection."""
    if self.redis_client:
      await self.redis_client.close()

  def _cache_key(self, flag_key: str, user_id: str | None = None) -> str:
    """Generate cache key for feature flag."""
    if user_id:
      return f"feature_flag:{flag_key}:{user_id}"
    return f"feature_flag:{flag_key}"

  async def _get_from_cache(self, cache_key: str) -> bool | None:
    """Get feature flag value from cache."""
    if not self.redis_client:
      return None

    try:
      value = await self.redis_client.get(cache_key)
      if value is not None:
        return value.lower() == "true"
    except Exception as e:
      logger.warning(f"Cache read error: {e}")

    return None

  async def _set_cache(self, cache_key: str, value: bool) -> None:
    """Set feature flag value in cache."""
    if not self.redis_client:
      return

    try:
      await self.redis_client.setex(
        cache_key,
        self.cache_ttl,
        "true" if value else "false",
      )
    except Exception as e:
      logger.warning(f"Cache write error: {e}")

  async def _invalidate_cache(self, flag_key: str) -> None:
    """Invalidate cache for a feature flag."""
    if not self.redis_client:
      return

    try:
      # Delete all cache keys for this flag
      pattern = f"feature_flag:{flag_key}:*"
      async for key in self.redis_client.scan_iter(match=pattern):
        await self.redis_client.delete(key)

      # Delete the base key
      await self.redis_client.delete(f"feature_flag:{flag_key}")
    except Exception as e:
      logger.warning(f"Cache invalidation error: {e}")

  def _calculate_user_bucket(self, flag_key: str, user_id: str) -> int:
    """
    Calculate user bucket for percentage rollout.

    Returns a value between 0-99 for consistent bucketing.
    """
    hash_input = f"{flag_key}:{user_id}"
    hash_value = hashlib.md5(hash_input.encode()).hexdigest()
    return int(hash_value[:8], 16) % 100

  def _evaluate_targeting_rules(
    self,
    targeting_rules: dict[str, Any] | None,
    context: dict[str, Any] | None,
  ) -> bool:
    """
    Evaluate targeting rules against context.

    Targeting rules can include:
    - user_ids: List of specific user IDs
    - user_groups: List of user groups
    - attributes: Key-value pairs to match
    """
    if not targeting_rules or not context:
      return True

    # Check user ID targeting
    if "user_ids" in targeting_rules:
      user_id = context.get("user_id")
      if user_id and user_id in targeting_rules["user_ids"]:
        return True

    # Check user group targeting
    if "user_groups" in targeting_rules:
      user_groups = context.get("user_groups", [])
      if any(group in targeting_rules["user_groups"] for group in user_groups):
        return True

    # Check attribute matching
    if "attributes" in targeting_rules:
      for key, value in targeting_rules["attributes"].items():
        if context.get(key) != value:
          return False
      return True

    return False

  async def create_flag(
    self,
    db: AsyncSession,
    flag_data: FeatureFlagCreate,
  ) -> FeatureFlag:
    """Create a new feature flag."""
    flag = FeatureFlag(**flag_data.model_dump())
    db.add(flag)
    await db.commit()
    await db.refresh(flag)

    logger.info(f"Created feature flag: {flag.key}")
    return flag

  async def get_flag(
    self,
    db: AsyncSession,
    flag_key: str,
  ) -> FeatureFlag | None:
    """Get feature flag by key."""
    result = await db.execute(select(FeatureFlag).where(FeatureFlag.key == flag_key))
    return result.scalar_one_or_none()

  async def list_flags(
    self,
    db: AsyncSession,
    environment: str | None = None,
    enabled: bool | None = None,
    skip: int = 0,
    limit: int = 100,
  ) -> tuple[list[FeatureFlag], int]:
    """List feature flags with optional filters."""
    query = select(FeatureFlag)

    if environment:
      query = query.where(FeatureFlag.environment == environment)
    if enabled is not None:
      query = query.where(FeatureFlag.enabled == enabled)

    # Get total count
    count_result = await db.execute(
      select(FeatureFlag).where(*query.whereclause.clauses if query.whereclause else [])
    )
    total = len(count_result.all())

    # Get paginated results
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    flags = result.scalars().all()

    return list(flags), total

  async def update_flag(
    self,
    db: AsyncSession,
    flag_key: str,
    flag_data: FeatureFlagUpdate,
  ) -> FeatureFlag | None:
    """Update feature flag."""
    flag = await self.get_flag(db, flag_key)
    if not flag:
      return None

    update_data = flag_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
      setattr(flag, field, value)

    flag.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(flag)

    # Invalidate cache
    await self._invalidate_cache(flag_key)

    logger.info(f"Updated feature flag: {flag_key}")
    return flag

  async def delete_flag(
    self,
    db: AsyncSession,
    flag_key: str,
  ) -> bool:
    """Delete feature flag."""
    flag = await self.get_flag(db, flag_key)
    if not flag:
      return False

    await db.delete(flag)
    await db.commit()

    # Invalidate cache
    await self._invalidate_cache(flag_key)

    logger.info(f"Deleted feature flag: {flag_key}")
    return True

  async def is_enabled(
    self,
    db: AsyncSession,
    flag_key: str,
    user_id: str | None = None,
    context: dict[str, Any] | None = None,
  ) -> bool:
    """
    Check if feature flag is enabled for a user.

    Args:
        db: Database session
        flag_key: Feature flag key
        user_id: User ID for percentage rollout
        context: Additional context for targeting rules

    Returns:
        True if feature is enabled, False otherwise
    """
    # Check cache first
    cache_key = self._cache_key(flag_key, user_id)
    cached_value = await self._get_from_cache(cache_key)
    if cached_value is not None:
      return cached_value

    # Get flag from database
    flag = await self.get_flag(db, flag_key)
    if not flag:
      logger.warning(f"Feature flag not found: {flag_key}")
      return False

    # Check if flag is globally disabled
    if not flag.enabled:
      await self._set_cache(cache_key, False)
      return False

    # Check status-based enabling
    if flag.status == FeatureFlagStatus.ENABLED:
      await self._set_cache(cache_key, True)
      return True

    # Check targeting rules
    if flag.targeting_rules and context:
      if self._evaluate_targeting_rules(flag.targeting_rules, context):
        await self._set_cache(cache_key, True)
        return True

    # Check percentage rollout
    if flag.status == FeatureFlagStatus.PERCENTAGE and user_id:
      bucket = self._calculate_user_bucket(flag_key, user_id)
      enabled = bucket < flag.percentage
      await self._set_cache(cache_key, enabled)
      return enabled

    await self._set_cache(cache_key, False)
    return False

  async def enable_flag(
    self,
    db: AsyncSession,
    flag_key: str,
    percentage: int | None = None,
  ) -> FeatureFlag | None:
    """Enable a feature flag, optionally with percentage rollout."""
    flag = await self.get_flag(db, flag_key)
    if not flag:
      return None

    flag.enabled = True
    if percentage is not None:
      flag.status = FeatureFlagStatus.PERCENTAGE
      flag.percentage = min(max(percentage, 0), 100)
    else:
      flag.status = FeatureFlagStatus.ENABLED
      flag.percentage = 100

    flag.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(flag)

    # Invalidate cache
    await self._invalidate_cache(flag_key)

    logger.info(f"Enabled feature flag: {flag_key} (percentage: {flag.percentage})")
    return flag

  async def disable_flag(
    self,
    db: AsyncSession,
    flag_key: str,
  ) -> FeatureFlag | None:
    """Disable a feature flag."""
    flag = await self.get_flag(db, flag_key)
    if not flag:
      return None

    flag.enabled = False
    flag.status = FeatureFlagStatus.DISABLED
    flag.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(flag)

    # Invalidate cache
    await self._invalidate_cache(flag_key)

    logger.info(f"Disabled feature flag: {flag_key}")
    return flag


# Global feature flag service instance
feature_flag_service = FeatureFlagService()
