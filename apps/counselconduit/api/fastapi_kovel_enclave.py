# apps/counselconduit/api/fastapi_kovel_enclave.py
"""CounselConduit: Kovel Enclave v3.0

Production API for KovelAI — Privileged Legal AI under the Kovel Doctrine.

Architecture:
    POST /enclave/v1/query           → Synchronous privileged query
    POST /enclave/v1/query/stream    → SSE streaming privileged query
    POST /webhooks/stripe            → Stripe billing webhooks
    GET  /enclave/v1/health          → Health check
    POST /account/delete             → GDPR Article 17 — Right to Erasure (30-day grace)
    POST /account/export             → GDPR Article 20 — Right to Data Portability
    GET  /account/deletion-status    → Check pending deletion status
    POST /onboarding/magic-link      → Magic link email authentication
    POST /kovel/attest               → Kovel attestation receipt (HMAC-SHA256)
    POST /vent                       → Vent Mode SSE streaming

Per U.S. v. Heppner (S.D.N.Y., Feb 2026):
    - All client queries are ephemeral (RAM-only)
    - Lawyer receives permanent transcript
    - Anti-forensic evaporation on client logout
"""

from __future__ import annotations

import os
import time

import structlog
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

try:
    # Monorepo context (running from repo root)
    from apps.counselconduit.api.firestore_client import (
        update_attorney_usage,
        write_audit_log,
        AuditEntry,
    )
    from apps.counselconduit.api.gemini_rag import (
        QueryRequest,
        QueryResponse,
        execute_privileged_query,
        stream_privileged_query,
    )
    from apps.counselconduit.api.judge6 import evaluate as judge6_evaluate
    from apps.counselconduit.api.stripe_connect import router as billing_router
    from apps.counselconduit.api.stripe_handler import router as stripe_router
except ImportError:
    # Docker/Cloud Run context (running from /app/)
    from api.firestore_client import (  # type: ignore[no-redef]
        update_attorney_usage,
        write_audit_log,
        AuditEntry,
    )
    from api.gemini_rag import (  # type: ignore[no-redef]
        QueryRequest,
        QueryResponse,
        execute_privileged_query,
        stream_privileged_query,
    )
    from api.judge6 import evaluate as judge6_evaluate  # type: ignore[no-redef]
    from api.stripe_connect import router as billing_router  # type: ignore[no-redef]
    from api.stripe_handler import router as stripe_router  # type: ignore[no-redef]

# Middleware + Error handlers (same path in both contexts)
try:
    from apps.counselconduit.api.middleware import RateLimitMiddleware, SecurityHeadersMiddleware
    from apps.counselconduit.api.middleware.token_budget import TokenBudgetMiddleware
    from apps.counselconduit.api.middleware.prompt_guard import PromptGuardMiddleware
    from apps.counselconduit.api.app_error import AppError, app_error_handler, unhandled_error_handler
    from apps.counselconduit.api.gdpr import router as gdpr_router
    from apps.counselconduit.api.kovel_attestation import router as attestation_router
    from apps.counselconduit.api.magic_link import router as onboarding_router
    from apps.counselconduit.api.vent_mode import router as vent_router
    from apps.counselconduit.api.cloud_tasks_gdpr import router as tasks_router
    from apps.counselconduit.api.stripe_connect_webhook import router as connect_webhook_router
    from apps.counselconduit.api.resend_webhook import router as resend_router
    from apps.counselconduit.api.byok import router as byok_router
except ImportError:
    from api.middleware import RateLimitMiddleware, SecurityHeadersMiddleware  # type: ignore[no-redef]
    from api.middleware.token_budget import TokenBudgetMiddleware  # type: ignore[no-redef]
    from api.middleware.prompt_guard import PromptGuardMiddleware  # type: ignore[no-redef]
    from api.app_error import AppError, app_error_handler, unhandled_error_handler  # type: ignore[no-redef]
    from api.gdpr import router as gdpr_router  # type: ignore[no-redef]
    from api.kovel_attestation import router as attestation_router  # type: ignore[no-redef]
    from api.magic_link import router as onboarding_router  # type: ignore[no-redef]
    from api.vent_mode import router as vent_router  # type: ignore[no-redef]
    from api.cloud_tasks_gdpr import router as tasks_router  # type: ignore[no-redef]
    from api.stripe_connect_webhook import router as connect_webhook_router  # type: ignore[no-redef]
    from api.resend_webhook import router as resend_router  # type: ignore[no-redef]
    from api.byok import router as byok_router  # type: ignore[no-redef]

# ── Structured Logging ─────────────────────────────────────────────────────

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger("counselconduit")

# ── App Configuration ──────────────────────────────────────────────────────

app = FastAPI(
    title="CounselConduit: Kovel Enclave",
    version="3.1.0",
    description="Privileged Legal AI under the Kovel Doctrine. Zero-retention architecture.",
    docs_url="/docs",  # OpenAPI/Swagger enabled — API documentation
    redoc_url="/redoc",
)

# ── OpenTelemetry (Cloud Trace) ────────────────────────────────────────────
try:
    from api.telemetry import setup_telemetry

    setup_telemetry(app)
except ImportError:
    try:
        from apps.counselconduit.api.telemetry import setup_telemetry

        setup_telemetry(app)
    except ImportError:
        pass  # OTEL optional — runs without tracing if deps missing

# CORS — restrict in production (explicit allow-list, no wildcard)
_ALLOWED_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "https://kovelai.web.app,https://kovelai.com,https://shadowtagai.web.app,http://localhost:4000,http://localhost:5173",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    expose_headers=["X-Kovel-Signature", "X-RateLimit-Limit", "X-RateLimit-Remaining", "X-Token-Budget-Remaining"],
)

