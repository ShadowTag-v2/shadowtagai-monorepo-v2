# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Stripe Billing Integration

Provides payment processing and subscription management:
- Customer management
- Subscription plans (usage-based + tiered)
- Usage metering for V2X fleet
- Webhook handling
- Invoice generation
- Payment method management

Plans:
- Starter: $11/vehicle/month (1-100 vehicles)
- Growth: $9/vehicle/month (101-500 vehicles)
- Enterprise: $7/vehicle/month (500+ vehicles)
"""

import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

import stripe

# Initialize Stripe (use environment variable)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_placeholder")


class SubscriptionTier(Enum):
    """Subscription tier levels"""

    STARTER = "starter"  # 1-100 vehicles
    GROWTH = "growth"  # 101-500 vehicles
    ENTERPRISE = "enterprise"  # 500+ vehicles


class BillingInterval(Enum):
    """Billing interval options"""

    MONTHLY = "month"
    YEARLY = "year"


@dataclass
class PricingPlan:
    """Pricing plan configuration"""

    tier: SubscriptionTier
    name: str
    price_per_vehicle: float
    min_vehicles: int
    max_vehicles: int | None
    features: list[str]
    stripe_price_id: str | None = None


# Pricing configuration
PRICING_PLANS = {
    SubscriptionTier.STARTER: PricingPlan(
        tier=SubscriptionTier.STARTER,
        name="Starter Plan",
        price_per_vehicle=11.0,
        min_vehicles=1,
        max_vehicles=100,
        features=[
            "V2X Mesh Network Access",
            "Real-time Traffic Intelligence",
            "Basic Analytics Dashboard",
            "Email Support",
            "99.5% Uptime SLA",
        ],
    ),
    SubscriptionTier.GROWTH: PricingPlan(
        tier=SubscriptionTier.GROWTH,
        name="Growth Plan",
        price_per_vehicle=9.0,
        min_vehicles=101,
        max_vehicles=500,
        features=[
            "All Starter features",
            "Advanced Analytics",
            "Custom Integrations",
            "Priority Support",
            "99.9% Uptime SLA",
            "Dedicated Account Manager",
        ],
    ),
    SubscriptionTier.ENTERPRISE: PricingPlan(
        tier=SubscriptionTier.ENTERPRISE,
        name="Enterprise Plan",
        price_per_vehicle=7.0,
        min_vehicles=501,
        max_vehicles=None,
        features=[
            "All Growth features",
            "White-label Options",
            "Custom SLA",
            "24/7 Phone Support",
            "99.99% Uptime SLA",
            "On-premise Deployment Option",
            "Volume Discounts Available",
        ],
    ),
}


class StripeBillingService:
    """Stripe billing integration service

    Handles all payment operations including:
    - Customer lifecycle
    - Subscription management
    - Usage tracking
    - Invoice generation
    """

    def __init__(self):
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_placeholder")

    # Customer Management
    async def create_customer(
        self,
        email: str,
        name: str,
        metadata: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Create a new Stripe customer

        Args:
            email: Customer email
            name: Customer name
            metadata: Additional metadata (e.g., company, fleet_size)

        Returns:
            Customer object with id and details

        """
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {},
                description=f"PNKLN V2X Platform - {name}",
            )

            return {
                "customer_id": customer.id,
                "email": customer.email,
                "name": customer.name,
                "created": datetime.fromtimestamp(customer.created).isoformat(),
            }
        except stripe.error.StripeError as e:
            return {"error": str(e)}

    async def get_customer(self, customer_id: str) -> dict[str, Any]:
        """Retrieve customer details"""
        try:
            customer = stripe.Customer.retrieve(customer_id)
            return {
                "customer_id": customer.id,
                "email": customer.email,
                "name": customer.name,
                "balance": customer.balance,
                "currency": customer.currency or "usd",
                "metadata": customer.metadata,
            }
        except stripe.error.StripeError as e:
            return {"error": str(e)}

    async def update_customer(
        self,
        customer_id: str,
        email: str | None = None,
        name: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Update customer information"""
        try:
            update_data = {}
            if email:
                update_data["email"] = email
            if name:
                update_data["name"] = name
            if metadata:
                update_data["metadata"] = metadata

            customer = stripe.Customer.modify(customer_id, **update_data)
            return {"customer_id": customer.id, "updated": True}
        except stripe.error.StripeError as e:
            return {"error": str(e)}

    # Payment Method Management
    async def attach_payment_method(
        self,
        customer_id: str,
        payment_method_id: str,
    ) -> dict[str, Any]:
        """Attach payment method to customer"""
        try:
            # Attach payment method
            payment_method = stripe.PaymentMethod.attach(payment_method_id, customer=customer_id)

            # Set as default
            stripe.Customer.modify(
                customer_id,
                invoice_settings={"default_payment_method": payment_method_id},
            )

            return {
                "payment_method_id": payment_method.id,
                "type": payment_method.type,
                "attached": True,
            }
        except stripe.error.StripeError as e:
            return {"error": str(e)}

    # Subscription Management
    async def create_subscription(
        self,
        customer_id: str,
        vehicle_count: int,
        billing_interval: BillingInterval = BillingInterval.MONTHLY,
    ) -> dict[str, Any]:
        """Create a usage-based subscription

        Automatically selects appropriate tier based on vehicle count
        """
        try:
            # Determine tier
            tier = self._determine_tier(vehicle_count)
            plan = PRICING_PLANS[tier]

            # Calculate pricing
            base_amount = int(plan.price_per_vehicle * vehicle_count * 100)  # cents

            # Create subscription
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": f"PNKLN V2X Platform - {plan.name}",
                                "description": f"V2X mesh network access for {vehicle_count} vehicles",
                            },
                            "recurring": {"interval": billing_interval.value},
                            "unit_amount": int(plan.price_per_vehicle * 100),
                        },
                        "quantity": vehicle_count,
                    },
                ],
                metadata={
                    "tier": tier.value,
                    "vehicle_count": str(vehicle_count),
                    "platform": "pnkln-v2x",
                },
                payment_behavior="default_incomplete",
                payment_settings={"save_default_payment_method": "on_subscription"},
                expand=["latest_invoice.payment_intent"],
            )

            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "tier": tier.value,
                "vehicle_count": vehicle_count,
                "amount_per_period": base_amount / 100,
                "billing_interval": billing_interval.value,
                "current_period_start": datetime.fromtimestamp(
                    subscription.current_period_start,
                ).isoformat(),
                "current_period_end": datetime.fromtimestamp(
                    subscription.current_period_end,
                ).isoformat(),
                "client_secret": subscription.latest_invoice.payment_intent.client_secret
                if subscription.latest_invoice
                else None,
            }
        except stripe.error.StripeError as e:
            return {"error": str(e)}

    async def update_subscription_quantity(
        self,
        subscription_id: str,
        new_vehicle_count: int,
    ) -> dict[str, Any]:
        """Update subscription quantity (vehicle count)

        Handles tier changes automatically
        """
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)

            # Check if tier should change
            current_tier = SubscriptionTier(subscription.metadata.get("tier"))
            new_tier = self._determine_tier(new_vehicle_count)

            # Update subscription
            updated_subscription = stripe.Subscription.modify(
                subscription_id,
                items=[{"id": subscription["items"]["data"][0].id, "quantity": new_vehicle_count}],
                metadata={"tier": new_tier.value, "vehicle_count": str(new_vehicle_count)},
                proration_behavior="always_invoice",
            )

            tier_changed = current_tier != new_tier

            return {
                "subscription_id": updated_subscription.id,
                "status": updated_subscription.status,
                "vehicle_count": new_vehicle_count,
                "tier": new_tier.value,
                "tier_changed": tier_changed,
                "previous_tier": current_tier.value if tier_changed else None,
            }
        except stripe.error.StripeError as e:
            return {"error": str(e)}

    async def cancel_subscription(
        self,
        subscription_id: str,
        immediate: bool = False,
    ) -> dict[str, Any]:
        """Cancel a subscription

        Args:
            subscription_id: Stripe subscription ID
            immediate: If True, cancel immediately. If False, cancel at period end.

        """
        try:
            if immediate:
                subscription = stripe.Subscription.delete(subscription_id)
            else:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True,
                )

            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "canceled": True,
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "canceled_at": datetime.fromtimestamp(subscription.canceled_at).isoformat()
                if subscription.canceled_at
                else None,
            }
        except stripe.error.StripeError as e:
            return {"error": str(e)}

    async def get_subscription(self, subscription_id: str) -> dict[str, Any]:
        """Retrieve subscription details"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)

            return {
                "subscription_id": subscription.id,
                "customer_id": subscription.customer,
                "status": subscription.status,
                "tier": subscription.metadata.get("tier"),
                "vehicle_count": int(subscription.metadata.get("vehicle_count", 0)),
                "current_period_start": datetime.fromtimestamp(
                    subscription.current_period_start,
                ).isoformat(),
                "current_period_end": datetime.fromtimestamp(
                    subscription.current_period_end,
                ).isoformat(),
                "cancel_at_period_end": subscription.cancel_at_period_end,
            }
        except stripe.error.StripeError as e:
            return {"error": str(e)}

    # Usage Tracking (Metered Billing)
    async def record_usage(
        self,
        subscription_item_id: str,
        quantity: int,
        timestamp: int | None = None,
        action: str = "increment",
    ) -> dict[str, Any]:
        """Record usage for metered billing

        Useful for tracking additional usage beyond base subscription
        (e.g., API calls, data transfer)
        """
        try:
            usage_record = stripe.SubscriptionItem.create_usage_record(
                subscription_item_id,
                quantity=quantity,
                timestamp=timestamp or int(datetime.now().timestamp()),
                action=action,
            )

            return {
                "usage_record_id": usage_record.id,
                "quantity": usage_record.quantity,
                "timestamp": datetime.fromtimestamp(usage_record.timestamp).isoformat(),
            }
        except stripe.error.StripeError as e:
            return {"error": str(e)}

    # Invoice Management
    async def get_upcoming_invoice(self, customer_id: str) -> dict[str, Any]:
        """Retrieve upcoming invoice preview"""
        try:
            invoice = stripe.Invoice.upcoming(customer=customer_id)

            return {
                "amount_due": invoice.amount_due / 100,
                "currency": invoice.currency,
                "period_start": datetime.fromtimestamp(invoice.period_start).isoformat(),
                "period_end": datetime.fromtimestamp(invoice.period_end).isoformat(),
                "lines": [
                    {
                        "description": line.description,
                        "amount": line.amount / 100,
                        "quantity": line.quantity,
                    }
                    for line in invoice.lines.data
                ],
            }
        except stripe.error.StripeError as e:
            return {"error": str(e)}

    async def list_invoices(self, customer_id: str, limit: int = 10) -> dict[str, Any]:
        """List customer invoices"""
        try:
            invoices = stripe.Invoice.list(customer=customer_id, limit=limit)

            return {
                "invoices": [
                    {
                        "invoice_id": inv.id,
                        "amount_paid": inv.amount_paid / 100,
                        "amount_due": inv.amount_due / 100,
                        "status": inv.status,
                        "created": datetime.fromtimestamp(inv.created).isoformat(),
                        "invoice_pdf": inv.invoice_pdf,
                    }
                    for inv in invoices.data
                ],
            }
        except stripe.error.StripeError as e:
            return {"error": str(e)}

    # Webhook Handling
    def verify_webhook_signature(self, payload: bytes, signature: str) -> dict[str, Any] | None:
        """Verify webhook signature and return event

        Security: Prevents spoofed webhooks
        """
        try:
            event = stripe.Webhook.construct_event(payload, signature, self.webhook_secret)
            return event
        except ValueError:
            return None
        except stripe.error.SignatureVerificationError:
            return None

    async def handle_webhook_event(self, event: dict[str, Any]) -> dict[str, Any]:
        """Process webhook events

        Handles:
        - payment_intent.succeeded
        - payment_intent.payment_failed
        - customer.subscription.created
        - customer.subscription.updated
        - customer.subscription.deleted
        - invoice.payment_succeeded
        - invoice.payment_failed
        """
        event_type = event["type"]
        data = event["data"]["object"]

        handlers = {
            "payment_intent.succeeded": self._handle_payment_succeeded,
            "payment_intent.payment_failed": self._handle_payment_failed,
            "customer.subscription.created": self._handle_subscription_created,
            "customer.subscription.updated": self._handle_subscription_updated,
            "customer.subscription.deleted": self._handle_subscription_deleted,
            "invoice.payment_succeeded": self._handle_invoice_paid,
            "invoice.payment_failed": self._handle_invoice_failed,
        }

        handler = handlers.get(event_type)
        if handler:
            return await handler(data)

        return {"status": "unhandled_event", "type": event_type}

    # Private helper methods
    def _determine_tier(self, vehicle_count: int) -> SubscriptionTier:
        """Determine subscription tier based on vehicle count"""
        if vehicle_count <= 100:
            return SubscriptionTier.STARTER
        if vehicle_count <= 500:
            return SubscriptionTier.GROWTH
        return SubscriptionTier.ENTERPRISE

    async def _handle_payment_succeeded(self, data: dict) -> dict[str, Any]:
        """Handle successful payment"""
        # Log payment success, update internal records
        return {
            "status": "payment_succeeded",
            "payment_intent_id": data["id"],
            "amount": data["amount"] / 100,
        }

    async def _handle_payment_failed(self, data: dict) -> dict[str, Any]:
        """Handle failed payment"""
        # Send alert, notify customer
        return {
            "status": "payment_failed",
            "payment_intent_id": data["id"],
            "error_message": data.get("last_payment_error", {}).get("message"),
        }

    async def _handle_subscription_created(self, data: dict) -> dict[str, Any]:
        """Handle new subscription"""
        # Provision access, send welcome email
        return {
            "status": "subscription_created",
            "subscription_id": data["id"],
            "customer_id": data["customer"],
        }

    async def _handle_subscription_updated(self, data: dict) -> dict[str, Any]:
        """Handle subscription update"""
        # Update access level, notify of changes
        return {
            "status": "subscription_updated",
            "subscription_id": data["id"],
            "status_detail": data["status"],
        }

    async def _handle_subscription_deleted(self, data: dict) -> dict[str, Any]:
        """Handle subscription cancellation"""
        # Revoke access, send cancellation email
        return {
            "status": "subscription_deleted",
            "subscription_id": data["id"],
            "canceled_at": data.get("canceled_at"),
        }

    async def _handle_invoice_paid(self, data: dict) -> dict[str, Any]:
        """Handle successful invoice payment"""
        # Update payment records, send receipt
        return {
            "status": "invoice_paid",
            "invoice_id": data["id"],
            "amount_paid": data["amount_paid"] / 100,
        }

    async def _handle_invoice_failed(self, data: dict) -> dict[str, Any]:
        """Handle failed invoice payment"""
        # Send dunning email, retry payment
        return {
            "status": "invoice_failed",
            "invoice_id": data["id"],
            "attempt_count": data.get("attempt_count", 0),
        }

    # Reporting
    async def get_revenue_report(self, start_date: datetime, end_date: datetime) -> dict[str, Any]:
        """Generate revenue report for date range

        Returns MRR, ARR, churn, growth metrics
        """
        try:
            # Get all charges in date range
            charges = stripe.Charge.list(
                created={"gte": int(start_date.timestamp()), "lte": int(end_date.timestamp())},
                limit=100,
            )

            total_revenue = sum(charge.amount for charge in charges.data if charge.paid) / 100

            # Get active subscriptions
            subscriptions = stripe.Subscription.list(status="active", limit=100)
            mrr = (
                sum(
                    sub.items.data[0].price.unit_amount * sub.items.data[0].quantity
                    for sub in subscriptions.data
                )
                / 100
            )

            return {
                "period_start": start_date.isoformat(),
                "period_end": end_date.isoformat(),
                "total_revenue": total_revenue,
                "mrr": mrr,
                "arr": mrr * 12,
                "active_subscriptions": len(subscriptions.data),
                "average_vehicle_count": sum(
                    int(sub.metadata.get("vehicle_count", 0)) for sub in subscriptions.data
                )
                / len(subscriptions.data)
                if subscriptions.data
                else 0,
            }
        except stripe.error.StripeError as e:
            return {"error": str(e)}


# Pricing calculator utility
def calculate_pricing(vehicle_count: int) -> dict[str, Any]:
    """Calculate pricing for a given vehicle count

    Returns tier, monthly cost, yearly cost with discount
    """
    service = StripeBillingService()
    tier = service._determine_tier(vehicle_count)
    plan = PRICING_PLANS[tier]

    monthly_cost = plan.price_per_vehicle * vehicle_count
    yearly_cost = monthly_cost * 12 * 0.85  # 15% annual discount

    return {
        "tier": tier.value,
        "plan_name": plan.name,
        "vehicle_count": vehicle_count,
        "price_per_vehicle": plan.price_per_vehicle,
        "monthly_cost": monthly_cost,
        "yearly_cost": yearly_cost,
        "yearly_savings": (monthly_cost * 12) - yearly_cost,
        "features": plan.features,
    }
