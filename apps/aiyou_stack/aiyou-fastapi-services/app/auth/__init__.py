# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Authentication module for API Builder.
Provides JWT authentication, API key authentication, and OAuth2 support.
"""

from app.auth.api_key import get_api_key, verify_api_key
from app.auth.jwt import (
    create_access_token,
    create_refresh_token,
    get_current_active_user,
    get_current_user,
    verify_token,
)
from app.auth.password import get_password_hash, verify_password

__all__ = [
    "create_access_token",
    "create_refresh_token",
    "get_api_key",
    "get_current_active_user",
    "get_current_user",
    "get_password_hash",
    "verify_api_key",
    "verify_password",
    "verify_token",
]
