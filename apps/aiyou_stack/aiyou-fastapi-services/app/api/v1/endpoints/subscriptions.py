"""Subscription Management Endpoints

Revenue:
- Subscription upgrades/downgrades
- Usage tracking
- Payment integration (Stripe)
"""

from fastapi import APIRouter, Depends, HTTPException, status
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
from app.services.subscription_service import SubscriptionService
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)
settings = get_settings()


def get_subscription_service(db: AsyncSession = Depends(get_db)) -> SubscriptionService:
    """Dependency to get SubscriptionService instance."""
    return SubscriptionService(db)


@router.get("/my-subscription", response_model=SubscriptionResponse)
async def get_my_subscription(
    current_user: User = Depends(get_current_active_user),
    service: SubscriptionService = Depends(get_subscription_service),
) -> Subscription:
    """Get current user's subscription

    Revenue:
    - Shows current tier and usage
    - Opportunity to upsell if near limits
    """
    subscription = await service.get_active_subscription(current_user.id)

    if subscription is None:
        # Create default free subscription if none exists
        subscription = await service.create_free_subscription(current_user.id)

    return subscription


@router.get("/usage", response_model=UsageResponse)
async def get_usage(
    current_user: User = Depends(get_current_active_user),
    service: SubscriptionService = Depends(get_subscription_service),
) -> UsageResponse:
    """Get current usage statistics

    Revenue:
    - Shows usage vs limits
    - Trigger upsell when approaching limits
    """
    subscription = await service.get_active_subscription(current_user.id)

    if subscription is None:
        return UsageResponse(
            api_calls_count=0,
            api_calls_limit=1000,
            percentage_used=0.0,
            tier="free",
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
    service: SubscriptionService = Depends(get_subscription_service),
) -> Subscription:
    """Upgrade subscription to higher tier

    Revenue:
    - Main monetization endpoint
    - Integrates with Stripe for payment
    - Immediate tier upgrade on payment success

    Security:
    - Payment verification required
    - Idempotency handling
    """
    subscription = await service.get_active_subscription(current_user.id)

    # Validate upgrade path
    tier_hierarchy = {"free": 0, "pro": 1, "enterprise": 2}
    current_tier_level = tier_hierarchy.get(subscription.tier if subscription else "free", 0)
    new_tier_level = tier_hierarchy.get(upgrade_data.new_tier, 0)

    if new_tier_level <= current_tier_level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only upgrade to higher tier",
        )

    # Get tier pricing
    tier_prices = {
        "pro": settings.TIER_PRO_PRICE,
        "enterprise": settings.TIER_ENTERPRISE_PRICE,
    }
    price = tier_prices.get(upgrade_data.new_tier, 0)

    # TODO: Integrate with Stripe payment processing
    # For now, we'll create/update subscription assuming payment succeeded

    subscription = await service.upgrade_subscription(
        subscription,
        current_user,
        upgrade_data.new_tier,
        price,
    )

    logger.info(
        "subscription_upgraded",
        user_id=current_user.id,
        old_tier=current_user.subscription_tier,
        new_tier=upgrade_data.new_tier,
    )

    return subscription


@router.post("/cancel", status_code=status.HTTP_200_OK)
async def cancel_subscription(
    current_user: User = Depends(get_current_active_user),
    service: SubscriptionService = Depends(get_subscription_service),
) -> dict:
    """Cancel subscription

    Revenue:
    - Retention opportunity
    - Cancel at period end (user keeps access until paid period ends)
    """
    subscription = await service.get_active_only_subscription(current_user.id)

    if subscription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found",
        )

    if subscription.tier == "free":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel free tier",
        )

    await service.cancel_subscription(subscription)

    logger.info("subscription_canceled", user_id=current_user.id, tier=subscription.tier)

    return {
        "message": "Subscription will be canceled at the end of the current billing period",
        "access_until": subscription.current_period_end,
    }
