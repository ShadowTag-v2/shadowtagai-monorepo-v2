"""
Subscription Service Layer

Encapsulates all database operations for subscription management,
usage tracking, tier upgrades, and cancellations.
"""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscription import Subscription
from app.models.user import User


class SubscriptionService:
    """Service layer for subscription operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_active_subscription(self, user_id: int) -> Subscription | None:
        """Get a user's active or trialing subscription."""
        result = await self.db.execute(
            select(Subscription)
            .where(Subscription.user_id == user_id)
            .where(Subscription.status.in_(["active", "trialing"]))
        )
        return result.scalar_one_or_none()

    async def get_active_only_subscription(self, user_id: int) -> Subscription | None:
        """Get a user's explicitly active subscription (excludes trialing)."""
        result = await self.db.execute(
            select(Subscription)
            .where(Subscription.user_id == user_id)
            .where(Subscription.status == "active")
        )
        return result.scalar_one_or_none()

    async def create_free_subscription(self, user_id: int) -> Subscription:
        """Create a default free-tier subscription for a user."""
        subscription = Subscription(
            user_id=user_id,
            tier="free",
            status="active",
            price=0,
            api_calls_count=0,
            api_calls_limit=1000,
            current_period_start=datetime.utcnow(),
        )
        self.db.add(subscription)
        await self.db.commit()
        await self.db.refresh(subscription)
        return subscription

    async def upgrade_subscription(
        self,
        subscription: Subscription | None,
        user: User,
        new_tier: str,
        price: int,
    ) -> Subscription:
        """Upgrade (or create) a subscription to the specified tier."""
        if subscription is None:
            subscription = Subscription(
                user_id=user.id,
                tier=new_tier,
                status="active",
                price=price,
                api_calls_count=0,
                api_calls_limit=None,
                current_period_start=datetime.utcnow(),
            )
            self.db.add(subscription)
        else:
            subscription.tier = new_tier
            subscription.price = price
            subscription.api_calls_limit = None
            subscription.status = "active"

        user.subscription_tier = new_tier
        await self.db.commit()
        await self.db.refresh(subscription)
        return subscription

    async def cancel_subscription(self, subscription: Subscription) -> None:
        """Mark a subscription for cancellation at the end of the billing period."""
        subscription.cancel_at_period_end = True
        subscription.canceled_at = datetime.utcnow()
        await self.db.commit()
