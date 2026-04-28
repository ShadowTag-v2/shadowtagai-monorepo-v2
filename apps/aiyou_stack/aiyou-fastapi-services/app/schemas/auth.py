# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Authentication Schemas

Security:
- Input validation
- Token type safety
- No credential leakage
"""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Login request schema"""

    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


class TokenResponse(BaseModel):
    """Token response schema

    Security:
    - Separate access and refresh tokens
    - Token type specified
    - No user credentials in response
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""

    refresh_token: str = Field(..., min_length=1)


class PasswordChangeRequest(BaseModel):
    """Password change request"""

    current_password: str = Field(..., min_length=1, max_length=128)
    new_password: str = Field(
        ...,
        min_length=12,
        max_length=128,
        description="Password must be at least 12 characters",
    )


class PasswordResetRequest(BaseModel):
    """Password reset request (forgot password)"""

    email: EmailStr
