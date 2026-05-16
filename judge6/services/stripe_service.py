# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Stripe Billing Service
Handles subscription management, payments, webhooks
"""

import stripe
from typing import Any
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from ..core.config import settings
from ..models.database import User, SubscriptionTier


# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
  """Stripe billing and subscription management"""

  # Price mapping (set these in .env after creating in Stripe Dashboard)
  PRICE_IDS = {
    "starter_monthly": settings.STRIPE_PRICE_STARTER_MONTHLY,
    "starter_annual": settings.STRIPE_PRICE_STARTER_ANNUAL,
    "professional_monthly": settings.STRIPE_PRICE_PROFESSIONAL_MONTHLY,
    "professional_annual": settings.STRIPE_PRICE_PROFESSIONAL_ANNUAL,
  }

  @staticmethod
  def create_customer(
    email: str,
    name: str | None = None,
    metadata: dict[str, str] | None = None,
  ) -> stripe.Customer:
    """
    Create a Stripe customer
    Call this when user registers
    """
    customer = stripe.Customer.create(
      email=email,
      name=name,
      metadata=metadata or {},
    )
    return customer

  @staticmethod
  def create_checkout_session(
    customer_id: str,
    price_id: str,
    success_url: str,
    cancel_url: str,
    metadata: dict[str, str] | None = None,
  ) -> stripe.checkout.Session:
    """
    Create a Stripe Checkout session for subscription
    Redirect user to session.url to complete payment
    """
    session = stripe.checkout.Session.create(
      customer=customer_id,
      mode="subscription",
      line_items=[{"price": price_id, "quantity": 1}],
      success_url=success_url,
      cancel_url=cancel_url,
      metadata=metadata or {},
      allow_promotion_codes=True,  # Enable promo codes
      billing_address_collection="required",
    )
    return session

  @staticmethod
  def create_portal_session(
    customer_id: str, return_url: str
  ) -> stripe.billing_portal.Session:
    """
    Create a Stripe Customer Portal session
    Allows customer to manage subscription, update payment method, view invoices
    """
    session = stripe.billing_portal.Session.create(
      customer=customer_id,
      return_url=return_url,
    )
    return session

  @staticmethod
  def get_subscription(subscription_id: str) -> stripe.Subscription:
    """Get subscription details"""
    return stripe.Subscription.retrieve(subscription_id)

  @staticmethod
  def cancel_subscription(
    subscription_id: str, at_period_end: bool = True
  ) -> stripe.Subscription:
    """
    Cancel subscription
    If at_period_end=True, cancels at end of billing period
    If False, cancels immediately
    """
    return stripe.Subscription.modify(
      subscription_id,
      cancel_at_period_end=at_period_end,
    )

  @staticmethod
  def update_subscription(
    subscription_id: str, new_price_id: str
  ) -> stripe.Subscription:
    """
    Upgrade/downgrade subscription
    Changes take effect immediately with prorated billing
    """
    subscription = stripe.Subscription.retrieve(subscription_id)

    return stripe.Subscription.modify(
      subscription_id,
      items=[
        {
          "id": subscription["items"]["data"][0].id,
          "price": new_price_id,
        }
      ],
      proration_behavior="always_invoice",  # Prorate immediately
    )

  @staticmethod
  def handle_webhook_event(payload: bytes, sig_header: str) -> dict[str, Any]:
    """
    Verify and parse Stripe webhook
    Call this from webhook endpoint
    """
    try:
      event = stripe.Webhook.construct_event(
        payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
      )
      return event
    except ValueError:
      # Invalid payload
      raise ValueError("Invalid webhook payload")
    except stripe.error.SignatureVerificationError:
      # Invalid signature
      raise ValueError("Invalid webhook signature")

  @staticmethod
  def process_subscription_created(event_data: dict[str, Any], db: Session) -> None:
    """
    Process checkout.session.completed event
    Updates user's subscription tier
    """
    session = event_data["object"]
    customer_id = session.get("customer")
    subscription_id = session.get("subscription")

    # Get user by Stripe customer ID
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()

    if not user:
      print(f"Warning: No user found for Stripe customer {customer_id}")
      return

    # Get subscription details to determine tier
    subscription = stripe.Subscription.retrieve(subscription_id)
    price_id = subscription["items"]["data"][0]["price"]["id"]

    # Map price ID to tier
    tier = StripeService._get_tier_from_price_id(price_id)

    # Update user
    user.stripe_subscription_id = subscription_id
    user.tier = tier
    user.monthly_request_limit = StripeService._get_limit_for_tier(tier)

    db.commit()

    print(f"User {user.email} upgraded to {tier.value}")

  @staticmethod
  def process_subscription_updated(event_data: dict[str, Any], db: Session) -> None:
    """
    Process customer.subscription.updated event
    Handles upgrades, downgrades, cancellations
    """
    subscription = event_data["object"]
    subscription_id = subscription["id"]
    status = subscription["status"]

    # Get user by subscription ID
    user = db.query(User).filter(User.stripe_subscription_id == subscription_id).first()

    if not user:
      print(f"Warning: No user found for subscription {subscription_id}")
      return

    if status == "canceled":
      # Downgrade to free
      user.tier = SubscriptionTier.FREE
      user.monthly_request_limit = settings.RATE_LIMIT_FREE
      user.stripe_subscription_id = None
      print(f"User {user.email} downgraded to FREE (canceled)")

    elif status == "active":
      # Update tier based on price
      price_id = subscription["items"]["data"][0]["price"]["id"]
      tier = StripeService._get_tier_from_price_id(price_id)
      user.tier = tier
      user.monthly_request_limit = StripeService._get_limit_for_tier(tier)
      print(f"User {user.email} subscription updated to {tier.value}")

    db.commit()

  @staticmethod
  def process_payment_failed(event_data: dict[str, Any], db: Session) -> None:
    """
    Process invoice.payment_failed event
    Notify user, potentially downgrade after grace period
    """
    invoice = event_data["object"]
    customer_id = invoice["customer"]

    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()

    if user:
      # TODO: Send email notification
      # TODO: Implement grace period logic
      print(f"Payment failed for user {user.email}")

  @staticmethod
  def _get_tier_from_price_id(price_id: str) -> SubscriptionTier:
    """Map Stripe price ID to subscription tier"""
    if price_id in [
      settings.STRIPE_PRICE_STARTER_MONTHLY,
      settings.STRIPE_PRICE_STARTER_ANNUAL,
    ]:
      return SubscriptionTier.STARTER
    elif price_id in [
      settings.STRIPE_PRICE_PROFESSIONAL_MONTHLY,
      settings.STRIPE_PRICE_PROFESSIONAL_ANNUAL,
    ]:
      return SubscriptionTier.PROFESSIONAL
    else:
      return SubscriptionTier.FREE

  @staticmethod
  def _get_limit_for_tier(tier: SubscriptionTier) -> int:
    """Get request limit for tier"""
    limits = {
      SubscriptionTier.FREE: settings.RATE_LIMIT_FREE,
      SubscriptionTier.STARTER: settings.RATE_LIMIT_STARTER,
      SubscriptionTier.PROFESSIONAL: settings.RATE_LIMIT_PROFESSIONAL,
      SubscriptionTier.ENTERPRISE: settings.RATE_LIMIT_ENTERPRISE,
    }
    return limits.get(tier, settings.RATE_LIMIT_FREE)

  @staticmethod
  def create_usage_record(
    subscription_item_id: str,
    quantity: int,
    timestamp: int | None = None,
  ) -> stripe.UsageRecord:
    """
    Create usage record for metered billing
    Use this if you implement pay-per-request overage charges
    """
    return stripe.UsageRecord.create(
      subscription_item=subscription_item_id,
      quantity=quantity,
      timestamp=timestamp or int(datetime.now(timezone.utc).timestamp()),
      action="increment",
    )

  @staticmethod
  def get_upcoming_invoice(customer_id: str) -> stripe.Invoice:
    """
    Get upcoming invoice for customer
    Use this to show "Your next bill will be $X"
    """
    return stripe.Invoice.upcoming(customer=customer_id)
