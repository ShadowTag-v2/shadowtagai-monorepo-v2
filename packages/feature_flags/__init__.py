# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Feature flags package — GrowthBook-compatible feature gating.

Modules:
    catalog:          All 119 feature flags + categories + hardcoded overrides
    growthbook_cache: TTL-based remote config cache

Primary API:
    is_flag_enabled(flag, default=False) → bool
    get_flag_value(flag, default=None)   → raw value
    flag_summary()                       → all flags with effective values
"""

from packages.feature_flags.catalog import (
  FLAG_CATEGORIES,
  HARDCODED_OVERRIDES,
  FlagCatalog,
  FlagCategory,
  flag_summary,
  get_flag_value,
  is_flag_enabled,
)
from packages.feature_flags.growthbook_cache import GrowthBookRemoteCache

__all__ = [
  "FLAG_CATEGORIES",
  "HARDCODED_OVERRIDES",
  "FlagCatalog",
  "FlagCategory",
  "GrowthBookRemoteCache",
  "flag_summary",
  "get_flag_value",
  "is_flag_enabled",
]
