# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Pydantic schemas for API validation"""

from src.schemas.analytics import (
    InsightResponse,
    TimeSeriesQuery,
    TimeSeriesResponse,
    UserBehaviorResponse,
)
from src.schemas.auth import AuthUserCreate, AuthUserResponse, Token
from src.schemas.dashboard import (
    DashboardCreate,
    DashboardResponse,
    DashboardUpdate,
    WidgetCreate,
    WidgetResponse,
)
from src.schemas.event import EventCreate, EventQuery, EventResponse
from src.schemas.funnel import (
    FunnelAnalyticsResponse,
    FunnelCreate,
    FunnelResponse,
    FunnelStepCreate,
    FunnelUpdate,
)
from src.schemas.metric import AggregatedMetricResponse, MetricResponse
from src.schemas.user import UserCreate, UserResponse, UserUpdate

__all__ = [
    "AggregatedMetricResponse",
    "AuthUserCreate",
    "AuthUserResponse",
    "DashboardCreate",
    "DashboardResponse",
    "DashboardUpdate",
    "EventCreate",
    "EventQuery",
    "EventResponse",
    "FunnelAnalyticsResponse",
    "FunnelCreate",
    "FunnelResponse",
    "FunnelStepCreate",
    "FunnelUpdate",
    "InsightResponse",
    "MetricResponse",
    "TimeSeriesQuery",
    "TimeSeriesResponse",
    "Token",
    "UserBehaviorResponse",
    "UserCreate",
    "UserResponse",
    "UserUpdate",
    "WidgetCreate",
    "WidgetResponse",
]
