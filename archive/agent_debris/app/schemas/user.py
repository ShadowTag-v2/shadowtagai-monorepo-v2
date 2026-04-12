"""User schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    email: EmailStr | None = None
    username: str | None = None
    memory_enabled: bool | None = None
    auto_summarization_enabled: bool | None = None


class UserResponse(UserBase):
    """Schema for user response."""

    id: int
    is_active: bool
    memory_enabled: bool
    auto_summarization_enabled: bool
    created_at: datetime
    last_login: datetime | None = None

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """Schema for JWT token."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token data."""

    user_id: int | None = None
