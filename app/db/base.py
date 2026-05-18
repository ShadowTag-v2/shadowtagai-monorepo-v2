# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Database base configuration — lazy initialization for Cloud Run.

The engine and session factory are created lazily via get_engine() / get_session_factory()
to avoid import-time failures in containers without DATABASE_URL.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# Declarative base can be created at import time (no I/O)
Base = declarative_base()

# Lazy singletons
_engine = None
_session_factory = None


def get_engine():
  """Get or create the async engine (lazy singleton)."""
  global _engine
  if _engine is None:
    _engine = create_async_engine(
      settings.database_url,
      echo=settings.debug,
      future=True,
    )
  return _engine


def get_session_factory():
  """Get or create the async session factory (lazy singleton)."""
  global _session_factory
  if _session_factory is None:
    _session_factory = sessionmaker(
      get_engine(),
      class_=AsyncSession,
      expire_on_commit=False,
      autocommit=False,
      autoflush=False,
    )
  return _session_factory


async def get_db() -> AsyncSession:
  """Dependency for getting async database sessions."""
  factory = get_session_factory()
  async with factory() as session:
    try:
      yield session
      await session.commit()
    except Exception:
      await session.rollback()
      raise
    finally:
      await session.close()


async def init_db() -> None:
  """Initialize database tables."""
  engine = get_engine()
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
