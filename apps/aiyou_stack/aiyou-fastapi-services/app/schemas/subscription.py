"""Subscription Schemas for Revenue Management

Monetization:
- Tier selection
- Payment tracking
- Usage monitoring
"""

from datetime import datetime

from pydantic import BaseModel, Field


class SubscriptionBase(BaseModel):
    """Base subscription schema"""

    tier: str = Field(..., pattern="^(free|pro|enterprise)$")


class SubscriptionCreate(SubscriptionBase):
    """Subscription creation schema

    Revenue:
    - Tier selection
    - Payment method required for paid tiers
    """

    payment_method_id: str | None = Field(
        None,
        description="Stripe payment method ID (required for pro/enterprise)",
    )


class SubscriptionUpdate(BaseModel):
    """Subscription update schema"""

    tier: str | None = Field(None, pattern="^(free|pro|enterprise)$")
    cancel_at_period_end: bool | None = None


class SubscriptionResponse(SubscriptionBase):
    """Subscription response schema

    Revenue tracking:
    - Current tier and status
    - Billing period
    - Usage limits
    """

    id: int
    user_id: int
    status: str
    price: int
    current_period_start: datetime | None
    current_period_end: datetime | None
    api_calls_count: int
    api_calls_limit: int | None
    cancel_at_period_end: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UsageResponse(BaseModel):
    """API usage response"""

    api_calls_count: int
    api_calls_limit: int | None
    percentage_used: float | None = None
    tier: str


class SubscriptionUpgradeRequest(BaseModel):
    """Subscription upgrade request"""

    new_tier: str = Field(..., pattern="^(pro|enterprise)$")
    payment_method_id: str = Field(..., description="Stripe payment method ID")
