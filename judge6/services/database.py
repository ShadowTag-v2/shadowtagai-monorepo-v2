# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Database Service
SQLAlchemy async database connection and session management
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from collections.abc import AsyncGenerator

from ..core.config import settings
from ..models.database import Base


# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    poolclass=NullPool,  # For async, use NullPool
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database session in FastAPI routes

    Usage:
    @app.get("/users")
    async def get_users(db: AsyncSession = Depends(get_db)):
        users = await db.execute(select(User))
        return users.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# For non-async contexts (like Stripe webhooks)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker as sync_sessionmaker

# Sync engine (convert async URL to sync)
sync_db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
sync_engine = create_engine(sync_db_url, echo=settings.DATABASE_ECHO)

SyncSessionLocal = sync_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)


def get_sync_db():
    """Get synchronous database session"""
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()
