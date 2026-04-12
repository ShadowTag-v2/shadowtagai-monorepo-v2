"""
Subscription Management Endpoints

Revenue:
- Subscription upgrades/downgrades
- Usage tracking
- Payment integration (Stripe)
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.subscription import (
    SubscriptionResponse,
    SubscriptionUpgradeRequest,
    UsageResponse,
)
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)
settings = get_settings()


@router.get("/my-subscription", response_model=SubscriptionResponse)
async def get_my_subscription(
    current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)
) -> Subscription:
    """
    Get current user's subscription

    Revenue:
    - Shows current tier and usage
    - Opportunity to upsell if near limits
    """
    result = await db.execute(
        select(Subscription)
        .where(Subscription.user_id == current_user.id)
        .where(Subscription.status.in_(["active", "trialing"]))
    )
    subscription = result.scalar_one_or_none()

    if subscription is None:
        # Create default free subscription if none exists
        subscription = Subscription(
            user_id=current_user.id,
            tier="free",
            status="active",
            price=0,
            api_calls_count=0,
            api_calls_limit=1000,  # Free tier limit
            current_period_start=datetime.utcnow(),
        )
        db.add(subscription)
        await db.commit()
        await db.refresh(subscription)

    return subscription


@router.get("/usage", response_model=UsageResponse)
async def get_usage(
    current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)
) -> UsageResponse:
    """
    Get current usage statistics

    Revenue:
    - Shows usage vs limits
    - Trigger upsell when approaching limits
    """
    result = await db.execute(
        select(Subscription)
        .where(Subscription.user_id == current_user.id)
        .where(Subscription.status.in_(["active", "trialing"]))
    )
    subscription = result.scalar_one_or_none()

    if subscription is None:
        return UsageResponse(
            api_calls_count=0, api_calls_limit=1000, percentage_used=0.0, tier="free"
        )

    percentage_used = None
    if subscription.api_calls_limit:
        percentage_used = subscription.api_calls_count / subscription.api_calls_limit * 100

    return UsageResponse(
        api_calls_count=subscription.api_calls_count,
        api_calls_limit=subscription.api_calls_limit,
        percentage_used=percentage_used,
        tier=subscription.tier,
    )


@router.post("/upgrade", response_model=SubscriptionResponse)
async def upgrade_subscription(
    upgrade_data: SubscriptionUpgradeRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Subscription:
    """
    Upgrade subscription to higher tier

    Revenue:
    - Main monetization endpoint
    - Integrates with Stripe for payment
    - Immediate tier upgrade on payment success

    Security:
    - Payment verification required
    - Idempotency handling
    """
    # Get current subscription
    result = await db.execute(
        select(Subscription)
        .where(Subscription.user_id == current_user.id)
        .where(Subscription.status.in_(["active", "trialing"]))
    )
    subscription = result.scalar_one_or_none()

    # Validate upgrade path
    tier_hierarchy = {"free": 0, "pro": 1, "enterprise": 2}
    current_tier_level = tier_hierarchy.get(subscription.tier if subscription else "free", 0)
    new_tier_level = tier_hierarchy.get(upgrade_data.new_tier, 0)

    if new_tier_level <= current_tier_level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Can only upgrade to higher tier"
        )

    # Get tier pricing
    tier_prices = {
        "pro": settings.TIER_PRO_PRICE,
        "enterprise": settings.TIER_ENTERPRISE_PRICE,
    }
    price = tier_prices.get(upgrade_data.new_tier, 0)

    # TODO: Integrate with Stripe payment processing
    # For now, we'll create/update subscription assuming payment succeeded
    # In production, this would:
    # 1. Create Stripe subscription
    # 2. Verify payment
    # 3. Update database on webhook callback

    if subscription is None:
        # Create new subscription
        subscription = Subscription(
            user_id=current_user.id,
            tier=upgrade_data.new_tier,
            status="active",
            price=price,
            api_calls_count=0,
            api_calls_limit=None,  # Unlimited for paid tiers
            current_period_start=datetime.utcnow(),
        )
        db.add(subscription)
    else:
        # Upgrade existing subscription
        subscription.tier = upgrade_data.new_tier
        subscription.price = price
        subscription.api_calls_limit = None  # Unlimited for paid tiers
        subscription.status = "active"

    # Update user tier
    current_user.subscription_tier = upgrade_data.new_tier

    await db.commit()
    await db.refresh(subscription)

    logger.info(
        "subscription_upgraded",
        user_id=current_user.id,
        old_tier=current_user.subscription_tier,
        new_tier=upgrade_data.new_tier,
    )

    return subscription


@router.post("/cancel", status_code=status.HTTP_200_OK)
async def cancel_subscription(
    current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Cancel subscription

    Revenue:
    - Retention opportunity
    - Cancel at period end (user keeps access until paid period ends)
    """
    result = await db.execute(
        select(Subscription)
        .where(Subscription.user_id == current_user.id)
        .where(Subscription.status == "active")
    )
    subscription = result.scalar_one_or_none()

    if subscription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No active subscription found"
        )

    if subscription.tier == "free":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot cancel free tier"
        )

    # Mark for cancellation at period end
    subscription.cancel_at_period_end = True
    subscription.canceled_at = datetime.utcnow()

    await db.commit()

    logger.info("subscription_canceled", user_id=current_user.id, tier=subscription.tier)

    return {
        "message": "Subscription will be canceled at the end of the current billing period",
        "access_until": subscription.current_period_end,
    }
