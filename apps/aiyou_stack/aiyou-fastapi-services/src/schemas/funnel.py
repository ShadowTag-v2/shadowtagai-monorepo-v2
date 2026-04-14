"""Funnel schemas"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class FunnelStepCreate(BaseModel):
    """Schema for creating a funnel step"""

    step_order: int = Field(..., description="Order of the step in the funnel")
    event_name: str = Field(..., description="Event name for this step")
    event_filters: dict[str, Any] | None = Field(
        default_factory=dict, description="Filters for the event",
    )
    name: str | None = Field(None, description="Display name for the step")
    description: str | None = Field(None, description="Step description")


class FunnelStepResponse(BaseModel):
    """Schema for funnel step response"""

    id: UUID
    step_order: int
    event_name: str
    event_filters: dict[str, Any]
    name: str | None
    description: str | None

    class Config:
        from_attributes = True


class FunnelCreate(BaseModel):
    """Schema for creating a funnel"""

    name: str = Field(..., description="Funnel name")
    description: str | None = Field(None, description="Funnel description")
    time_window_hours: int = Field(
        default=24, description="Time window for completing funnel (hours)",
    )
    steps: list[FunnelStepCreate] = Field(..., description="Funnel steps")
    tags: list[str] | None = Field(default_factory=list, description="Tags for categorization")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Sign-up Funnel",
                "description": "Track user sign-up process",
                "time_window_hours": 24,
                "steps": [
                    {"step_order": 1, "event_name": "landing_page_view", "name": "Landing Page"},
                    {"step_order": 2, "event_name": "signup_form_view", "name": "Sign-up Form"},
                    {"step_order": 3, "event_name": "signup_completed", "name": "Sign-up Complete"},
                ],
                "tags": ["acquisition", "signup"],
            },
        }


class FunnelUpdate(BaseModel):
    """Schema for updating a funnel"""

    name: str | None = None
    description: str | None = None
    is_active: bool | None = None
    time_window_hours: int | None = None
    tags: list[str] | None = None


class FunnelResponse(BaseModel):
    """Schema for funnel response"""

    id: UUID
    name: str
    description: str | None
    is_active: bool
    time_window_hours: int
    tags: list[str]
    steps: list[FunnelStepResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FunnelStepAnalytics(BaseModel):
    """Analytics for a single funnel step"""

    step_order: int
    event_name: str
    name: str | None
    users_entered: int
    users_completed: int
    conversion_rate: float
    drop_off_rate: float
    avg_time_to_next_step: float | None


class FunnelAnalyticsResponse(BaseModel):
    """Schema for funnel analytics response"""

    funnel_id: UUID
    funnel_name: str
    total_users_entered: int
    total_users_completed: int
    overall_conversion_rate: float
    avg_completion_time: float | None
    steps: list[FunnelStepAnalytics]
    start_date: datetime
    end_date: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "funnel_id": "123e4567-e89b-12d3-a456-426614174000",
                "funnel_name": "Sign-up Funnel",
                "total_users_entered": 1000,
                "total_users_completed": 250,
                "overall_conversion_rate": 0.25,
                "avg_completion_time": 180.5,
                "steps": [
                    {
                        "step_order": 1,
                        "event_name": "landing_page_view",
                        "name": "Landing Page",
                        "users_entered": 1000,
                        "users_completed": 500,
                        "conversion_rate": 0.50,
                        "drop_off_rate": 0.50,
                        "avg_time_to_next_step": 45.2,
                    },
                ],
            },
        }
