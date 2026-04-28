# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Payment Service (Stripe Integration)

Revenue:
- Stripe subscription management
- Payment processing
- Webhook handling
"""

from typing import Any

import stripe
from stripe.error import StripeError

from app.core.config import get_settings
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

# Initialize Stripe
if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentService:
    """Stripe payment service

    Revenue Features:
    - Create customers
    - Create subscriptions
    - Process payments
    - Handle webhooks
    - Manage billing
    """

    @staticmethod
    async def create_customer(
        email: str,
        name: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> str | None:
        """Create Stripe customer

        Args:
            email: Customer email
            name: Customer name
            metadata: Additional metadata

        Returns:
            Stripe customer ID or None on error

        """
        try:
            customer = stripe.Customer.create(email=email, name=name, metadata=metadata or {})
            logger.info("stripe_customer_created", customer_id=customer.id, email=email)
            return customer.id

        except StripeError as e:
            logger.error("stripe_customer_creation_failed", error=str(e))
            return None

    @staticmethod
    async def create_subscription(
        customer_id: str,
        price_id: str,
        payment_method_id: str,
        trial_days: int | None = None,
    ) -> dict[str, Any] | None:
        """Create Stripe subscription

        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID (for the tier)
            payment_method_id: Payment method ID
            trial_days: Trial period in days

        Returns:
            Subscription data or None on error

        """
        try:
            # Attach payment method to customer
            stripe.PaymentMethod.attach(payment_method_id, customer=customer_id)

            # Set as default payment method
            stripe.Customer.modify(
                customer_id,
                invoice_settings={"default_payment_method": payment_method_id},
            )

            # Create subscription
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                trial_period_days=trial_days,
                expand=["latest_invoice.payment_intent"],
            )

            logger.info(
                "stripe_subscription_created",
                subscription_id=subscription.id,
                customer_id=customer_id,
            )

            return {
                "id": subscription.id,
                "status": subscription.status,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end,
                "trial_start": subscription.trial_start,
                "trial_end": subscription.trial_end,
            }

        except StripeError as e:
            logger.error("stripe_subscription_creation_failed", error=str(e))
            return None

    @staticmethod
    async def cancel_subscription(subscription_id: str, at_period_end: bool = True) -> bool:
        """Cancel Stripe subscription

        Args:
            subscription_id: Stripe subscription ID
            at_period_end: Cancel at period end (True) or immediately (False)

        Returns:
            Success status

        """
        try:
            if at_period_end:
                stripe.Subscription.modify(subscription_id, cancel_at_period_end=True)
            else:
                stripe.Subscription.delete(subscription_id)

            logger.info(
                "stripe_subscription_canceled",
                subscription_id=subscription_id,
                at_period_end=at_period_end,
            )
            return True

        except StripeError as e:
            logger.error("stripe_subscription_cancellation_failed", error=str(e))
            return False

    @staticmethod
    async def verify_webhook_signature(payload: bytes, signature: str) -> dict[str, Any] | None:
        """Verify Stripe webhook signature

        Security:
        - Prevents webhook spoofing
        - Ensures events are from Stripe

        Args:
            payload: Webhook payload
            signature: Stripe signature header

        Returns:
            Event data or None if verification fails

        """
        try:
            event = stripe.Webhook.construct_event(
                payload,
                signature,
                settings.STRIPE_WEBHOOK_SECRET,
            )
            return event

        except ValueError:
            logger.error("webhook_invalid_payload")
            return None
        except stripe.error.SignatureVerificationError:
            logger.error("webhook_invalid_signature")
            return None


# Global payment service instance
payment_service = PaymentService()
