"""User Model

Security Features:
- Password stored as bcrypt hash only
- Email validation
- Soft delete capability
- Account lock on suspicious activity
- Created/updated timestamps for audit
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.subscription import Subscription


class User(Base):
    """User model with security features

    Security:
    - Never store plaintext passwords
    - Email uniqueness enforced at DB level
    - Account locking mechanism
    - Audit trail (created_at, updated_at)
    """

    __tablename__ = "users"

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Authentication
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Profile
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Security
    is_locked: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="Account locked due to suspicious activity",
    )
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Subscription (for revenue)
    subscription_tier: Mapped[str] = mapped_column(
        String(50), default="free", nullable=False, comment="free, pro, or enterprise",
    )

    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="Soft delete timestamp",
    )

    # Relationships
    subscriptions: Mapped[list[Subscription]] = relationship(
        "Subscription", back_populates="user", lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, tier={self.subscription_tier})>"

    def is_deleted(self) -> bool:
        """Check if user is soft-deleted"""
        return self.deleted_at is not None

    def should_lock_account(self) -> bool:
        """Check if account should be locked (5 failed attempts)"""
        return self.failed_login_attempts >= 5

    def can_login(self) -> bool:
        """Check if user can log in"""
        return self.is_active and not self.is_locked and not self.is_deleted()
