"""
User Service Layer

Encapsulates all user-related database operations.
Route handlers must delegate here — no raw DB calls in routes.
"""

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.utils.logger import get_logger

logger = get_logger(__name__)


class UserService:
    """Service layer for user management operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def update_user(self, user: User, full_name: str | None, email: str | None) -> User:
        """Update user profile fields and persist."""
        if full_name is not None:
            user.full_name = full_name
        if email is not None:
            user.email = email

        await self.db.commit()
        await self.db.refresh(user)

        logger.info("user_updated", user_id=user.id)
        return user

    async def soft_delete_user(self, user: User) -> None:
        """Soft-delete a user account (deactivate, set deleted_at)."""
        user.deleted_at = datetime.utcnow()
        user.is_active = False

        await self.db.commit()

        logger.info("user_deleted", user_id=user.id)
