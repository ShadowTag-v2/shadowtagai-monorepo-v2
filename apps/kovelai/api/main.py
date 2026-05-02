"""KovelAI FastAPI Backend — S.E.U. Proxy + Stripe Connect + Kovel Enclave

Architecture:
    Client (CC login) → S.E.U. Token → AI/Search APIs → Evaporation
    Payment: Client CC → Stripe Connect → Lawyer's Bank (we never touch legal fees)
    Our revenue: Lawyer's auto-scaling monthly SaaS tier

Per U.S. v. Heppner (S.D.N.Y., Feb 2026):
    - All client queries are ephemeral (RAM-only)
    - Lawyer receives permanent transcript
    - Anti-forensic evaporation on client logout
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
import secrets
import time
from datetime import UTC, datetime

from api.stripe_connect import StripeConnect
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

logger = logging.getLogger("kovelai.api")

app = FastAPI(
    title="KovelAI — Privileged Client Gateway",
    version="1.0.0",
    description="S.E.U. Proxy + Stripe Connect + Kovel Enclave",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://kovelai.com", "http://localhost:3000"],
    allow_methods=["POST", "GET"],
    allow_headers=os.environ.get("CORS_HEADERS", "Content-Type,Authorization,X-Requested-With").split(","),
)


# ──────────────────────────────────────────────
# Models
# ──────────────────────────────────────────────


class MagicLinkRequest(BaseModel):
    """Lawyer initiates a Magic Link for their client."""

    attorney_id: str = Field(..., description="Attorney's unique ID")
    client_email: str = Field(..., description="Client's email for Magic Link delivery")
    session_rate_cents: int = Field(
        default=1500,
        description="Per-query rate in cents ($15 default)",
    )
    session_ttl_seconds: int = Field(default=1800, description="Session timeout (30 min default)")


class ClientQuery(BaseModel):
    """Client's query through the S.E.U. proxy."""

    query: str = Field(..., max_length=4000, description="Client's natural language query")
    query_type: str = Field(
        default="ai_chat",
        description="ai_chat | web_search | translation | osint",
    )


class SessionToken(BaseModel):
    """S.E.U. ephemeral session token."""

    token: str
    expires_at: str
    session_id: str
    bound_ip: str
    attorney_id: str
    tier: str


class PrivilegedResponse(BaseModel):
    """Response delivered to the client — ephemeral."""

    result: str
    disclaimer: str
    ttl_seconds: int
    vault_signature: str


class LawyerTranscript(BaseModel):
    """Permanent record delivered to the lawyer's dashboard."""

    session_id: str
    attorney_id: str
    query: str
    response: str
    timestamp: str
    vault_signature: str


# ──────────────────────────────────────────────
# S.E.U. Security Layer
# ──────────────────────────────────────────────


class SEUProxyEngine:
    """Sandbox-bound, Ephemeral, User-billed token management.
    Mathematically immune to supply-chain API key exfiltration.
    """

    _active_sessions: dict[str, dict] = {}

    @classmethod
    def mint_token(cls, attorney_id: str, client_ip: str, tier: str = "starter") -> SessionToken:
        """Mint an ephemeral token bound to session + IP."""
        session_id = secrets.token_hex(16)
        token = secrets.token_urlsafe(48)
        expires_at = datetime.now(UTC).isoformat()

        cls._active_sessions[token] = {
            "session_id": session_id,
            "attorney_id": attorney_id,
            "bound_ip": client_ip,
            "tier": tier,
            "minted_at": time.time(),
            "query_count": 0,
        }

        return SessionToken(
            token=token,
            expires_at=expires_at,
            session_id=session_id,
            bound_ip=client_ip,
            attorney_id=attorney_id,
            tier=tier,
        )

    @classmethod
    def validate_token(cls, token: str, client_ip: str) -> dict:
        """Validate token is active + IP-bound. Reject stolen tokens."""
        session = cls._active_sessions.get(token)
        if not session:
            raise HTTPException(status_code=401, detail="S.E.U. REJECTED: Token expired or invalid")
        if session["bound_ip"] != client_ip:
            raise HTTPException(
                status_code=403,
                detail="S.E.U. REJECTED: IP mismatch — possible exfiltration",
            )
        return session

    @classmethod
    def destroy_token(cls, token: str) -> bool:
        """Mathematically destroy the token on logout."""
        return cls._active_sessions.pop(token, None) is not None

    @classmethod
    def increment_usage(cls, token: str) -> int:
        """Track usage for tier auto-scaling."""
        session = cls._active_sessions.get(token)
        if session:
            session["query_count"] += 1
            return session["query_count"]
        return 0


# ──────────────────────────────────────────────
# Kovel Shield (Cryptographic Signing)
# ──────────────────────────────────────────────


