"""
Monetization layer for ShadowTag-v2 Intelligence Services.

Implements:
- Stripe payment integration
- Usage-based billing
- Tiered pricing plans
- Webhook handling
- Revenue tracking
"""

import hashlib
import hmac
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class PricingTier(Enum):
    """Pricing tier levels."""

    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


@dataclass
class PricingPlan:
    """Pricing plan configuration."""

    tier: PricingTier
    name: str
    price_monthly: float
    price_annual: float  # Annual discount applied

    # Limits
    max_sources: int
    max_items_per_day: int
    max_api_calls_per_month: int

    # Features
    visualizations: bool
    ml_anomaly_detection: bool
    priority_support: bool
    custom_integrations: bool
    sla_guarantee: float | None = None  # Uptime %

    # Stripe IDs
    stripe_price_id_monthly: str | None = None
    stripe_price_id_annual: str | None = None


# Pricing tiers configuration
PRICING_PLANS = {
    PricingTier.FREE: PricingPlan(
        tier=PricingTier.FREE,
        name="Free",
        price_monthly=0.0,
        price_annual=0.0,
        max_sources=2,
        max_items_per_day=100,
        max_api_calls_per_month=1000,
        visualizations=False,
        ml_anomaly_detection=False,
        priority_support=False,
        custom_integrations=False,
    ),
    PricingTier.STARTER: PricingPlan(
        tier=PricingTier.STARTER,
        name="Starter",
        price_monthly=99.0,
        price_annual=990.0,  # 2 months free
        max_sources=5,
        max_items_per_day=1000,
        max_api_calls_per_month=10000,
        visualizations=True,
        ml_anomaly_detection=False,
        priority_support=False,
        custom_integrations=False,
        stripe_price_id_monthly="price_starter_monthly",
        stripe_price_id_annual="price_starter_annual",
    ),
    PricingTier.PROFESSIONAL: PricingPlan(
        tier=PricingTier.PROFESSIONAL,
        name="Professional",
        price_monthly=299.0,
        price_annual=2990.0,  # 2 months free
        max_sources=20,
        max_items_per_day=10000,
        max_api_calls_per_month=100000,
        visualizations=True,
        ml_anomaly_detection=True,
        priority_support=True,
        custom_integrations=False,
        sla_guarantee=99.5,
        stripe_price_id_monthly="price_pro_monthly",
        stripe_price_id_annual="price_pro_annual",
    ),
    PricingTier.ENTERPRISE: PricingPlan(
        tier=PricingTier.ENTERPRISE,
        name="Enterprise",
        price_monthly=999.0,
        price_annual=9990.0,  # 2 months free
        max_sources=999,  # Unlimited
        max_items_per_day=999999,  # Unlimited
        max_api_calls_per_month=9999999,  # Unlimited
        visualizations=True,
        ml_anomaly_detection=True,
        priority_support=True,
        custom_integrations=True,
        sla_guarantee=99.9,
        stripe_price_id_monthly="price_enterprise_monthly",
        stripe_price_id_annual="price_enterprise_annual",
    ),
}


@dataclass
class UsageMetrics:
    """Track usage for billing."""

    customer_id: str
    period_start: datetime
    period_end: datetime

    # Usage counters
    sources_used: int = 0
    items_collected: int = 0
    api_calls_made: int = 0

    # Feature usage
    visualizations_generated: int = 0
    ml_detections_run: int = 0

    # Overage charges
    overage_items: int = 0
    overage_api_calls: int = 0
    overage_cost: float = 0.0


