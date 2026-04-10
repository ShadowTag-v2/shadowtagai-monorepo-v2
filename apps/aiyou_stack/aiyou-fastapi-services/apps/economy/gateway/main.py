import logging
import os

from fastapi import FastAPI, HTTPException, Request

# import stripe (mocked for now)

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PaymentGateway")

app = FastAPI(title="Antigravity Payment Gateway", version="1.0.0")

# Mock Stripe Secret
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_mock_secret")


@app.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """
    Listens for Stripe 'checkout.session.completed' events.
    Triggers NFT Minting upon success.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    # Verify Signature (Mock logic)
    if not sig_header:
        logger.warning("Missing stripe-signature header")
        # In real env, raise HTTPException

    logger.info("Received Stripe Webhook")

    try:
        data = await request.json()
        event_type = data.get("type")

        if event_type == "checkout.session.completed":
            session = data.get("data", {}).get("object", {})
            customer_email = session.get("customer_details", {}).get("email")
            amount_total = session.get("amount_total")

            logger.info(f"💰 Payment Successful: {customer_email} paid {amount_total}")

            # TRIGGER MINTING
            # In a real microservices arch, we would emit a Pub/Sub event here
            # or call the Minter Service URL.
            # await call_minter_service(customer_email)
            logger.info(f"🚀 Triggering NFT Mint for {customer_email}")

        else:
            logger.info(f"Unhandled event type: {event_type}")

    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(status_code=400, detail="Webhook error")

    return {"status": "success"}


@app.get("/health")
def health_check():
    return {"status": "active", "service": "payment-gateway"}
