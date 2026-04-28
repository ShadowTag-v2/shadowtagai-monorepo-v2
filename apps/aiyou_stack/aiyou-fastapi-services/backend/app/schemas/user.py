# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""User schemas"""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema"""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: str | None = None


class UserCreate(UserBase):
    """Schema for creating a user"""

    password: str = Field(..., min_length=8)
    marketing_consent: bool = False
    analytics_consent: bool = False


class UserResponse(UserBase):
    """Schema for user response"""

    id: uuid.UUID
    is_active: bool
    is_verified: bool
    gdpr_applies: bool
    ccpa_applies: bool
    marketing_consent: bool
    analytics_consent: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