class StripeIntegration:
    """
    Stripe payment integration.

    Handles:
    - Subscription creation and management
    - Usage-based billing
    - Webhook processing
    - Invoice generation
    """

    def __init__(
        self,
        api_key: str,
        webhook_secret: str,
        enable_test_mode: bool = True,
    ):
        self.api_key = api_key
        self.webhook_secret = webhook_secret
        self.test_mode = enable_test_mode

        # In production, initialize Stripe SDK
        # import stripe
        # stripe.api_key = api_key

    async def create_subscription(
        self,
        customer_email: str,
        tier: PricingTier,
        billing_period: str = "monthly",
    ) -> dict:
        """
        Create a new subscription.

        Args:
            customer_email: Customer email
            tier: Pricing tier
            billing_period: monthly or annual

        Returns:
            Subscription details
        """
        plan = PRICING_PLANS[tier]

        if self.test_mode:
            # Mock response
            subscription_id = f"sub_test_{hashlib.sha256(customer_email.encode()).hexdigest()[:12]}"

            return {
                "id": subscription_id,
                "customer_email": customer_email,
                "tier": tier.value,
                "status": "active",
                "current_period_start": datetime.now().isoformat(),
                "current_period_end": (datetime.now() + timedelta(days=30)).isoformat(),
                "amount": plan.price_monthly if billing_period == "monthly" else plan.price_annual,
                "test_mode": True,
            }

        # Production Stripe integration
        # customer = stripe.Customer.create(email=customer_email)
        # subscription = stripe.Subscription.create(
        #     customer=customer.id,
        #     items=[{
        #         'price': plan.stripe_price_id_monthly if billing_period == "monthly"
        #                  else plan.stripe_price_id_annual,
        #     }],
        # )
        # return subscription

        raise NotImplementedError("Production Stripe integration pending")

    async def record_usage(
        self,
        subscription_id: str,
        usage_metrics: UsageMetrics,
    ) -> dict:
        """
        Record usage for billing period.

        Args:
            subscription_id: Stripe subscription ID
            usage_metrics: Usage data

        Returns:
            Updated usage record
        """
        if self.test_mode:
            logger.info(
                f"Recording usage for {subscription_id}: "
                f"{usage_metrics.items_collected} items, "
                f"{usage_metrics.api_calls_made} API calls"
            )

            return {
                "subscription_id": subscription_id,
                "usage_recorded": True,
                "items": usage_metrics.items_collected,
                "api_calls": usage_metrics.api_calls_made,
                "timestamp": datetime.now().isoformat(),
            }

        # Production: Report usage to Stripe
        # stripe.SubscriptionItem.create_usage_record(
        #     subscription_item_id,
        #     quantity=usage_metrics.items_collected,
        #     timestamp=int(datetime.now().timestamp()),
        # )

        raise NotImplementedError("Production usage recording pending")

    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
    ) -> bool:
        """
        Verify Stripe webhook signature.

        Args:
            payload: Webhook payload
            signature: Stripe signature header

        Returns:
            True if valid
        """
        expected_signature = hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    async def handle_webhook(self, event_type: str, data: dict) -> dict:
        """
        Handle Stripe webhook event.

        Args:
            event_type: Event type (e.g., 'invoice.paid')
            data: Event data

        Returns:
            Processing result
        """
        logger.info(f"Processing webhook: {event_type}")

        handlers = {
            "customer.subscription.created": self._handle_subscription_created,
            "customer.subscription.updated": self._handle_subscription_updated,
            "customer.subscription.deleted": self._handle_subscription_deleted,
            "invoice.paid": self._handle_invoice_paid,
            "invoice.payment_failed": self._handle_payment_failed,
        }

        handler = handlers.get(event_type)
        if handler:
            return await handler(data)

        logger.warning(f"Unhandled webhook type: {event_type}")
        return {"status": "ignored"}

    async def _handle_subscription_created(self, data: dict) -> dict:
        """Handle new subscription."""
        subscription_id = data.get("id")
        customer_email = data.get("customer_email")

        logger.info(f"New subscription created: {subscription_id} for {customer_email}")

        # In production: Update database, send welcome email, provision access

        return {"status": "processed", "action": "subscription_created"}

    async def _handle_subscription_updated(self, data: dict) -> dict:
        """Handle subscription update."""
        subscription_id = data.get("id")

        logger.info(f"Subscription updated: {subscription_id}")

        return {"status": "processed", "action": "subscription_updated"}

    async def _handle_subscription_deleted(self, data: dict) -> dict:
        """Handle subscription cancellation."""
        subscription_id = data.get("id")

        logger.info(f"Subscription cancelled: {subscription_id}")

        # In production: Downgrade to free tier, send cancellation email

        return {"status": "processed", "action": "subscription_cancelled"}

    async def _handle_invoice_paid(self, data: dict) -> dict:
        """Handle successful payment."""
        invoice_id = data.get("id")
        amount = data.get("amount_paid", 0) / 100  # Convert cents to dollars

        logger.info(f"Invoice paid: {invoice_id}, amount: ${amount:.2f}")

        return {"status": "processed", "action": "payment_received"}

    async def _handle_payment_failed(self, data: dict) -> dict:
        """Handle failed payment."""
        invoice_id = data.get("id")

        logger.warning(f"Payment failed for invoice: {invoice_id}")

        # In production: Send payment failure email, retry logic

        return {"status": "processed", "action": "payment_failed"}