# Cor.30 R31: Security headers on every response
app.add_middleware(SecurityHeadersMiddleware)

# Cor.30 R14-R15: Per-IP + per-route rate limiting
app.add_middleware(RateLimitMiddleware)

# OWASP LLM10: Token budget + circuit breaker
app.add_middleware(TokenBudgetMiddleware)

# OWASP LLM01: Prompt injection detection
app.add_middleware(PromptGuardMiddleware)

# Cor.30: Opaque error handling — never expose stack traces
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, unhandled_error_handler)

# ── Router Mounts ──────────────────────────────────────────────────────────

app.include_router(stripe_router)
app.include_router(billing_router)
app.include_router(gdpr_router)
app.include_router(attestation_router)
app.include_router(onboarding_router)
app.include_router(vent_router)
app.include_router(tasks_router)
app.include_router(connect_webhook_router)
app.include_router(resend_router)
app.include_router(byok_router)


@app.get("/")
async def root():
    """Root endpoint — API discovery."""
    return {
        "service": "CounselConduit",
        "version": "3.0.0",
        "status": "operational",
        "docs": "/docs" if os.getenv("APP_ENV") == "development" else "disabled",
    }


@app.get("/health")
async def health():
    """Health check for Cloud Run / load balancer probes.

    Includes Firestore connectivity verification.
    """
    health_data = {
        "status": "healthy",
        "service": "counselconduit",
        "version": "3.1.0",
        "firestore": "unknown",
    }
    try:
        from google.cloud import firestore as _fs

        db = _fs.AsyncClient()
        # Lightweight read to verify connectivity
        await db.collection("_health").document("ping").get()
        health_data["firestore"] = "connected"
    except Exception as e:
        health_data["firestore"] = f"error: {type(e).__name__}"
        health_data["status"] = "degraded"
    return health_data


@app.post("/heartbeat")
async def heartbeat(request: Request):
    """Client session heartbeat — keeps session alive, resets dead-man's switch."""
    body = await request.json()
    session_id = body.get("session_id", "unknown")
    return {
        "status": "alive",
        "session_id": session_id,
        "server_time": time.time(),
    }


# ── Auth Middleware ─────────────────────────────────────────────────────────


def _verify_kovel_auth(x_kovel_auth: str | None) -> str:
    """Verify the Kovel authentication token.

    In production: validates Firebase Auth JWT via firebase_admin.
    In development: accepts any non-empty token.
    """
    if not x_kovel_auth:
        raise HTTPException(
            status_code=403,
            detail="Kovel Authentication Missing. Operation Terminated.",
        )

    # Production: Firebase Auth JWT verification
    if os.getenv("APP_ENV") != "development":
        try:
            import firebase_admin
            from firebase_admin import auth as firebase_auth

            # Initialize Firebase app if not already done
            if not firebase_admin._apps:
                firebase_admin.initialize_app()

            decoded = firebase_auth.verify_id_token(x_kovel_auth)
            attorney_id = decoded.get("uid", "")
            if not attorney_id:
                raise HTTPException(status_code=403, detail="Invalid token: no UID")
            return attorney_id

        except firebase_admin.exceptions.FirebaseError as e:
            logger.warning("Firebase JWT verification failed: %s", e)
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired authentication token.",
            ) from e
        except ImportError:
            logger.warning("firebase_admin not installed — falling back to dev mode")

    # Development: return token as attorney_id
    return x_kovel_auth


# ── Routes ─────────────────────────────────────────────────────────────────


@app.post("/enclave/v1/query", response_model=QueryResponse)
async def execute_query(
    request: QueryRequest,
    x_kovel_auth: str = Header(None),
):
    """Execute a Kovel-privileged query against the Gemini RAG pipeline.

    Synchronous endpoint — returns full response after completion.
    All responses pass through Judge #6 governance before returning.
    """
    attorney_id = _verify_kovel_auth(x_kovel_auth)
    request.attorney_id = attorney_id

    start = time.monotonic()
    result = await execute_privileged_query(request)
    elapsed_ms = int((time.monotonic() - start) * 1000)

    # Judge #6 governance gate
    governance = judge6_evaluate(result.response)
    if not governance.assessment.approved:
        result.response = governance.output_text  # Replace with blocked message
    elif governance.output_text != governance.input_text:
        result.response = governance.output_text  # Apply warnings

    # Audit log (async, non-blocking)
    try:
        await write_audit_log(
            AuditEntry(
                attorney_id=attorney_id,
                action="query",
                tokens_used=result.token_count,
                model=result.model,
            )
        )
        await update_attorney_usage(attorney_id, result.token_count)
    except Exception as e:
        logger.warning("audit_log_failed", error=str(e))

    logger.info(
        "query_completed",
        attorney_id=attorney_id,
        tokens=result.token_count,
        elapsed_ms=elapsed_ms,
        risk_score=governance.assessment.risk_score,
    )

    return result


@app.post("/enclave/v1/query/stream")
async def stream_query(
    request: QueryRequest,
    x_kovel_auth: str = Header(None),
):
    """Stream a Kovel-privileged query response via Server-Sent Events.

    Real-time streaming for chat-style interfaces.
    """
    attorney_id = _verify_kovel_auth(x_kovel_auth)
    request.attorney_id = attorney_id

    async def event_generator():
        async for chunk in stream_privileged_query(request):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/enclave/v1/health")
async def enclave_health():
    """Health check endpoint for Cloud Run and load balancers."""
    return {
        "status": "operational",
        "service": "CounselConduit Kovel Enclave",
        "version": "3.0.0",
        "timestamp": time.time(),
    }


@app.on_event("startup")
async def startup():
    logger.info("counselconduit_started", version="3.0.0")


@app.on_event("shutdown")
async def shutdown():
    logger.info("counselconduit_shutdown")
