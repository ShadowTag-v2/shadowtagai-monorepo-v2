"""Dashboard schemas"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class WidgetCreate(BaseModel):
    """Schema for creating a dashboard widget"""

    title: str = Field(..., description="Widget title")
    description: str | None = Field(None, description="Widget description")
    widget_type: str = Field(..., description="Widget type (chart, table, metric, funnel)")
    visualization_type: str | None = Field(
        None, description="Visualization type (line, bar, pie, area)",
    )
    metric_type: str | None = Field(
        None, description="Metric type (event_count, user_count, conversion_rate)",
    )
    event_filters: dict[str, Any] | None = Field(default_factory=dict, description="Event filters")
    time_range: str | None = Field(default="7d", description="Time range (7d, 30d, 90d)")
    group_by: list[str] | None = Field(default_factory=list, description="Fields to group by")
    position: dict[str, int] | None = Field(default_factory=dict, description="Widget position")
    chart_config: dict[str, Any] | None = Field(
        default_factory=dict, description="Chart configuration",
    )
    refresh_interval_seconds: int | None = Field(
        default=300, description="Refresh interval in seconds",
    )


class WidgetResponse(BaseModel):
    """Schema for widget response"""

    id: UUID
    title: str
    description: str | None
    widget_type: str
    visualization_type: str | None
    metric_type: str | None
    event_filters: dict[str, Any]
    time_range: str | None
    group_by: list[str]
    position: dict[str, int]
    chart_config: dict[str, Any]
    refresh_interval_seconds: int
    last_refreshed: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DashboardCreate(BaseModel):
    """Schema for creating a dashboard"""

    name: str = Field(..., description="Dashboard name")
    description: str | None = Field(None, description="Dashboard description")
    is_public: bool | None = Field(default=False, description="Is dashboard public")
    layout: dict[str, Any] | None = Field(default_factory=dict, description="Layout configuration")
    tags: list[str] | None = Field(default_factory=list, description="Tags")
    widgets: list[WidgetCreate] | None = Field(
        default_factory=list, description="Dashboard widgets",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Main Analytics Dashboard",
                "description": "Overview of key metrics",
                "is_public": False,
                "widgets": [
                    {
                        "title": "Daily Active Users",
                        "widget_type": "chart",
                        "visualization_type": "line",
                        "metric_type": "user_count",
                        "time_range": "30d",
                    },
                ],
            },
        }


class DashboardUpdate(BaseModel):
    """Schema for updating a dashboard"""

    name: str | None = None
    description: str | None = None
    is_public: bool | None = None
    is_default: bool | None = None
    layout: dict[str, Any] | None = None
    tags: list[str] | None = None


class DashboardResponse(BaseModel):
    """Schema for dashboard response"""

    id: UUID
    name: str
    description: str | None
    is_public: bool
    is_default: bool
    layout: dict[str, Any]
    tags: list[str]
    widgets: list[WidgetResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
