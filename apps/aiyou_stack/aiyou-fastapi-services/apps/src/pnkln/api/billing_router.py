"""PNKLN Billing API Router
Exposes billing endpoints for revenue capture.
"""

import logging
import os

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel

from src.pnkln.services.billing_service import BillingService
from src.pnkln.services.monetization import RevenueEvent

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/billing", tags=["billing"])

# Initialize billing service
billing_service = BillingService()


class UsageRequest(BaseModel):
    """Request model for recording usage."""

    client_id: str
    node_id: str
    gb_processed: float = 0.0
    inference_count: int = 0


class InvoiceRequest(BaseModel):
    """Request model for creating an invoice."""

    client_id: str
    node_id: str
    gb_processed: float
    inference_count: int
    email: str | None = None


class InvoiceResponse(BaseModel):
    """Response model for invoice creation."""

    invoice_id: str
    amount_usd: float
    status: str


@router.post("/events", response_model=dict)
async def record_billing_event(request: UsageRequest):
    """Record a billing event for usage tracking.

    Args:
        request: Usage details

    Returns:
        Confirmation with usage record ID

    """
    try:
        usage_id = billing_service.record_usage(
            client_id=request.client_id,
            node_id=request.node_id,
            gb_processed=request.gb_processed,
            inference_count=request.inference_count,
        )

        # Calculate bill for response
        event = RevenueEvent(
            client_id=request.client_id,
            node_id=request.node_id,
            gb_processed_at_edge=request.gb_processed,
            inference_count=request.inference_count,
        )
        bill = event.calculate_bill(billing_service.rate_card)

        return {
            "status": "recorded",
            "usage_id": usage_id,
            "bill_amount_usd": round(bill, 4),
        }
    except Exception as e:
        logger.error(f"Failed to record billing event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/invoices", response_model=InvoiceResponse)
async def create_invoice(request: InvoiceRequest):
    """Create an invoice for a revenue event.

    Args:
        request: Invoice details

    Returns:
        Invoice ID and amount

    """
    try:
        event = RevenueEvent(
            client_id=request.client_id,
            node_id=request.node_id,
            gb_processed_at_edge=request.gb_processed,
            inference_count=request.inference_count,
        )

        invoice_id = billing_service.create_invoice(request.client_id, event)
        bill = event.calculate_bill(billing_service.rate_card)

        return InvoiceResponse(invoice_id=invoice_id, amount_usd=round(bill, 2), status="created")
    except Exception as e:
        logger.error(f"Failed to create invoice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/invoices/{client_id}")
async def list_invoices(client_id: str, limit: int = 10):
    """List invoices for a client.

    Args:
        client_id: Client identifier
        limit: Max invoices to return

    Returns:
        List of invoice summaries

    """
    try:
        import stripe

        customer_id = billing_service.get_or_create_customer(client_id)
        invoices = stripe.Invoice.list(customer=customer_id, limit=limit)

        return {
            "client_id": client_id,
            "invoices": [
                {
                    "invoice_id": inv.id,
                    "amount_usd": inv.amount_due / 100,
                    "status": inv.status,
                    "created": inv.created,
                }
                for inv in invoices.data
            ],
        }
    except Exception as e:
        logger.error(f"Failed to list invoices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature"),
):
    """Handle Stripe webhook events.

    Args:
        request: Raw request with payload
        stripe_signature: Stripe signature header

    Returns:
        Processing result

    """
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")

    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing Stripe-Signature header")

    payload = await request.body()
    result = BillingService.handle_webhook(payload, stripe_signature, endpoint_secret)

    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("message"))

    return result


@router.get("/health")
async def billing_health():
    """Health check for billing service."""
    return {
        "status": "healthy",
        "stripe_configured": bool(os.getenv("STRIPE_SECRET_KEY")),
        "rate_card": {
            "egress_per_gb_usd": billing_service.rate_card.data_egress_saved_price_per_gb,
            "inference_per_unit_usd": billing_service.rate_card.inference_unit_price,
        },
    }
