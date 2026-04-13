"""
KovelAI Stripe Connect Module — Payment Routing Engine

Track A: Client CC → Stripe Connect → Lawyer's Bank Account
Track B: Lawyer's firm card → KovelAI Monthly SaaS Tier

Per ABA Model Rule 5.4:
    We NEVER split fees with the lawyer. The client pays the lawyer
    directly via Stripe Connect. We are a SaaS vendor to the firm,
    billing separately on Track B.

Usage:
    from api.stripe_connect import StripeConnect

    # Onboard a new law firm
    account = StripeConnect.create_connected_account("Smith & Associates", "smith@firm.com")

    # Bill client per-query
    payment = StripeConnect.bill_client_query(
        lawyer_account_id=account["account_id"],
        rate_cents=250,
        client_payment_method="pm_xxx",
        session_id="seu_xxx",
    )
"""

from __future__ import annotations

import logging
import os
from typing import Optional

logger = logging.getLogger("kovelai.stripe")

# Stripe SDK — graceful fallback if not installed
try:
    import stripe

    stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_AVAILABLE = bool(stripe.api_key)
except ImportError:
    stripe = None  # type: ignore[assignment]
    STRIPE_AVAILABLE = False


WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")


class StripeConnect:
    """Stripe Connect integration for KovelAI dual-billing model."""

    # ── Track A: Client → Lawyer (Express Connect) ─────

    @staticmethod
    def create_connected_account(
        firm_name: str,
        email: str,
        country: str = "US",
    ) -> dict:
        """
        Create a Stripe Express Connected Account for a law firm.
        The firm completes KYC through Stripe's hosted onboarding.

        Returns:
            dict with account_id and onboarding status
        """
        if not STRIPE_AVAILABLE:
            logger.warning("Stripe not configured — returning mock account")
            return {
                "account_id": "acct_mock_" + firm_name.lower().replace(" ", "_"),
                "status": "mock",
                "message": "Set STRIPE_SECRET_KEY to enable live accounts",
            }

        account = stripe.Account.create(
            type="express",
            country=country,
            email=email,
            capabilities={
                "card_payments": {"requested": True},
                "transfers": {"requested": True},
            },
            business_profile={
                "name": firm_name,
                "mcc": "8111",  # Legal Services
                "product_description": "Legal services — client triage and research",
            },
            metadata={
                "platform": "kovelai",
                "firm_name": firm_name,
            },
        )

        logger.info("Created Stripe Connect account %s for %s", account.id, firm_name)
        return {
            "account_id": account.id,
            "status": "created",
            "details_submitted": account.details_submitted,
            "charges_enabled": account.charges_enabled,
        }

    @staticmethod
    def create_account_link(
        account_id: str,
        refresh_url: str = "https://kovelai.com/onboard/refresh",
        return_url: str = "https://kovelai.com/onboard/complete",
    ) -> dict:
        """
        Generate a Stripe-hosted onboarding link for the law firm.
        The firm owner clicks this to complete KYC, add bank info, etc.

        Returns:
            dict with url and expires_at
        """
        if not STRIPE_AVAILABLE:
            return {
                "url": f"https://connect.stripe.com/mock-onboarding/{account_id}",
                "expires_at": "2026-12-31T23:59:59Z",
                "status": "mock",
            }

        link = stripe.AccountLink.create(
            account=account_id,
            refresh_url=refresh_url,
            return_url=return_url,
            type="account_onboarding",
        )

        return {
            "url": link.url,
            "expires_at": link.expires_at,
            "status": "created",
        }

    @staticmethod
    def bill_client_query(
        lawyer_account_id: str,
        rate_cents: int,
        client_payment_method: str,
        session_id: str,
        query_type: str = "ai_chat",
        application_fee_cents: int = 0,
    ) -> dict:
        """
        Bill the client's credit card and route payment DIRECTLY
        to the lawyer's bank via Stripe Connect.

        The application_fee_cents (our take-rate, 0.5% default) is
        captured separately. We never touch the legal fee.

        Args:
            lawyer_account_id: Stripe Connected Account ID (acct_xxx)
            rate_cents: Per-query rate in cents (e.g., 250 = $2.50)
            client_payment_method: Client's saved payment method (pm_xxx)
            session_id: S.E.U. session ID for audit trail
            query_type: ai_chat | web_search | translation | osint
            application_fee_cents: KovelAI platform fee (0.5% default)

        Returns:
            dict with payment_intent_id, status, and routing info
        """
        if not application_fee_cents:
            # Default 0.5% platform fee (minimum 1 cent)
            application_fee_cents = max(1, int(rate_cents * 0.005))

        if not STRIPE_AVAILABLE:
            logger.warning("Stripe not configured — returning mock billing")
            return {
                "payment_intent_id": f"pi_mock_{session_id[:8]}",
                "status": "mock_succeeded",
                "amount_cents": rate_cents,
                "application_fee_cents": application_fee_cents,
                "destination": lawyer_account_id,
                "query_type": query_type,
                "message": "Set STRIPE_SECRET_KEY to enable live billing",
            }

        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=rate_cents,
                currency="usd",
                payment_method=client_payment_method,
                confirm=True,
                application_fee_amount=application_fee_cents,
                transfer_data={
                    "destination": lawyer_account_id,
                },
                metadata={
                    "platform": "kovelai",
                    "session_id": session_id,
                    "query_type": query_type,
                },
                # Anti-fraud: auto return to requires_payment_method on failure
                payment_method_options={
                    "card": {
                        "request_three_d_secure": "automatic",
                    },
                },
            )

            logger.info(
                "Charged %d cents → %s (session: %s)",
                rate_cents,
                lawyer_account_id,
                session_id,
            )

            return {
                "payment_intent_id": payment_intent.id,
                "status": payment_intent.status,
                "amount_cents": rate_cents,
                "application_fee_cents": application_fee_cents,
                "destination": lawyer_account_id,
                "query_type": query_type,
            }

        except stripe.StripeError as e:
            logger.error("Stripe billing failed: %s", str(e))
            return {
                "payment_intent_id": None,
                "status": "failed",
                "error": str(e),
                "amount_cents": rate_cents,
            }

    # ── Track B: Lawyer → KovelAI (Subscription) ───────

    @staticmethod
    def create_firm_subscription(
        firm_email: str,
        tier: str = "starter",
        payment_method: Optional[str] = None,
    ) -> dict:
        """
        Create a KovelAI SaaS subscription for the law firm.
        This is Track B — the firm pays US for platform access.

        Tiers auto-scale based on usage (like Claude Code).
        """
        PRICE_IDS = {
            "starter": os.getenv("STRIPE_PRICE_STARTER", "price_starter_mock"),
            "pro": os.getenv("STRIPE_PRICE_PRO", "price_pro_mock"),
            "sovereign": os.getenv("STRIPE_PRICE_SOVEREIGN", "price_sovereign_mock"),
        }

        price_id = PRICE_IDS.get(tier, PRICE_IDS["starter"])

        if not STRIPE_AVAILABLE:
            return {
                "subscription_id": f"sub_mock_{tier}",
                "status": "mock",
                "tier": tier,
                "price_id": price_id,
            }

        try:
            # Find or create customer
            customers = stripe.Customer.list(email=firm_email, limit=1)
            if customers.data:
                customer = customers.data[0]
            else:
                customer = stripe.Customer.create(
                    email=firm_email,
                    metadata={"platform": "kovelai", "tier": tier},
                )

            # Attach payment method if provided
            if payment_method:
                stripe.PaymentMethod.attach(payment_method, customer=customer.id)
                stripe.Customer.modify(
                    customer.id,
                    invoice_settings={"default_payment_method": payment_method},
                )

            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{"price": price_id}],
                metadata={"platform": "kovelai", "tier": tier},
            )

            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "tier": tier,
                "customer_id": customer.id,
            }

        except stripe.StripeError as e:
            logger.error("Subscription creation failed: %s", str(e))
            return {
                "subscription_id": None,
                "status": "failed",
                "error": str(e),
            }

    # ── Webhook Verification ────────────────────────────

    @staticmethod
    def verify_webhook(payload: bytes, sig_header: str) -> Optional[dict]:
        """
        Verify a Stripe webhook signature and return the event.

        Returns:
            Parsed event dict, or None if verification fails
        """
        if not STRIPE_AVAILABLE or not WEBHOOK_SECRET:
            logger.warning("Webhook verification skipped — Stripe not configured")
            return None

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
            return event
        except stripe.SignatureVerificationError:
            logger.error("Webhook signature verification FAILED")
            return None
        except ValueError:
            logger.error("Invalid webhook payload")
            return None

    # ── Reporting ───────────────────────────────────────

    @staticmethod
    def get_account_balance(account_id: str) -> dict:
        """Get the balance for a connected account (for lawyer dashboard)."""
        if not STRIPE_AVAILABLE:
            return {
                "available": [{"amount": 0, "currency": "usd"}],
                "pending": [{"amount": 0, "currency": "usd"}],
                "status": "mock",
            }

        try:
            balance = stripe.Balance.retrieve(stripe_account=account_id)
            return {
                "available": [
                    {"amount": b.amount, "currency": b.currency} for b in balance.available
                ],
                "pending": [{"amount": b.amount, "currency": b.currency} for b in balance.pending],
                "status": "live",
            }
        except stripe.StripeError as e:
            return {"status": "error", "error": str(e)}
