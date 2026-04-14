"""Subscription Model for Revenue Tracking

Monetization Features:
- Track subscription tiers (free, pro, enterprise)
- Stripe integration ready
- Payment history
- Usage limits per tier
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class Subscription(Base):
    """Subscription model for revenue tracking

    Revenue Features:
    - Multiple tiers with different pricing
    - Stripe subscription ID tracking
    - Payment status monitoring
    - Usage tracking for metered billing
    """

    __tablename__ = "subscriptions"

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # User Relationship
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True,
    )

    # Subscription Details
    tier: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="free, pro, or enterprise",
    )
    status: Mapped[str] = mapped_column(
        String(50), default="active", nullable=False, comment="active, canceled, past_due, trialing",
    )

    # Stripe Integration
    stripe_subscription_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True, index=True,
    )
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    # Pricing (in cents)
    price: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Price in cents (e.g., 2900 = $29.00)",
    )

    # Billing Period
    current_period_start: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Trial
    trial_start: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    trial_end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Usage Tracking (for metered billing)
    api_calls_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    api_calls_limit: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="NULL = unlimited",
    )

    # Payment
    last_payment_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_payment_amount: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Last payment in cents",
    )

    # Cancellation
    canceled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="subscriptions")

    def __repr__(self) -> str:
        return f"<Subscription(id={self.id}, user_id={self.user_id}, tier={self.tier}, status={self.status})>"

    def is_active(self) -> bool:
        """Check if subscription is currently active"""
        return self.status in ["active", "trialing"]

    def is_within_limits(self) -> bool:
        """Check if usage is within limits"""
        if self.api_calls_limit is None:
            return True
        return self.api_calls_count < self.api_calls_limit

    def can_access_feature(self, feature_tier: str) -> bool:
        """Check if subscription tier can access feature

        Args:
            feature_tier: Required tier (free, pro, enterprise)

        Returns:
            True if user's tier >= required tier

        """
        tier_hierarchy = {"free": 0, "pro": 1, "enterprise": 2}
        user_tier_level = tier_hierarchy.get(self.tier, 0)
        required_tier_level = tier_hierarchy.get(feature_tier, 0)
        return user_tier_level >= required_tier_level
