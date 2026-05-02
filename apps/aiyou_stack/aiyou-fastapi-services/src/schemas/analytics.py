"""Analytics schemas for insights and reporting"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TimeSeriesQuery(BaseModel):
    """Schema for time series query"""

    metric: str = Field(..., description="Metric to query")
    start_date: datetime = Field(..., description="Start date")
    end_date: datetime = Field(..., description="End date")
    interval: str = Field(default="day", description="Time interval (hour, day, week, month)")
    filters: dict[str, Any] | None = Field(default_factory=dict, description="Filters")
    group_by: list[str] | None = Field(default_factory=list, description="Group by fields")


class TimeSeriesDataPoint(BaseModel):
    """Single data point in time series"""

    timestamp: datetime
    value: float
    dimensions: dict[str, Any] | None = None


class TimeSeriesResponse(BaseModel):
    """Schema for time series response"""

    metric: str
    interval: str
    start_date: datetime
    end_date: datetime
    data: list[TimeSeriesDataPoint]
    total: float
    average: float

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "metric": "user_count",
                    "interval": "day",
                    "start_date": "2025-01-01T00:00:00Z",
                    "end_date": "2025-01-07T23:59:59Z",
                    "data": [
                        {"timestamp": "2025-01-01T00:00:00Z", "value": 150},
                        {"timestamp": "2025-01-02T00:00:00Z", "value": 175},
                    ],
                    "total": 1200,
                    "average": 171.43,
                },
            ],
        },
    )


class UserBehaviorMetrics(BaseModel):
    """User behavior metrics"""

    avg_session_duration: float
    avg_events_per_session: float
    bounce_rate: float
    return_rate: float
    most_common_events: list[dict[str, Any]]
    most_visited_pages: list[dict[str, Any]]


class UserBehaviorResponse(BaseModel):
    """Schema for user behavior analysis"""

    user_id: str | None
    segment: str | None
    time_period: str
    metrics: UserBehaviorMetrics
    top_conversion_paths: list[list[str]]

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "segment": "power_users",
                    "time_period": "30d",
                    "metrics": {
                        "avg_session_duration": 325.5,
                        "avg_events_per_session": 12.3,
                        "bounce_rate": 0.25,
                        "return_rate": 0.65,
                        "most_common_events": [
                            {"event_name": "page_view", "count": 5000},
                            {"event_name": "button_click", "count": 2500},
                        ],
                        "most_visited_pages": [{"page_url": "/dashboard", "count": 3000}],
                    },
                    "top_conversion_paths": [
                        ["landing_page", "signup_form", "signup_complete"],
                        ["landing_page", "pricing_page", "signup_complete"],
                    ],
                },
            ],
        },
    )


class InsightType(BaseModel):
    """Single insight"""

    title: str
    description: str
    insight_type: str  # trend, anomaly, recommendation, correlation
    severity: str  # info, warning, critical
    data: dict[str, Any]
    recommendations: list[str] | None = None


class InsightResponse(BaseModel):
    """Schema for insights response"""

    generated_at: datetime
    time_period: str
    insights: list[InsightType]

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "generated_at": "2025-01-15T12:00:00Z",
                    "time_period": "7d",
                    "insights": [
                        {
                            "title": "Conversion Rate Increased",
                            "description": "Sign-up conversion rate increased by 25% this week",
                            "insight_type": "trend",
                            "severity": "info",
                            "data": {
                                "previous_rate": 0.20,
                                "current_rate": 0.25,
                                "change_percent": 25,
                            },
                            "recommendations": [
                                "Continue current marketing campaign",
                                "Analyze which changes contributed to the increase",
                            ],
                        },
                    ],
                },
            ],
        },
    )
