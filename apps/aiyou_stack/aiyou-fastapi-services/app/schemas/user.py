"""User Schemas with Input Validation

Security:
- Email validation
- Password [VAPORIZED_PWD] validation
- No sensitive data in responses
- XSS prevention via sanitization
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Base user schema"""

    email: EmailStr
    full_name: str | None = Field(None, max_length=255)


class UserCreate(UserBase):
    """User creation schema

    Security:
    - Email validation (EmailStr)
    - Password [VAPORIZED_PWD] in endpoint
    - Length limits on all fields
    """

    password: str = Field(
        ..., min_length=12, max_length=128, description="Password must be at least 12 characters",
    )

    @field_validator("full_name")
    @classmethod
    def sanitize_full_name(cls, v: str | None) -> str | None:
        """Sanitize full name to prevent XSS"""
        if v:
            # Remove potentially dangerous characters
            dangerous_chars = ["<", ">", "&", '"', "'", "/", "\\"]
            for char in dangerous_chars:
                v = v.replace(char, "")
        return v


class UserUpdate(BaseModel):
    """User update schema"""

    full_name: str | None = Field(None, max_length=255)
    email: EmailStr | None = None

    @field_validator("full_name")
    @classmethod
    def sanitize_full_name(cls, v: str | None) -> str | None:
        """Sanitize full name to prevent XSS"""
        if v:
            dangerous_chars = ["<", ">", "&", '"', "'", "/", "\\"]
            for char in dangerous_chars:
                v = v.replace(char, "")
        return v


class UserResponse(UserBase):
    """User response schema

    Security:
    - NO password hash exposed
    - NO sensitive internal fields
    - Only safe public data
    """

    id: int
    is_active: bool
    is_verified: bool
    subscription_tier: str
    created_at: datetime
    last_login: datetime | None = None

    model_config = {"from_attributes": True}


class UserWithSubscription(UserResponse):
    """User response with subscription details"""

    api_calls_count: int = 0
    api_calls_limit: int | None = None

    model_config = {"from_attributes": True}
