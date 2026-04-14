"""User schemas"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for creating a user"""

    user_id: str = Field(..., description="Unique user identifier")
    anonymous_id: str | None = Field(None, description="Anonymous ID")
    email: EmailStr | None = Field(None, description="User email")
    name: str | None = Field(None, description="User name")
    properties: dict[str, Any] | None = Field(default_factory=dict, description="User properties")
    segment: str | None = Field(None, description="User segment")
    cohort: str | None = Field(None, description="User cohort")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "email": "user@example.com",
                "name": "John Doe",
                "properties": {"plan": "premium", "signup_source": "landing_page"},
                "segment": "power_users",
            },
        }


class UserUpdate(BaseModel):
    """Schema for updating a user"""

    email: EmailStr | None = None
    name: str | None = None
    properties: dict[str, Any] | None = None
    segment: str | None = None
    cohort: str | None = None
    is_active: bool | None = None
    is_verified: bool | None = None


class UserResponse(BaseModel):
    """Schema for user response"""

    id: UUID
    user_id: str
    email: str | None
    name: str | None
    properties: dict[str, Any]
    segment: str | None
    cohort: str | None
    is_active: bool
    is_verified: bool
    first_seen: datetime
    last_seen: datetime
    event_count: int
    session_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