class UsageTracker:
    """
    Track usage for billing and limits.

    Features:
    - Real-time usage tracking
    - Limit enforcement
    - Overage calculation
    - Billing period management
    """

    def __init__(self, plan: PricingPlan):
        self.plan = plan
        self.current_usage = UsageMetrics(
            customer_id="",
            period_start=datetime.now(),
            period_end=datetime.now() + timedelta(days=30),
        )

    def track_item_collection(self, count: int = 1):
        """Track items collected."""
        self.current_usage.items_collected += count

        # Check limits
        if self.current_usage.items_collected > self.plan.max_items_per_day:
            overage = self.current_usage.items_collected - self.plan.max_items_per_day
            self.current_usage.overage_items += overage

            # $0.001 per overage item
            self.current_usage.overage_cost += overage * 0.001

    def track_api_call(self):
        """Track API call."""
        self.current_usage.api_calls_made += 1

        # Check monthly limit
        if self.current_usage.api_calls_made > self.plan.max_api_calls_per_month:
            overage = self.current_usage.api_calls_made - self.plan.max_api_calls_per_month
            self.current_usage.overage_api_calls += overage

            # $0.0001 per overage API call
            self.current_usage.overage_cost += overage * 0.0001

    def track_visualization(self):
        """Track visualization generation."""
        if not self.plan.visualizations:
            raise ValueError("Visualizations not included in plan. Upgrade to Starter or higher.")

        self.current_usage.visualizations_generated += 1

    def track_ml_detection(self):
        """Track ML anomaly detection."""
        if not self.plan.ml_anomaly_detection:
            raise ValueError(
                "ML detection not included in plan. Upgrade to Professional or higher."
            )

        self.current_usage.ml_detections_run += 1

    def check_limit(self, resource: str) -> bool:
        """
        Check if resource limit reached.

        Args:
            resource: items, api_calls, sources

        Returns:
            True if under limit
        """
        if resource == "items":
            return self.current_usage.items_collected < self.plan.max_items_per_day
        elif resource == "api_calls":
            return self.current_usage.api_calls_made < self.plan.max_api_calls_per_month
        elif resource == "sources":
            return self.current_usage.sources_used < self.plan.max_sources

        return False

    def get_usage_summary(self) -> dict:
        """Get current usage summary."""
        return {
            "plan": self.plan.name,
            "period_start": self.current_usage.period_start.isoformat(),
            "period_end": self.current_usage.period_end.isoformat(),
            "usage": {
                "items_collected": self.current_usage.items_collected,
                "items_limit": self.plan.max_items_per_day,
                "items_remaining": max(
                    0, self.plan.max_items_per_day - self.current_usage.items_collected
                ),
                "api_calls": self.current_usage.api_calls_made,
                "api_calls_limit": self.plan.max_api_calls_per_month,
                "api_calls_remaining": max(
                    0,
                    self.plan.max_api_calls_per_month - self.current_usage.api_calls_made,
                ),
            },
            "overages": {
                "items": self.current_usage.overage_items,
                "api_calls": self.current_usage.overage_api_calls,
                "cost": self.current_usage.overage_cost,
            },
            "features": {
                "visualizations": self.plan.visualizations,
                "ml_anomaly_detection": self.plan.ml_anomaly_detection,
                "priority_support": self.plan.priority_support,
            },
        }


def calculate_revenue_projections(
    monthly_customers_by_tier: dict[PricingTier, int],
    months: int = 12,
    churn_rate: float = 0.05,
) -> dict:
    """
    Calculate revenue projections.

    Args:
        monthly_customers_by_tier: Customer count per tier
        months: Projection period
        churn_rate: Monthly churn rate (default 5%)

    Returns:
        Revenue projections
    """
    monthly_revenue = []
    cumulative_customers = {tier: count for tier, count in monthly_customers_by_tier.items()}

    for _month in range(months):
        # Calculate MRR
        mrr = sum(
            PRICING_PLANS[tier].price_monthly * count
            for tier, count in cumulative_customers.items()
        )

        monthly_revenue.append(mrr)

        # Apply churn
        for tier in cumulative_customers:
            cumulative_customers[tier] = int(cumulative_customers[tier] * (1 - churn_rate))

    total_revenue = sum(monthly_revenue)
    arr = monthly_revenue[-1] * 12 if monthly_revenue else 0

    return {
        "mrr_by_month": monthly_revenue,
        "arr": arr,
        "total_revenue_12mo": total_revenue,
        "avg_mrr": total_revenue / months if months > 0 else 0,
        "final_customer_count": sum(cumulative_customers.values()),
        "churn_impact": {
            "initial_customers": sum(monthly_customers_by_tier.values()),
            "final_customers": sum(cumulative_customers.values()),
            "churned_customers": sum(monthly_customers_by_tier.values())
            - sum(cumulative_customers.values()),
        },
    }
