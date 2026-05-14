# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Judge #6 - ATP 5-19 Risk Management API for AI
Main FastAPI Application

Run with: uvicorn judge6.main:app --reload
"""

from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import time
import uuid

from .core.config import settings
from .core.judge import get_judge, JudgmentResult, Decision
from .services.database import get_db, init_db, get_sync_db
from .services.auth import AuthService
from .services.stripe_service import StripeService
from .models.database import User, AuditLog, SubscriptionTier
from .api import schemas
import stripe


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="ATP 5-19 Risk Management API for AI Systems",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database and services"""
    await init_db()
    print(f"{settings.APP_NAME} v{settings.APP_VERSION} starting...")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Target p99 latency: {settings.TARGET_P99_LATENCY_MS}ms")


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


# Dependency: Verify API key
async def verify_api_key(
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Verify API key from Authorization header
    Format: "Bearer judge6_sk_..."
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing API key")

    # Extract API key
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid API key format")

    api_key = authorization[7:]  # Remove "Bearer "

    # Verify API key (note: this is a sync call, need to adapt)
    # For now, convert to sync context
    from sqlalchemy import select
    from .models.database import APIKey as APIKeyModel
    import hashlib

    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    result = await db.execute(select(APIKeyModel).where(APIKeyModel.key_hash == key_hash))
    api_key_obj = result.scalar_one_or_none()

    if not api_key_obj or not api_key_obj.is_active:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Get user
    result = await db.execute(select(User).where(User.id == api_key_obj.user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User account inactive")

    # Check rate limit
    if user.current_month_usage >= user.monthly_request_limit:
        raise HTTPException(
            status_code=429,
            detail=f"Monthly quota exceeded. Used {user.current_month_usage}/{user.monthly_request_limit} requests.",
        )

    # Update usage
    api_key_obj.total_requests += 1
    user.current_month_usage += 1
    await db.commit()

    return user


# CORE API ENDPOINTS


@app.post("/api/v1/judge", response_model=schemas.JudgeResponse)
async def judge_request(
    request: schemas.JudgeRequest,
    user: User = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db),
):
    """
    Judge an AI request using ATP 5-19 risk assessment

    This is the main endpoint - runs all 3 layers and returns judgment.
    """
    start_time = time.perf_counter()
    request_id = str(uuid.uuid4())

    try:
        # Get Judge instance
        judge = get_judge()

        # Run assessment
        result: JudgmentResult = await judge.assess(
            prompt=request.prompt,
            context=request.context,
            user_policies=None,  # TODO: Load from user.policies
            request_id=request_id,
        )

        # Create audit log
        audit_log = AuditLog(
            user_id=user.id,
            request_id=request_id,
            prompt=request.prompt,
            context=request.context,
            layer1_decision=result.layer1_result.risk_level,
            layer1_confidence=result.layer1_result.confidence,
            layer1_reasoning=result.layer1_result.reasoning,
            layer1_latency_ms=result.layer1_result.latency_ms,
            layer2_decision=result.layer2_result.risk_level,
            layer2_confidence=result.layer2_result.confidence,
            layer2_reasoning=result.layer2_result.reasoning,
            layer2_latency_ms=result.layer2_result.latency_ms,
            layer3_decision=len(result.violated_rules) == 0,
            layer3_violated_rules=result.violated_rules,
            layer3_latency_ms=result.layer3_result.latency_ms,
            final_risk_level=result.risk_level,
            final_allowed=result.decision == Decision.ALLOW,
            final_reasoning=result.reasoning,
            latency_ms=result.total_latency_ms,
        )

        db.add(audit_log)
        await db.commit()

        # Return response
        return schemas.JudgeResponse(
            request_id=request_id,
            decision=result.decision.value,
            risk_level=result.risk_level.value,
            confidence=result.confidence,
            reasoning=result.reasoning,
            violated_rules=result.violated_rules,
            latency_ms=result.total_latency_ms,
            usage={
                "requests_used": user.current_month_usage,
                "requests_limit": user.monthly_request_limit,
                "tier": user.tier.value,
            },
        )

    except Exception as e:
        # Log error
        print(f"Judge error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


# USER MANAGEMENT


@app.post("/api/v1/auth/register", response_model=schemas.UserResponse)
async def register(
    user_data: schemas.UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user"""
    from sqlalchemy import select

    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    hashed_password = AuthService.hash_password(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        company=user_data.company,
        tier=SubscriptionTier.FREE,
        monthly_request_limit=settings.RATE_LIMIT_FREE,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Create Stripe customer (if Stripe is configured)
    if settings.STRIPE_SECRET_KEY:
        try:
            customer = StripeService.create_customer(
                email=user.email,
                name=user.full_name,
                metadata={"user_id": str(user.id), "company": user.company or ""},
            )
            user.stripe_customer_id = customer.id
            await db.commit()
        except Exception as e:
            print(f"Warning: Failed to create Stripe customer: {e}")

    # Create initial API key
    from .models.database import APIKey

    full_key, key_hash, key_prefix = AuthService.generate_api_key()

    api_key = APIKey(
        user_id=user.id,
        key_hash=key_hash,
        key_prefix=key_prefix,
        name="Default API Key",
    )

    db.add(api_key)
    await db.commit()

    return schemas.UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        company=user.company,
        tier=user.tier.value,
        api_key=full_key,  # Only returned once!
        monthly_limit=user.monthly_request_limit,
        current_usage=user.current_month_usage,
    )


@app.post("/api/v1/auth/login")
async def login(
    credentials: schemas.UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Login and get access token"""
    from sqlalchemy import select

    # Find user
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Verify password
    if not AuthService.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create access token
    from datetime import timedelta

    access_token = AuthService.create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "tier": user.tier.value,
        },
    }


@app.get("/api/v1/usage")
async def get_usage(
    user: User = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db),
):
    """Get current usage statistics"""
    return {
        "tier": user.tier.value,
        "requests_used": user.current_month_usage,
        "requests_limit": user.monthly_request_limit,
        "overage": max(0, user.current_month_usage - user.monthly_request_limit),
        "percentage_used": (user.current_month_usage / user.monthly_request_limit * 100) if user.monthly_request_limit > 0 else 0,
    }


# BILLING & SUBSCRIPTIONS


@app.post("/api/v1/billing/checkout")
async def create_checkout_session(
    tier: str,
    annual: bool = False,
    user: User = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db),
):
    """
    Create Stripe checkout session for subscription upgrade

    Args:
        tier: "starter" or "professional"
        annual: True for annual billing (16.7% discount)

    Returns:
        checkout_url: Redirect user to this URL to complete payment
    """
    # Validate tier
    if tier not in ["starter", "professional"]:
        raise HTTPException(status_code=400, detail="Invalid tier. Must be 'starter' or 'professional'")

    # Create Stripe customer if doesn't exist

    if not user.stripe_customer_id:
        customer = StripeService.create_customer(
            email=user.email,
            name=user.full_name,
            metadata={"user_id": str(user.id)},
        )
        user.stripe_customer_id = customer.id
        await db.commit()

    # Get price ID
    price_key = f"{tier}_{'annual' if annual else 'monthly'}"
    price_id = StripeService.PRICE_IDS.get(price_key)

    if not price_id:
        raise HTTPException(status_code=500, detail=f"Price ID not configured for {price_key}")

    # Create checkout session
    session = StripeService.create_checkout_session(
        customer_id=user.stripe_customer_id,
        price_id=price_id,
        success_url=f"{settings.CORS_ORIGINS[0]}/dashboard?payment=success",
        cancel_url=f"{settings.CORS_ORIGINS[0]}/dashboard?payment=canceled",
        metadata={"user_id": str(user.id), "tier": tier},
    )

    return {"checkout_url": session.url}