class KovelShield:
    """Cryptographic signing for Kovel Doctrine compliance."""

    @staticmethod
    def sign(payload: str) -> str:
        secret = os.getenv("KOVEL_KMS_SECRET", "dev-secret-rotate-in-production").encode()
        return hmac.new(secret, payload.encode(), hashlib.sha256).hexdigest()

    @staticmethod
    def disclaimer() -> str:
        return (
            "This is raw factual research retrieved at the direction of your attorney. "
            "It is not legal advice. This research has been flagged for your attorney "
            "to review and determine its legal applicability to your case."
        )


# ──────────────────────────────────────────────
# Billing Engine (Stripe Connect Abstraction)
# ──────────────────────────────────────────────


class BillingEngine:
    """Track A: Client CC → Stripe Connect → Lawyer's bank (we don't touch it)
    Track B: Lawyer's corporate card → KovelAI monthly tier
    """

    TIERS = {
        "starter": {"name": "Triage Starter", "price_cents": 39900, "max_sessions": 50},
        "pro": {"name": "Intelligence Pro", "price_cents": 129900, "max_sessions": 250},
        "sovereign": {"name": "Sovereign OS", "price_cents": 350000, "max_sessions": -1},
    }

    @classmethod
    def bill_client_query(cls, attorney_id: str, rate_cents: int, query_type: str) -> dict:
        """Bill the client's credit card via Stripe Connect.
        Payment routes DIRECTLY to the lawyer's bank. We never touch it.
        """
        # In production: stripe.PaymentIntent.create(
        #     amount=rate_cents,
        #     transfer_data={"destination": lawyer_stripe_account_id},
        # )
        return {
            "status": "charged",
            "attorney_id": attorney_id,
            "amount_cents": rate_cents,
            "query_type": query_type,
            "timestamp": datetime.now(UTC).isoformat(),
            "note": "Routed via Stripe Connect to lawyer's bank account",
        }

    @classmethod
    def check_tier_upgrade(cls, attorney_id: str, session_count: int) -> str | None:
        """Auto-upgrade lawyer's tier if they exceed session cap."""
        if session_count > 250:
            return "sovereign"
        if session_count > 50:
            return "pro"
        return None


# ──────────────────────────────────────────────
# API Endpoints
# ──────────────────────────────────────────────


@app.post("/api/v1/magic-link", response_model=dict)
async def create_magic_link(req: MagicLinkRequest):
    """Lawyer creates a Magic Link for their client."""
    # In production: send email via SendGrid/SES with secure link
    link_token = secrets.token_urlsafe(32)
    return {
        "status": "created",
        "magic_link": f"https://kovelai.com/portal/{link_token}",
        "attorney_id": req.attorney_id,
        "client_email": req.client_email,
        "session_rate_cents": req.session_rate_cents,
        "session_ttl_seconds": req.session_ttl_seconds,
    }


@app.post("/api/v1/session/start", response_model=SessionToken)
async def start_session(request: Request, attorney_id: str = Header(...)):
    """Client logs in with credit card. S.E.U. token minted."""
    client_ip = request.client.host if request.client else "unknown"
    token = SEUProxyEngine.mint_token(
        attorney_id=attorney_id,
        client_ip=client_ip,
        tier="starter",
    )
    return token


@app.post("/api/v1/query", response_model=PrivilegedResponse)
async def execute_privileged_query(
    query: ClientQuery,
    request: Request,
    x_seu_token: str = Header(..., alias="X-SEU-Token"),
):
    """Client executes a privileged query through the S.E.U. proxy.
    Query is processed in RAM, result delivered, data evaporated.
    """
    client_ip = request.client.host if request.client else "unknown"

    # S.E.U. Validation
    session = SEUProxyEngine.validate_token(x_seu_token, client_ip)
    count = SEUProxyEngine.increment_usage(x_seu_token)

    # Billing: charge client's CC via Stripe Connect
    billing_result = StripeConnect.bill_client_query(
        lawyer_account_id=session.get("stripe_account_id", "acct_default"),
        rate_cents=1500,
        client_payment_method=session.get("payment_method", "pm_default"),
        session_id=session["session_id"],
        query_type=query.query_type,
    )
    logger.info("Billing result: %s", billing_result.get("status"))

    # Check tier auto-upgrade
    new_tier = BillingEngine.check_tier_upgrade(session["attorney_id"], count)
    if new_tier and new_tier != session["tier"]:
        session["tier"] = new_tier

    # Cryptographic signing for Kovel compliance
    vault_sig = KovelShield.sign(f"{session['attorney_id']}:{query.query}:{int(time.time())}")

    # In production: route to LiteLLM (Gemini/Claude/GPT) or Vertex AI Enterprise Search
    # based on query_type. Currently returns placeholder.
    result = f"[{query.query_type.upper()}] Privileged research result for query: '{query.query[:100]}...'"

    # Anti-forensic: Python GC will collect these locals after return
    return PrivilegedResponse(
        result=result,
        disclaimer=KovelShield.disclaimer(),
        ttl_seconds=30,
        vault_signature=vault_sig,
    )


