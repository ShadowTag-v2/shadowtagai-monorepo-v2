# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# 1. Fetch the Database URL from the environment (matching our Docker setup)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://REDACTED_USER:REDACTED_PASS@localhost:5432/ShadowTag-v2_db",
)

# 2. Create the SQLAlchemy Engine
engine = create_engine(DATABASE_URL, echo=False)

# 3. Create a Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 4. Define the Base class using modern SQLAlchemy 2.0 syntax
class Base(DeclarativeBase):
    pass


# 5. Dependency injection function for FastAPI routes
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
