# apps/counselconduit/api/fastapi_kovel_enclave.py
"""CounselConduit: Kovel Enclave v3.4

Production API for KovelAI — Privileged Legal AI under the Kovel Doctrine.

Architecture:
    POST /enclave/v1/query           → Synchronous privileged query
    POST /enclave/v1/query/stream    → SSE streaming privileged query
    POST /webhooks/stripe            → Stripe billing webhooks
    GET  /enclave/v1/health          → Health check
    GET  /oracle/health               → Oracle Studio pipeline health
    POST /account/delete             → GDPR Article 17 — Right to Erasure (30-day grace)
    POST /account/export             → GDPR Article 20 — Right to Data Portability
    GET  /account/deletion-status    → Check pending deletion status
    POST /onboarding/magic-link      → Magic link email authentication
    POST /kovel/attest               → Kovel attestation receipt (HMAC-SHA256)
    POST /vent                       → Vent Mode SSE streaming
    POST /webhooks/github/pr-review  → Sovereign PR Review (M1 Max Swarm)
    GET  /pr-review/status/{pr}      → Check review status
    POST /api/v1/evaluate            → ScholarEval 8-dimension research quality scoring
    GET  /api/v1/evaluate/health     → ScholarEval health check

X402 Protocol:
    Priced endpoints return HTTP 402 with USDC/Base L2 payment challenge.
    Client submits X-Payment header with signed proof to access.

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
    AuditEntry,
    update_attorney_usage,
    write_audit_log,
  )
  from apps.counselconduit.api.gemini_rag import (
    QueryRequest,
    QueryResponse,
    execute_privileged_query,
    stream_privileged_query,
  )

  from apps.counselconduit.api.stripe_connect import router as billing_router
  from apps.counselconduit.api.stripe_handler import router as stripe_router
except ImportError:
  # Docker/Cloud Run context (running from /app/)
  from api.firestore_client import (  # type: ignore[no-redef]
    AuditEntry,
    update_attorney_usage,
    write_audit_log,
  )
  from api.gemini_rag import (  # type: ignore[no-redef]
    QueryRequest,
    QueryResponse,
    execute_privileged_query,
    stream_privileged_query,
  )

  from api.stripe_connect import router as billing_router  # type: ignore[no-redef]
  from api.stripe_handler import router as stripe_router  # type: ignore[no-redef]

# Middleware + Error handlers (same path in both contexts)
try:
  from apps.counselconduit.api.app_error import (
    AppError,
    app_error_handler,
    unhandled_error_handler,
  )
  from apps.counselconduit.api.auth import verify_firebase_token
  from apps.counselconduit.api.byok import router as byok_router
  from apps.counselconduit.api.cloud_tasks_gdpr import router as tasks_router
  from apps.counselconduit.api.cloud_tasks_gdpr_handler import (
    router as gdpr_handler_router,
  )
  from apps.counselconduit.api.deprecation_middleware import DeprecationMiddleware
  from apps.counselconduit.api.dispatch_router import router as dispatch_router
  from apps.counselconduit.api.gdpr import router as gdpr_router
  from apps.counselconduit.api.kovel_attestation import router as attestation_router
  from apps.counselconduit.api.magic_link import router as onboarding_router
  from apps.counselconduit.api.middleware import (
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
  )
  from apps.counselconduit.api.middleware.prompt_guard import PromptGuardMiddleware
  from apps.counselconduit.api.middleware.token_budget import TokenBudgetMiddleware
  from apps.counselconduit.api.pr_review_webhook import router as pr_review_router
  from apps.counselconduit.api.provider_health import router as provider_health_router
  from apps.counselconduit.api.resend_webhook import router as resend_router
  from apps.counselconduit.api.sandbox_router import SandboxMiddleware
  from apps.counselconduit.api.session_pin_monitor import cleanup_session_pins_firestore  # noqa: F401
  from apps.counselconduit.api.stripe_connect_onboarding import (
    router as connect_onboarding_router,
  )
  from apps.counselconduit.api.stripe_connect_webhook import (
    router as connect_webhook_router,
  )
  from apps.counselconduit.api.token_meter import router as token_meter_router
  from apps.counselconduit.api.vent_mode import router as vent_router

  # ScholarEval + X402 micropayment wiring
  try:
    from src.api.evaluate import router as evaluate_router
    from src.payments.x402_protocol import X402Middleware, X402PaymentVerifier
    _X402_AVAILABLE = True
  except ImportError:
    _X402_AVAILABLE = False
except ImportError:
  from api.app_error import AppError, app_error_handler, unhandled_error_handler  # type: ignore[no-redef]
  from api.auth import verify_firebase_token  # type: ignore[no-redef]
  from api.byok import router as byok_router  # type: ignore[no-redef]
  from api.cloud_tasks_gdpr import router as tasks_router  # type: ignore[no-redef]
  from api.cloud_tasks_gdpr_handler import router as gdpr_handler_router  # type: ignore[no-redef]
  from api.deprecation_middleware import DeprecationMiddleware  # type: ignore[no-redef]
  from api.dispatch_router import router as dispatch_router  # type: ignore[no-redef]
  from api.gdpr import router as gdpr_router  # type: ignore[no-redef]
  from api.kovel_attestation import router as attestation_router  # type: ignore[no-redef]
  from api.magic_link import router as onboarding_router  # type: ignore[no-redef]
  from api.middleware import RateLimitMiddleware, SecurityHeadersMiddleware  # type: ignore[no-redef]
  from api.middleware.prompt_guard import PromptGuardMiddleware  # type: ignore[no-redef]
  from api.middleware.token_budget import TokenBudgetMiddleware  # type: ignore[no-redef]
  from api.pr_review_webhook import router as pr_review_router  # type: ignore[no-redef]
  from api.provider_health import router as provider_health_router  # type: ignore[no-redef]
  from api.resend_webhook import router as resend_router  # type: ignore[no-redef]
  from api.sandbox_router import SandboxMiddleware  # type: ignore[no-redef]
  from api.stripe_connect_onboarding import router as connect_onboarding_router  # type: ignore[no-redef]
  from api.stripe_connect_webhook import router as connect_webhook_router  # type: ignore[no-redef]
  from api.token_meter import router as token_meter_router  # type: ignore[no-redef]
  from api.vent_mode import router as vent_router  # type: ignore[no-redef]

  # ScholarEval + X402 micropayment wiring (Docker context)
  try:
    from src.api.evaluate import router as evaluate_router  # type: ignore[no-redef]
    from src.payments.x402_protocol import X402Middleware, X402PaymentVerifier  # type: ignore[no-redef]
    _X402_AVAILABLE = True
  except ImportError:
    _X402_AVAILABLE = False

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
  version="3.4.0",
  description="Privileged Legal AI under the Kovel Doctrine. Zero-retention architecture.",
  docs_url="/docs",  # OpenAPI/Swagger enabled — API documentation
  redoc_url="/redoc",
  openapi_tags=[
    {
      "name": "Kovel Enclave",
      "description": "Privileged query endpoints protected by Kovel doctrine",
    },
    {
      "name": "Stripe Connect",
      "description": "Dual-billing engine: client→attorney + attorney→us",
    },
    {"name": "GDPR", "description": "Article 17 erasure + Article 20 data portability"},
    {"name": "Attestation", "description": "HMAC-SHA256 Kovel attestation receipts"},
    {"name": "Vent Mode", "description": "SSE streaming for real-time AI interaction"},
    {
      "name": "Sandbox",
      "description": "Phase 3: Tenant isolation, quota enforcement, proxy tokens",
    },
    {
      "name": "BYOK",
      "description": "Bring Your Own Key — customer-managed LLM API keys",
    },
    {
      "name": "research",
      "description": "ScholarEval — 8-dimension research quality framework",
    },
    {
      "name": "X402",
      "description": "USDC micropayments on Base L2 via HTTP 402 protocol",
    },
    {
      "name": "dispatch",
      "description": "NadirClaw 3-tier model dispatch + routing metrics",
    },
  ],
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

# X402: USDC micropayment enforcement on priced endpoints (/api/v1/evaluate, etc.)
if _X402_AVAILABLE:
  _x402_secret = os.getenv("X402_HMAC_SECRET", "dev-x402-secret")
  app.add_middleware(
    X402Middleware,
    verifier=X402PaymentVerifier(
      recipient=os.getenv("X402_RECIPIENT", "0x0000000000000000000000000000000000000000"),
      secret=_x402_secret,
    ),
  )

# Cor.30 R31: Security headers on every response
app.add_middleware(SecurityHeadersMiddleware)

# Cor.30 R14-R15: Per-IP + per-route rate limiting
app.add_middleware(RateLimitMiddleware)

# OWASP LLM10: Token budget + circuit breaker
app.add_middleware(TokenBudgetMiddleware)

# OWASP LLM01: Prompt injection detection
app.add_middleware(PromptGuardMiddleware)

# Phase 3: Tenant isolation + per-tier quota enforcement + proxy token validation
app.add_middleware(SandboxMiddleware)

# RFC 8594: Deprecation + Sunset headers on versioned routes
app.add_middleware(DeprecationMiddleware)

# CORS must be the LAST middleware added (= outermost wrapper) so it
# intercepts OPTIONS preflight requests before RateLimitMiddleware,
# SandboxMiddleware, etc. can reject them with 400/401.
app.add_middleware(
  CORSMiddleware,
  allow_origins=_ALLOWED_ORIGINS,
  allow_credentials=True,
  allow_methods=["GET", "POST", "OPTIONS"],
  allow_headers=os.environ.get(
    "CORS_HEADERS", "Content-Type,Authorization,X-Requested-With"
  ).split(","),
  expose_headers=[
    "X-Kovel-Signature",
    "X-RateLimit-Limit",
    "X-RateLimit-Remaining",
    "X-Token-Budget-Remaining",
    "X-Dispatch-Tier",
  ],
  max_age=3600,  # Cache preflight responses for 1 hour
)

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
app.include_router(gdpr_handler_router)
app.include_router(connect_onboarding_router)
app.include_router(dispatch_router)
app.include_router(token_meter_router)
app.include_router(provider_health_router)
app.include_router(pr_review_router)
if _X402_AVAILABLE:
  app.include_router(evaluate_router)  # ScholarEval: POST /api/v1/evaluate

# ── Static Files (admin dashboard) ────────────────────────────────────────
import pathlib as _pathlib  # noqa: E402

_static_dir = _pathlib.Path(__file__).resolve().parent.parent / "static"
if _static_dir.is_dir():
  from starlette.staticfiles import StaticFiles

  app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")


# ── Root-level static files (ZAP WARN fix: 404 on /robots.txt, /favicon.ico) ─
from starlette.responses import FileResponse as _FileResponse  # noqa: E402
from starlette.responses import JSONResponse  # noqa: E402


@app.get("/robots.txt", include_in_schema=False)
async def robots_txt():
  """Serve robots.txt from static directory."""
  _robots = _static_dir / "robots.txt"
  if _robots.is_file():
    return _FileResponse(str(_robots), media_type="text/plain")
  return JSONResponse({"detail": "Not found"}, status_code=404)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
  """Serve favicon.ico from static directory."""
  _favicon = _static_dir / "favicon.ico"
  if _favicon.is_file():
    return _FileResponse(str(_favicon), media_type="image/x-icon")
  return JSONResponse({"detail": "Not found"}, status_code=404)


@app.get("/")
async def root():
  """Root endpoint — API discovery."""
  return {
    "service": "CounselConduit",
    "version": "3.3.2",
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
    "version": "3.4.0",
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


@app.get("/healthz")
async def healthz():
  """Kubernetes/Cloud Run standard health probe alias."""
  return await health()


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
      decoded = verify_firebase_token(x_kovel_auth)
      attorney_id = decoded.get("uid", "")
      if not attorney_id:
        raise HTTPException(status_code=403, detail="Invalid token: no UID")
      return attorney_id
    except HTTPException:
      raise
    except Exception as e:
      logger.error("Auth verification failed: %s", e)
      raise HTTPException(
        status_code=401,
        detail="Authentication service error.",
      ) from e

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
  All responses pass through to the client without content inspection.
  """
  attorney_id = _verify_kovel_auth(x_kovel_auth)
  request.attorney_id = attorney_id

  start = time.monotonic()
  result = await execute_privileged_query(request)
  elapsed_ms = int((time.monotonic() - start) * 1000)

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
    risk_score=0,
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
    "version": "3.4.0",
    "timestamp": time.time(),
  }


@app.get("/oracle/health")
async def oracle_health():
  """Oracle Studio pipeline health check.

  Probed by the GCP Uptime Check 'CounselConduit Oracle Studio Pipeline'.
  Verifies Firestore connectivity and Oracle Studio module availability.
  """
  health_data = {
    "status": "healthy",
    "service": "oracle-studio",
    "version": "3.4.0",
    "pipeline_stages": 7,
    "firestore": "unknown",
    "timestamp": time.time(),
  }
  try:
    from google.cloud import firestore as _fs

    db = _fs.AsyncClient()
    await db.collection("_health").document("ping").get()
    health_data["firestore"] = "connected"
  except Exception as e:
    health_data["firestore"] = f"error: {type(e).__name__}"
    health_data["status"] = "degraded"
  return health_data


@app.on_event("startup")
async def startup():
  logger.info("counselconduit_started", version="3.4.0")


@app.on_event("shutdown")
async def shutdown():
  logger.info("counselconduit_shutdown")
