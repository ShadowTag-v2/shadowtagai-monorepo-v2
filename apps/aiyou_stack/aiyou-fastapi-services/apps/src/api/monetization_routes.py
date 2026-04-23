"""FastAPI routes for monetization and billing.

Endpoints:
- GET / - Landing page
- GET /api/pricing - Get pricing plans
- POST /api/billing/create-checkout-session - Create Stripe checkout
- POST /api/billing/create-portal-session - Create customer portal
- POST /api/webhooks/stripe - Stripe webhook handler
- GET /api/billing/usage - Get current usage stats
- GET /api/billing/subscription - Get subscription details
- GET /api/revenue/analytics - Revenue analytics (admin)
"""

import logging

from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from src.monetization import (
    PRICING_PLANS,
    PricingTier,
    get_stripe_integration,
    get_usage_tracker,
)
from src.monetization.landing_page import generate_landing_page

logger = logging.getLogger(__name__)

router = APIRouter(tags=["monetization"])
billing_router = APIRouter(prefix="/api/billing", tags=["billing"])
webhook_router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])
revenue_router = APIRouter(prefix="/api/revenue", tags=["revenue"])


# Request/Response models
class CreateCheckoutRequest(BaseModel):
    """Create checkout session request."""

    tier: str
    success_url: str
    cancel_url: str
    billing_period: str = "monthly"  # monthly or annual


class CreatePortalRequest(BaseModel):
    """Create customer portal session request."""

    customer_id: str
    return_url: str


class UsageResponse(BaseModel):
    """Usage statistics response."""

    customer_id: str
    tier: str
    usage: dict
    limits: dict
    overages: dict


class SubscriptionResponse(BaseModel):
    """Subscription details response."""

    customer_id: str
    tier: str
    status: str
    current_period_start: str
    current_period_end: str
    cancel_at_period_end: bool


# Landing page
@router.get("/", response_class=HTMLResponse)
async def get_landing_page():
    """Serve the landing page with pricing and signup.

    Returns complete HTML page with:
    - Hero section
    - Feature showcase
    - Pricing tables
    - ROI calculator
    - Stripe checkout integration
    """
    # In production, get from environment variables
    stripe_publishable_key = "pk_test_..."  # Placeholder
    custom_domain = "intelligence.shadowtag_v4.dev"

    html = generate_landing_page(
        stripe_publishable_key=stripe_publishable_key,
        custom_domain=custom_domain,
    )

    return HTMLResponse(content=html)


# Pricing
@router.get("/api/pricing")
async def get_pricing_plans():
    """Get all pricing plans.

    Returns detailed pricing information for all tiers.
    """
    return {
        "plans": {
            tier.value: {
                "name": tier.value.title(),
                "price_monthly": plan.price_monthly,
                "price_annual": plan.price_annual,
                "max_sources": plan.max_sources,
                "max_items_per_day": plan.max_items_per_day,
                "features": {
                    "visualizations": plan.visualizations,
                    "ml_anomaly_detection": plan.ml_anomaly_detection,
                    "priority_support": plan.priority_support,
                    "custom_integrations": plan.custom_integrations,
                    "sla_guarantee": plan.sla_guarantee,
                },
            }
            for tier, plan in PRICING_PLANS.items()
        },
        "currency": "USD",
        "billing_periods": ["monthly", "annual"],
        "annual_discount": "2 months free",
    }


