# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Analytics module for PostHog integration."""

from .contextual_service import ContextualAnalyticsService, RequestHeaders
from .events.business_events import business_events
from .search_analytics import (
    build_search_properties,
    track_search_completion,
)
from .service import analytics

__all__ = [
    "analytics",
    "business_events",
    "ContextualAnalyticsService",
    "RequestHeaders",
    "build_search_properties",
    "track_search_completion",
]
