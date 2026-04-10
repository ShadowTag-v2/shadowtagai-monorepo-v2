"""User management service"""

from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate


class UserService:
    """Service for managing users"""

    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        """Create a new user"""
        user = User(
            user_id=user_data.user_id,
            anonymous_id=user_data.anonymous_id,
            email=user_data.email,
            name=user_data.name,
            properties=user_data.properties or {},
            segment=user_data.segment,
            cohort=user_data.cohort,
        )

        db.add(user)
        await db.flush()
        return user

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
        """Get user by user_id"""
        result = await db.execute(select(User).where(User.user_id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_user(db: AsyncSession, user_id: str, user_data: UserUpdate) -> User | None:
        """Update user information"""
        user = await UserService.get_user_by_id(db, user_id)

        if not user:
            return None

        # Update fields
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_at = datetime.utcnow()
        await db.flush()

        return user

    @staticmethod
    async def get_or_create_user(
        db: AsyncSession, user_id: str, user_data: UserCreate | None = None
    ) -> User:
        """Get existing user or create new one"""
        user = await UserService.get_user_by_id(db, user_id)

        if user:
            return user

        # Create new user
        if not user_data:
            user_data = UserCreate(user_id=user_id)

        return await UserService.create_user(db, user_data)

    @staticmethod
    async def list_users(
        db: AsyncSession,
        segment: str | None = None,
        cohort: str | None = None,
        is_active: bool | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[User]:
        """List users with filtering"""
        stmt = select(User)

        conditions = []

        if segment:
            conditions.append(User.segment == segment)

        if cohort:
            conditions.append(User.cohort == cohort)

        if is_active is not None:
            conditions.append(User.is_active == is_active)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.order_by(User.created_at.desc())
        stmt = stmt.limit(limit).offset(offset)

        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_user_segments(db: AsyncSession) -> list[str]:
        """Get list of all unique user segments"""
        result = await db.execute(select(User.segment).distinct().where(User.segment.isnot(None)))
        return [row[0] for row in result.all()]

    @staticmethod
    async def get_user_cohorts(db: AsyncSession) -> list[str]:
        """Get list of all unique user cohorts"""
        result = await db.execute(select(User.cohort).distinct().where(User.cohort.isnot(None)))
        return [row[0] for row in result.all()]
