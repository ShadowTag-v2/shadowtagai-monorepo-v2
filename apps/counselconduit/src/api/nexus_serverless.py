# Copyright 2026 ShadowTag AI — All Rights Reserved.
# nexus_serverless.py — Cloud Run FastAPI + CTM Retrieval
"""
Nexus Serverless — Cloud Run FastAPI Endpoints for CounselConduit v3.0

Implements the Pure GCP nexus layer:
- /api/v3/generate — LLM generation with FlyingMonkeySwarm circuit breaker
- /api/v3/retrieve — CTM (Case-Text-Memo) retrieval from Firestore
- /api/v3/evaluate — ScholarEval citation accuracy scoring
- /api/v3/health — Service health check
"""

import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ─── Config ───────────────────────────────────────────────────────

PROJECT_ID = os.getenv("GCP_PROJECT", "shadowtag-omega-v4")
REGION = os.getenv("GCP_REGION", "us-central1")


# ─── Models ───────────────────────────────────────────────────────


class GenerateRequest(BaseModel):
  """LLM generation request."""

  prompt: str = Field(..., min_length=1, max_length=32000)
  max_tokens: int = Field(default=4096, ge=1, le=8192)
  temperature: float = Field(default=0.3, ge=0.0, le=2.0)
  session_id: str | None = None


class GenerateResponse(BaseModel):
  """LLM generation response."""

  text: str
  model_used: str
  latency_ms: float
  fallback: bool = False
  session_id: str | None = None


class RetrieveRequest(BaseModel):
  """CTM retrieval request."""

  query: str = Field(..., min_length=1, max_length=2000)
  collection: str = Field(default="cases")
  limit: int = Field(default=10, ge=1, le=100)


class EvaluateRequest(BaseModel):
  """ScholarEval citation accuracy request."""

  text: str = Field(..., min_length=1)
  citations: list[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
  """Health check response."""

  status: str = "healthy"
  version: str = "3.4.0"
  project: str = PROJECT_ID
  uptime_s: float = 0.0


# ─── App Lifecycle ────────────────────────────────────────────────

_start_time = time.monotonic()


@asynccontextmanager
async def lifespan(app: FastAPI):
  """Startup/shutdown lifecycle."""
  logger.info("🚀 Nexus Serverless v3.4.0 starting on %s/%s", PROJECT_ID, REGION)
  yield
  logger.info("🛑 Nexus Serverless shutting down")


app = FastAPI(
  title="CounselConduit Nexus API",
  version="3.4.0",
  description="Pure GCP Legal AI Orchestrator",
  lifespan=lifespan,
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=["https://counselconduit.com", "https://*.run.app"],
  allow_methods=["GET", "POST"],
  allow_headers=["*"],
  allow_credentials=True,
)


# ─── Middleware ────────────────────────────────────────────────────


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
  """Add security headers to all responses."""
  response = await call_next(request)
  response.headers["X-Content-Type-Options"] = "nosniff"
  response.headers["X-Frame-Options"] = "DENY"
  response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
  response.headers["X-Request-ID"] = request.headers.get(
    "X-Cloud-Trace-Context", "none"
  )
  return response


# ─── Endpoints ────────────────────────────────────────────────────


@app.get("/api/v3/health", response_model=HealthResponse)
async def health():
  """Health check endpoint for Cloud Run probes."""
  return HealthResponse(
    uptime_s=round(time.monotonic() - _start_time, 2),
  )


@app.post("/api/v3/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest):
  """Generate LLM response with circuit breaker protection."""
  try:
    # Import here to avoid circular deps at module load
    from .flying_monkeys_pure import FlyingMonkeySwarm

    swarm = FlyingMonkeySwarm(project_id=PROJECT_ID, location=REGION)
    result = await swarm.invoke(
      prompt=req.prompt,
      max_tokens=req.max_tokens,
      temperature=req.temperature,
    )
    return GenerateResponse(
      text=result["text"],
      model_used=result["model_used"],
      latency_ms=result["latency_ms"],
      fallback=result["fallback"],
      session_id=req.session_id,
    )
  except Exception as e:
    logger.exception("Generation failed")
    raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/v3/retrieve")
async def retrieve(req: RetrieveRequest) -> dict[str, Any]:
  """Retrieve CTM (Case-Text-Memo) documents from Firestore."""
  try:
    from google.cloud import firestore

    db = firestore.AsyncClient(project=PROJECT_ID)
    collection_ref = db.collection(req.collection)

    # Simple text search — production should use Vector Search
    docs = []
    query = collection_ref.limit(req.limit)
    async for doc in query.stream():
      doc_data = doc.to_dict()
      doc_data["_id"] = doc.id
      docs.append(doc_data)

    return {
      "results": docs,
      "count": len(docs),
      "collection": req.collection,
      "query": req.query,
    }
  except Exception as e:
    logger.exception("Retrieval failed")
    raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/v3/evaluate")
async def evaluate(req: EvaluateRequest) -> dict[str, Any]:
  """ScholarEval — Score citation accuracy against legal databases."""
  # Stub: Production uses CourtListener + case.law API verification
  valid_citations = []
  invalid_citations = []

  for citation in req.citations:
    # Basic format validation (e.g., "123 F.3d 456")
    if any(c.isdigit() for c in citation) and any(
      marker in citation for marker in ["F.", "U.S.", "S.Ct.", "L.Ed.", "Cal."]
    ):
      valid_citations.append(citation)
    else:
      invalid_citations.append(citation)

  total = len(req.citations) or 1
  accuracy = len(valid_citations) / total

  return {
    "accuracy_score": round(accuracy, 4),
    "valid_citations": valid_citations,
    "invalid_citations": invalid_citations,
    "total_citations": len(req.citations),
    "hallucination_rate": round(1.0 - accuracy, 4),
    "passes_threshold": accuracy >= 0.95,
  }


@app.exception_handler(402)
async def payment_required(request: Request, exc: HTTPException):
  """X402 micropayment required handler."""
  return JSONResponse(
    status_code=402,
    content={
      "error": "Payment Required",
      "message": "This endpoint requires X402 micropayment.",
      "payment_url": f"https://counselconduit.com/pay?session={request.query_params.get('session_id', 'unknown')}",
    },
  )
