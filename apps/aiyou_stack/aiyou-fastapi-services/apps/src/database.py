# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Database configuration and session management."""

import os
from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .models.agent_models import Base

# Database URL - defaults to SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ShadowTag-v2_agents.db")

# For PostgreSQL in production (Vertex AI / Cloud SQL)
# DATABASE_URL = "postgresql://REDACTED_USER:REDACTED_PASS@localhost/dbname"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    pool_pre_ping=True,  # Verify connections before using
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",  # Log SQL queries if enabled
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")


def get_db() -> Generator[Session, None, None]:
    """Dependency for getting database sessions in FastAPI routes.

    Yields:
        Database session

    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """Context manager for getting database sessions outside of FastAPI.

    Yields:
        Database session

    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def reset_db():
    """Reset the database by dropping and recreating all tables."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database reset successfully")
