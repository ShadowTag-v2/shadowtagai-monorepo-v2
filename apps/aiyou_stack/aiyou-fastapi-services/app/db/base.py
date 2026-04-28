# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""SQLAlchemy base and declarative base"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models"""