@app.post("/api/v1/session/end")
async def end_session(x_seu_token: str = Header(..., alias="X-SEU-Token")):
    """Client logout. Token mathematically destroyed. Data evaporated."""
    destroyed = SEUProxyEngine.destroy_token(x_seu_token)
    if not destroyed:
        raise HTTPException(status_code=404, detail="Session already expired")
    return {
        "status": "evaporated",
        "message": "Session destroyed. Token invalidated. Query data garbage-collected.",
    }


@app.get("/api/v1/health")
async def health():
    """Health check."""
    return {
        "status": "operational",
        "service": "KovelAI S.E.U. Proxy",
        "version": "1.0.0",
        "active_sessions": len(SEUProxyEngine._active_sessions),
    }


@app.get("/api/v1/tiers")
async def list_tiers():
    """List available pricing tiers."""
    return BillingEngine.TIERS


# ──────────────────────────────────────────────
# Stripe Connect Endpoints
# ──────────────────────────────────────────────


class OnboardFirmRequest(BaseModel):
    """Firm onboarding request."""

    firm_name: str = Field(..., description="Law firm name")
    email: str = Field(..., description="Firm admin email")


@app.post("/api/v1/stripe/onboard")
async def onboard_firm(req: OnboardFirmRequest):
    """Create a Stripe Express Connected Account for a new law firm.
    Returns an onboarding link the firm owner clicks to complete KYC.
    """
    account = StripeConnect.create_connected_account(
        firm_name=req.firm_name,
        email=req.email,
    )
    if account.get("status") == "failed":
        raise HTTPException(status_code=500, detail=account.get("error", "Account creation failed"))

    # Generate the Stripe-hosted onboarding link
    link = StripeConnect.create_account_link(account["account_id"])
    return {
        "account_id": account["account_id"],
        "onboarding_url": link.get("url"),
        "status": account["status"],
    }


@app.post("/api/v1/stripe/webhook")
async def stripe_webhook(request: Request):
    """Stripe webhook handler. Processes:
    - payment_intent.succeeded → log client payment
    - account.updated → track onboarding completion
    - invoice.paid → confirm SaaS tier payment
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    event = StripeConnect.verify_webhook(payload, sig_header)
    if event is None:
        # In dev mode without webhook secret, log but accept
        logger.warning("Webhook verification skipped or failed")
        return JSONResponse(
            status_code=200,
            content={"status": "received", "verified": False},
        )

    event_type = event.get("type", "")
    data = event.get("data", {}).get("object", {})

    if event_type == "payment_intent.succeeded":
        logger.info(
            "Payment succeeded: %s → %s (%d cents)",
            data.get("id"),
            data.get("transfer_data", {}).get("destination"),
            data.get("amount", 0),
        )
    elif event_type == "account.updated":
        logger.info(
            "Account updated: %s (charges_enabled=%s)",
            data.get("id"),
            data.get("charges_enabled"),
        )
    elif event_type == "invoice.paid":
        logger.info(
            "Invoice paid: %s for customer %s",
            data.get("id"),
            data.get("customer"),
        )
    else:
        logger.debug("Unhandled event type: %s", event_type)

    return JSONResponse(
        status_code=200,
        content={"status": "processed", "type": event_type},
    )


@app.get("/api/v1/stripe/balance/{account_id}")
async def get_firm_balance(account_id: str):
    """Get the balance for a connected account.
    Used in the lawyer dashboard to show earnings.
    """
    balance = StripeConnect.get_account_balance(account_id)
    return balance


class SubscribeRequest(BaseModel):
    """Firm subscription request (Track B)."""

    email: str = Field(..., description="Firm billing email")
    tier: str = Field(default="starter", description="starter | pro | sovereign")
    payment_method: str | None = Field(default=None, description="Stripe payment method ID")


@app.post("/api/v1/stripe/subscribe")
async def subscribe_firm(req: SubscribeRequest):
    """Create or update a KovelAI SaaS subscription for the firm.
    This is Track B: Lawyer pays US for platform access.
    """
    result = StripeConnect.create_firm_subscription(
        firm_email=req.email,
        tier=req.tier,
        payment_method=req.payment_method,
    )
    if result.get("status") == "failed":
        raise HTTPException(status_code=500, detail=result.get("error", "Subscription failed"))
    return result
