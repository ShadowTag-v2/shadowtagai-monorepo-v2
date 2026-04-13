"""
Authentication Service Layer

Encapsulates all database operations for user authentication,
registration, and token management.
"""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User


class AuthService:
    """Service layer for authentication operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(self, email: str) -> User | None:
        """Retrieve a user by email address."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> User | None:
        """Retrieve a user by ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create_user(self, email: str, full_name: str, hashed_password: str) -> User:
        """Create a new user with the given details."""
        new_user = User(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=False,
            subscription_tier="free",
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def record_failed_login(self, user: User) -> None:
        """Increment failed login attempts and lock if threshold reached."""
        user.failed_login_attempts += 1
        if user.should_lock_account():
            user.is_locked = True
        await self.db.commit()

    async def record_successful_login(self, user: User) -> None:
        """Reset failed attempts and update last login timestamp."""
        user.failed_login_attempts = 0
        user.last_login = datetime.utcnow()
        await self.db.commit()

    async def update_password(self, user: User, new_hashed_password: str) -> None:
        """Update a user's password hash."""
        user.hashed_password = new_hashed_password
        await self.db.commit()

    def create_token_pair(self, user_id: int) -> dict:
        """Generate an access/refresh token pair for a user."""
        access_token = create_access_token(data={"sub": str(user_id)})
        refresh_token = create_refresh_token(data={"sub": str(user_id)})
        return {"access_token": access_token, "refresh_token": refresh_token}
