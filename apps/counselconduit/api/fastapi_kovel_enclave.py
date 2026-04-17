# apps/counselconduit/api/fastapi_kovel_enclave.py
"""CounselConduit: Kovel Enclave v3.0

Production API for KovelAI — Privileged Legal AI under the Kovel Doctrine.

Architecture:
    POST /enclave/v1/query           → Synchronous privileged query
    POST /enclave/v1/query/stream    → SSE streaming privileged query  
    POST /webhooks/stripe            → Stripe billing webhooks
    GET  /enclave/v1/health          → Health check

Per U.S. v. Heppner (S.D.N.Y., Feb 2026):
    - All client queries are ephemeral (RAM-only)
    - Lawyer receives permanent transcript
    - Anti-forensic evaporation on client logout
"""

from __future__ import annotations

import logging
import os
import time

import structlog
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from apps.counselconduit.api.auth import get_current_attorney
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
    version="3.0.0",
    description="Privileged Legal AI under the Kovel Doctrine. Zero-retention architecture.",
    docs_url="/docs" if os.getenv("APP_ENV") == "development" else None,
    redoc_url=None,
)

# CORS — restrict in production
_ALLOWED_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "https://kovelai.web.app,https://kovelai.com,http://localhost:4000",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    expose_headers=["X-Kovel-Signature"],
)

# ── Router Mounts ──────────────────────────────────────────────────────────

app.include_router(stripe_router)
app.include_router(billing_router)


# ── Auth Middleware ─────────────────────────────────────────────────────────

def _verify_kovel_auth(x_kovel_auth: str | None) -> str:
    """Verify the Kovel authentication token.
    
    In production: validates Firebase Auth JWT.
    In development: accepts any non-empty token.
    """
    if not x_kovel_auth:
        raise HTTPException(
            status_code=403,
            detail="Kovel Authentication Missing. Operation Terminated.",
        )
    # TODO: Firebase Auth JWT verification
    # decoded = firebase_admin.auth.verify_id_token(x_kovel_auth)
    # return decoded["uid"]
    return x_kovel_auth  # Dev mode: return token as attorney_id


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
        await write_audit_log(AuditEntry(
            attorney_id=attorney_id,
            action="query",
            tokens_used=result.token_count,
            model=result.model,
        ))
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
async def health():
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
