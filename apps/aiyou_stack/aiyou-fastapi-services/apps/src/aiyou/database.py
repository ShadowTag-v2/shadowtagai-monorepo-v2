# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Database connection and session management.

Provides SQLAlchemy engine, session factory, and base declarative class.
"""

import logging
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import Pool

from .config import settings

logger = logging.getLogger(__name__)

# Create SQLAlchemy engine
connect_args: dict[str, Any] = {}
engine_args: dict[str, Any] = {
    "echo": settings.database_echo,
    "pool_pre_ping": True,
}

if "sqlite" in settings.database_url:
    connect_args["check_same_thread"] = False
    from sqlalchemy.pool import StaticPool

    engine_args["poolclass"] = StaticPool
else:
    engine_args["pool_size"] = settings.database_pool_size
    engine_args["max_overflow"] = settings.database_max_overflow

engine = create_engine(settings.database_url, connect_args=connect_args, **engine_args)


# Enable connection pooling optimizations
@event.listens_for(Pool, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Set SQLite pragmas for performance (if using SQLite)."""
    if "sqlite" in settings.database_url:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()


# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency for FastAPI routes to get database session.

    Yields:
        Database session

    Example:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()

    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for database sessions outside FastAPI routes.

    Yields:
        Database session

    Example:
        with get_db_context() as db:
            user = db.query(User).first()

    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """Initialize database by creating all tables.

    Should be called during application startup.
    """
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")


def check_db_connection() -> bool:
    """Check if database connection is healthy.

    Returns:
        True if connection is healthy, False otherwise

    """
    try:
        with get_db_context() as db:
            db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
