"""Event schemas"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    """Schema for creating an event"""

    event_name: str = Field(..., description="Name of the event")
    event_type: str | None = Field(
        None, description="Type of event (page_view, click, conversion, etc.)"
    )

    # User identification
    user_id: str | None = Field(None, description="User ID")
    anonymous_id: str | None = Field(None, description="Anonymous ID for non-authenticated users")
    session_id: str | None = Field(None, description="Session ID")

    # Event properties
    properties: dict[str, Any] | None = Field(default_factory=dict, description="Event properties")

    # Page information
    page_url: str | None = Field(None, description="Page URL")
    page_title: str | None = Field(None, description="Page title")
    referrer: str | None = Field(None, description="Referrer URL")

    # Device and browser
    user_agent: str | None = Field(None, description="User agent string")
    device_type: str | None = Field(None, description="Device type (mobile, tablet, desktop)")
    browser: str | None = Field(None, description="Browser name")
    os: str | None = Field(None, description="Operating system")

    # Location
    country: str | None = Field(None, description="Country")
    region: str | None = Field(None, description="Region/State")
    city: str | None = Field(None, description="City")
    ip_address: str | None = Field(None, description="IP address")

    # Campaign tracking
    utm_source: str | None = Field(None, description="UTM source")
    utm_medium: str | None = Field(None, description="UTM medium")
    utm_campaign: str | None = Field(None, description="UTM campaign")
    utm_term: str | None = Field(None, description="UTM term")
    utm_content: str | None = Field(None, description="UTM content")

    # Value tracking
    revenue: float | None = Field(None, description="Revenue amount")
    currency: str | None = Field(None, description="Currency code")

    timestamp: datetime | None = Field(None, description="Event timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "event_name": "purchase_completed",
                "event_type": "conversion",
                "user_id": "user_123",
                "session_id": "session_abc",
                "properties": {
                    "product_id": "prod_456",
                    "product_name": "Premium Plan",
                    "quantity": 1,
                },
                "revenue": 99.99,
                "currency": "USD",
            }
        }


class EventResponse(BaseModel):
    """Schema for event response"""

    id: UUID
    event_name: str
    event_type: str | None
    user_id: str | None
    anonymous_id: str | None
    session_id: str | None
    properties: dict[str, Any]
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class EventQuery(BaseModel):
    """Schema for querying events"""

    event_name: str | None = None
    event_type: str | None = None
    user_id: str | None = None
    session_id: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    limit: int = Field(default=100, le=1000)
    offset: int = Field(default=0, ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "event_name": "page_view",
                "start_date": "2025-01-01T00:00:00Z",
                "end_date": "2025-01-31T23:59:59Z",
                "limit": 100,
            }
        }
