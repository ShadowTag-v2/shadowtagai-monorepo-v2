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
    "AuthUserCreate",
    "AuthUserResponse",
    "Token",
    "EventCreate",
    "EventResponse",
    "EventQuery",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "FunnelCreate",
    "FunnelUpdate",
    "FunnelResponse",
    "FunnelStepCreate",
    "FunnelAnalyticsResponse",
    "DashboardCreate",
    "DashboardUpdate",
    "DashboardResponse",
    "WidgetCreate",
    "WidgetResponse",
    "MetricResponse",
    "AggregatedMetricResponse",
    "TimeSeriesQuery",
    "TimeSeriesResponse",
    "UserBehaviorResponse",
    "InsightResponse",
]
