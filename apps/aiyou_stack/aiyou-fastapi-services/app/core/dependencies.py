# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Dependency Injection for Authentication

Security:
- JWT verification
- User session validation
- Permission checks
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_access_token
from app.db.session import get_db
from app.models.user import User

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),  # noqa: B008
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> User:
    """Get current authenticated user from JWT token

    Security:
    - Token verification
    - User existence check
    - Account status validation
    - No caching (always fresh data)

    Raises:
        HTTPException: 401 if token invalid or user not found

    Returns:
        User object

    """
    token = credentials.credentials

    # Verify and decode token
    user_id = verify_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Validate user can log in
    if not user.can_login():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive, locked, or deleted",
        )

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:  # noqa: B008
    """Get current user and ensure account is active

    Security:
    - Additional active check
    - Prevents soft-deleted users

    Returns:
        Active user object

    """
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")

    return current_user


async def require_tier(
    required_tier: str,
    current_user: User = Depends(get_current_active_user),  # noqa: B008
) -> User:
    """Require specific subscription tier

    Revenue:
    - Tier-based access control
    - Upsell opportunity on 403

    Args:
        required_tier: Minimum tier required (free, pro, enterprise)
        current_user: Current authenticated user

    Raises:
        HTTPException: 403 if user tier insufficient

    Returns:
        User object if authorized

    """
    tier_hierarchy = {"free": 0, "pro": 1, "enterprise": 2}
    user_tier_level = tier_hierarchy.get(current_user.subscription_tier, 0)
    required_tier_level = tier_hierarchy.get(required_tier, 0)

    if user_tier_level < required_tier_level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"This feature requires {required_tier} tier or higher. Upgrade your subscription.",
        )

    return current_user


# Convenience dependencies for tier requirements
async def require_pro_tier(current_user: User = Depends(get_current_active_user)) -> User:  # noqa: B008
    """Require pro tier or higher"""
    return await require_tier("pro", current_user)


async def require_enterprise_tier(current_user: User = Depends(get_current_active_user)) -> User:  # noqa: B008
    """Require enterprise tier"""
    return await require_tier("enterprise", current_user)
