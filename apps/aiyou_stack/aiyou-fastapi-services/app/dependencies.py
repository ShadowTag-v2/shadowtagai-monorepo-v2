"""Common dependencies for FastAPI routes
"""

from app.db.session import SessionLocal


def get_db():
    """Dependency function to get database session.
    Yields a database session and closes it after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
