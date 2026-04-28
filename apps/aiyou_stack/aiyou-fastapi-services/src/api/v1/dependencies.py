# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""API dependencies"""

from collections.abc import Generator

from sqlalchemy.orm import Session

from src.core.settings import get_settings
from src.db.session import SessionLocal
from src.services.email.service import EmailService


def get_db() -> Generator[Session, None, None]:
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_email_service() -> EmailService:
    """Email service dependency"""
    return EmailService()


def get_settings_dependency():
    """Settings dependency"""
    return get_settings()