# Checkout
@billing_router.post("/create-checkout-session")
async def create_checkout_session(request: CreateCheckoutRequest):
    """Create Stripe checkout session for subscription.

    Body:
    - tier: Pricing tier (starter, professional, enterprise)
    - success_url: URL to redirect after successful payment
    - cancel_url: URL to redirect if user cancels
    - billing_period: monthly or annual

    Returns:
    - checkout_url: URL to redirect user to Stripe checkout
    - session_id: Checkout session ID

    """
    try:
        tier_enum = PricingTier[request.tier.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid tier: {request.tier}") from None

    stripe = get_stripe_integration()

    try:
        session = await stripe.create_checkout_session(
            tier=tier_enum,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            billing_period=request.billing_period,
        )

        return {
            "checkout_url": session.get("url"),
            "session_id": session.get("id"),
        }

    except Exception as e:
        logger.error(f"Failed to create checkout session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create checkout session") from e


@billing_router.post("/create-portal-session")
async def create_portal_session(request: CreatePortalRequest):
    """Create Stripe customer portal session.

    Allows customers to:
    - Update payment methods
    - View invoices
    - Cancel subscription
    - Update billing info

    Body:
    - customer_id: Stripe customer ID
    - return_url: URL to return to after portal session

    Returns:
    - portal_url: URL to redirect user to customer portal

    """
    stripe = get_stripe_integration()

    try:
        session = await stripe.create_portal_session(
            customer_id=request.customer_id,
            return_url=request.return_url,
        )

        return {
            "portal_url": session.get("url"),
        }

    except Exception as e:
        logger.error(f"Failed to create portal session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create portal session") from e


# Usage tracking
@billing_router.get("/usage", response_model=UsageResponse)
async def get_usage_stats(customer_id: str):
    """Get current usage statistics for a customer.

    Query parameters:
    - customer_id: Customer ID

    Returns:
    - Current usage (sources, items, API calls)
    - Plan limits
    - Any overages

    """
    tracker = get_usage_tracker()

    try:
        stats = tracker.get_usage_stats()
        tier = tracker.get_customer_tier(customer_id)

        plan = PRICING_PLANS.get(tier)
        if not plan:
            raise HTTPException(status_code=404, detail="Customer plan not found")

        # Calculate overages
        overages = {}
        if stats["sources_used"] > plan.max_sources:
            overages["sources"] = stats["sources_used"] - plan.max_sources

        if stats["items_collected_today"] > plan.max_items_per_day:
            overages["items"] = stats["items_collected_today"] - plan.max_items_per_day

        return UsageResponse(
            customer_id=customer_id,
            tier=tier.value,
            usage=stats,
            limits={
                "max_sources": plan.max_sources,
                "max_items_per_day": plan.max_items_per_day,
            },
            overages=overages,
        )

    except Exception as e:
        logger.error(f"Failed to get usage stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get usage stats") from e


@billing_router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(customer_id: str):
    """Get subscription details for a customer.

    Query parameters:
    - customer_id: Customer ID

    Returns:
    - Subscription status
    - Current period
    - Cancellation status

    """
    stripe = get_stripe_integration()

    try:
        subscription = await stripe.get_subscription(customer_id)

        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")

        return SubscriptionResponse(
            customer_id=customer_id,
            tier=subscription.get("tier", "free"),
            status=subscription.get("status", "unknown"),
            current_period_start=subscription.get("current_period_start", ""),
            current_period_end=subscription.get("current_period_end", ""),
            cancel_at_period_end=subscription.get("cancel_at_period_end", False),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to get subscription") from e


# Webhooks
@webhook_router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str | None = Header(None, alias="stripe-signature"),
):
    """Stripe webhook handler.

    Handles events:
    - checkout.session.completed - New subscription
    - customer.subscription.updated - Subscription changed
    - customer.subscription.deleted - Subscription cancelled
    - invoice.payment_succeeded - Payment successful
    - invoice.payment_failed - Payment failed

    Stripe will send webhook signature in header for verification.
    """
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing Stripe signature")

    payload = await request.body()
    stripe = get_stripe_integration()

    try:
        await stripe.handle_webhook(payload.decode(), stripe_signature)
        return {"status": "success"}

    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e


# Revenue analytics (admin only)
@revenue_router.get("/analytics")
async def get_revenue_analytics():
    """Get revenue analytics (admin only).

    Returns:
    - MRR (Monthly Recurring Revenue)
    - ARR (Annual Recurring Revenue)
    - Revenue by tier
    - Growth metrics
    - Customer counts
    - Churn rate

    """
    stripe = get_stripe_integration()

    try:
        analytics = await stripe.get_revenue_analytics()
        return analytics

    except Exception as e:
        logger.error(f"Failed to get revenue analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get revenue analytics") from e


@revenue_router.get("/projections")
async def get_revenue_projections():
    """Get revenue projections (admin only).

    Returns:
    - 12-month revenue projection
    - Expected customer growth
    - Churn estimates
    - Target metrics

    """
    stripe = get_stripe_integration()

    try:
        projections = stripe.project_revenue()
        return projections

    except Exception as e:
        logger.error(f"Failed to get revenue projections: {e}")
        raise HTTPException(status_code=500, detail="Failed to get revenue projections") from e


# Include all routers
def include_monetization_routes(app):
    """Include all monetization routes in FastAPI app."""
    app.include_router(router)
    app.include_router(billing_router)
    app.include_router(webhook_router)
    app.include_router(revenue_router)
