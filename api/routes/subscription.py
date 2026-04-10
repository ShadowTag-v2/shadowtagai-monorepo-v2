from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import stripe
import os

router = APIRouter(prefix="/api/subscription", tags=["subscription"])
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

class CheckoutRequest(BaseModel):
    tier: str
    email: str
    success_url: str = "https://cor2.ai/success"
    cancel_url: str = "https://cor2.ai/pricing"

@router.post("/create-checkout-session")
async def create_checkout_session(req: CheckoutRequest):
    price_ids = {
        'pro': os.getenv('PRO_PRICE_ID'),
        'math_auditor': os.getenv('MATH_AUDITOR_PRICE_ID')
    }
    if req.tier not in price_ids:
        raise HTTPException(400, f"Invalid tier: {req.tier}")
    try:
        session = stripe.checkout.Session.create(
            customer_email=req.email,
            payment_method_types=['card'],
            line_items=[{'price': price_ids[req.tier], 'quantity': 1}],
            mode='subscription',
            success_url=req.success_url,
            cancel_url=req.cancel_url
        )
        return {'checkout_url': session.url, 'session_id': session.id}
    except Exception as e:
        raise HTTPException(400, str(e))
