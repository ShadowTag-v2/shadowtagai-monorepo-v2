"""PNKLN Billing Service - Stripe Integration
Handles invoice generation, usage recording, and webhook processing.
"""

import logging
import os
from datetime import datetime

import stripe

from src.pnkln.services.monetization import RateCard, RevenueEvent

logger = logging.getLogger(__name__)

# Initialize Stripe with API key from environment
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_placeholder")


class BillingService:
    """Billing service for Tower Edge revenue capture.
    Integrates with Stripe for invoicing and usage-based billing.
    """

    def __init__(self, rate_card: RateCard | None = None):
        """Initialize billing service.

        Args:
            rate_card: RateCard for pricing (defaults to standard rates)

        """
        self.rate_card = rate_card or RateCard()
        self._ensure_stripe_products()

    def _ensure_stripe_products(self):
        """Ensure Stripe products and prices exist."""
        try:
            # Check if products exist, create if not
            products = stripe.Product.list(limit=10)
            product_names = {p.name for p in products.data}

            if "PNKLN Edge Egress" not in product_names:
                self.egress_product = stripe.Product.create(
                    name="PNKLN Edge Egress",
                    description="Data processed at edge vs. cloud backhaul",
                )
                self.egress_price = stripe.Price.create(
                    product=self.egress_product.id,
                    unit_amount=int(self.rate_card.data_egress_saved_price_per_gb * 100),
                    currency="usd",
                    billing_scheme="per_unit",
                )
            else:
                self.egress_product = next(
                    p for p in products.data if p.name == "PNKLN Edge Egress"
                )
                prices = stripe.Price.list(product=self.egress_product.id, limit=1)
                self.egress_price = prices.data[0] if prices.data else None

            if "PNKLN Edge Inference" not in product_names:
                self.inference_product = stripe.Product.create(
                    name="PNKLN Edge Inference",
                    description="Low-latency inference at edge node",
                )
                self.inference_price = stripe.Price.create(
                    product=self.inference_product.id,
                    unit_amount=int(
                        self.rate_card.inference_unit_price * 100 * 1000,
                    ),  # Per 1000 inferences
                    currency="usd",
                    billing_scheme="per_unit",
                )
            else:
                self.inference_product = next(
                    p for p in products.data if p.name == "PNKLN Edge Inference"
                )
                prices = stripe.Price.list(product=self.inference_product.id, limit=1)
                self.inference_price = prices.data[0] if prices.data else None

            logger.info("Stripe products initialized")
        except stripe.error.AuthenticationError:
            logger.warning("Stripe API key not configured - running in mock mode")
            self.egress_price = None
            self.inference_price = None

    def get_or_create_customer(self, client_id: str, email: str | None = None) -> str:
        """Get or create a Stripe customer for the client.

        Args:
            client_id: Internal client identifier
            email: Customer email (optional)

        Returns:
            Stripe customer ID

        """
        try:
            # Search for existing customer by metadata
            customers = stripe.Customer.search(query=f"metadata['pnkln_client_id']:'{client_id}'")
            if customers.data:
                return customers.data[0].id

            # Create new customer
            customer = stripe.Customer.create(email=email, metadata={"pnkln_client_id": client_id})
            logger.info(f"Created Stripe customer {customer.id} for client {client_id}")
            return customer.id
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {e}")
            return f"mock_customer_{client_id}"

    def record_usage(
        self,
        client_id: str,
        node_id: str,
        gb_processed: float,
        inference_count: int,
    ) -> str:
        """Record usage for a client.

        Args:
            client_id: Client identifier
            node_id: Tower node that processed the workload
            gb_processed: GB of data processed at edge
            inference_count: Number of inference calls

        Returns:
            Usage record ID

        """
        event = RevenueEvent(
            client_id=client_id,
            node_id=node_id,
            gb_processed_at_edge=gb_processed,
            inference_count=inference_count,
        )

        bill_amount = event.calculate_bill(self.rate_card)

        logger.info(
            f"Usage recorded: {client_id} | Node: {node_id} | "
            f"Egress: {gb_processed}GB | Inferences: {inference_count} | "
            f"Bill: ${bill_amount:.4f}",
        )

        return f"usage_{client_id}_{datetime.now().isoformat()}"

    def create_invoice(self, client_id: str, revenue_event: RevenueEvent) -> str:
        """Create an invoice for a revenue event.

        Args:
            client_id: Client identifier
            revenue_event: Event to bill

        Returns:
            Invoice ID

        """
        try:
            customer_id = self.get_or_create_customer(client_id)
            bill_amount = revenue_event.calculate_bill(self.rate_card)

            invoice = stripe.Invoice.create(
                customer=customer_id,
                collection_method="send_invoice",
                days_until_due=30,
                metadata={
                    "node_id": revenue_event.node_id,
                    "gb_processed": str(revenue_event.gb_processed_at_edge),
                    "inference_count": str(revenue_event.inference_count),
                },
            )

            # Add line items
            if revenue_event.gb_processed_at_edge > 0 and self.egress_price:
                stripe.InvoiceItem.create(
                    customer=customer_id,
                    invoice=invoice.id,
                    price=self.egress_price.id,
                    quantity=int(revenue_event.gb_processed_at_edge),
                )

            if revenue_event.inference_count > 0 and self.inference_price:
                stripe.InvoiceItem.create(
                    customer=customer_id,
                    invoice=invoice.id,
                    price=self.inference_price.id,
                    quantity=revenue_event.inference_count // 1000 or 1,
                )

            # Finalize and send
            stripe.Invoice.finalize_invoice(invoice.id)

            logger.info(f"Invoice {invoice.id} created for ${bill_amount:.2f}")
            return invoice.id

        except stripe.error.StripeError as e:
            logger.error(f"Failed to create invoice: {e}")
            return f"mock_invoice_{client_id}_{datetime.now().isoformat()}"

    @staticmethod
    def handle_webhook(payload: bytes, sig_header: str, endpoint_secret: str) -> dict:
        """Handle Stripe webhook events.

        Args:
            payload: Raw webhook payload
            sig_header: Stripe signature header
            endpoint_secret: Webhook endpoint secret

        Returns:
            Processed event data

        """
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)

            if event.type == "invoice.paid":
                invoice = event.data.object
                logger.info(f"Invoice {invoice.id} paid: ${invoice.amount_paid / 100:.2f}")
                return {
                    "status": "success",
                    "event": "invoice.paid",
                    "invoice_id": invoice.id,
                }

            if event.type == "invoice.payment_failed":
                invoice = event.data.object
                logger.warning(f"Invoice {invoice.id} payment failed")
                return {
                    "status": "failed",
                    "event": "invoice.payment_failed",
                    "invoice_id": invoice.id,
                }

            return {"status": "ignored", "event": event.type}

        except stripe.error.SignatureVerificationError:
            logger.error("Invalid webhook signature")
            return {"status": "error", "message": "Invalid signature"}

    @staticmethod
    def create_test_invoice():
        """Create a test invoice for verification."""
        service = BillingService()
        event = RevenueEvent(
            client_id="test_client",
            node_id="TEST-NODE-001",
            gb_processed_at_edge=10.0,
            inference_count=5000,
        )
        invoice_id = service.create_invoice("test_client", event)
        print(f"Test invoice created: {invoice_id}")
        return invoice_id