@app.post("/api/v1/billing/portal")
async def create_portal_session(
    user: User = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db),
):
    """
    Create Stripe Customer Portal session
    Allows user to manage subscription, update payment method, view invoices
    """
    if not user.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No Stripe customer found")

    session = StripeService.create_portal_session(
        customer_id=user.stripe_customer_id,
        return_url=f"{settings.CORS_ORIGINS[0]}/dashboard",
    )

    return {"portal_url": session.url}


@app.post("/api/v1/billing/webhook")
async def stripe_webhook(request: Request):
    """
    Stripe webhook handler
    Processes subscription events (created, updated, canceled, payment failed)

    IMPORTANT: This endpoint must be registered in Stripe Dashboard
    URL: https://yourdomain.com/api/v1/billing/webhook
    Events to send: checkout.session.completed, customer.subscription.updated,
                    customer.subscription.deleted, invoice.payment_failed
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")

    try:
        event = StripeService.handle_webhook_event(payload, sig_header)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Process event (use sync DB for webhooks)

    db = next(get_sync_db())

    try:
        if event["type"] == "checkout.session.completed":
            StripeService.process_subscription_created(event["data"], db)

        elif event["type"] == "customer.subscription.updated":
            StripeService.process_subscription_updated(event["data"], db)

        elif event["type"] == "customer.subscription.deleted":
            StripeService.process_subscription_updated(event["data"], db)

        elif event["type"] == "invoice.payment_failed":
            StripeService.process_payment_failed(event["data"], db)

        else:
            print(f"Unhandled event type: {event['type']}")

    finally:
        db.close()

    return {"status": "success"}


@app.get("/api/v1/billing/subscription")
async def get_subscription(
    user: User = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db),
):
    """Get current subscription details"""
    if not user.stripe_subscription_id:
        return {
            "tier": user.tier.value,
            "status": "free",
            "subscription": None,
        }

    try:
        subscription = StripeService.get_subscription(user.stripe_subscription_id)

        return {
            "tier": user.tier.value,
            "status": subscription["status"],
            "current_period_end": subscription["current_period_end"],
            "cancel_at_period_end": subscription["cancel_at_period_end"],
            "subscription": {
                "id": subscription["id"],
                "plan": subscription["items"]["data"][0]["price"]["nickname"],
                "amount": subscription["items"]["data"][0]["price"]["unit_amount"] / 100,
                "currency": subscription["items"]["data"][0]["price"]["currency"],
                "interval": subscription["items"]["data"][0]["price"]["recurring"]["interval"],
            },
        }
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=500, detail=f"Stripe error: {str(e)}")


# Root redirect
@app.get("/")
async def root():
    """Root endpoint - redirect to docs"""
    return {
        "message": "Judge #6 - ATP 5-19 Risk Management API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "judge6.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
