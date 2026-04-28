# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Initialize database with tables"""

import asyncio

from sqlalchemy.ext.asyncio import create_async_engine

from src.config import settings
from src.database import Base


async def init_db():
    """Create all database tables"""
    print("Creating database tables...")

    engine = create_async_engine(settings.database_url, echo=True)

    async with engine.begin() as conn:
        # Drop all tables (use with caution in production!)
        # await conn.run_sync(Base.metadata.drop_all)

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()

    print("Database tables created successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())
