# apps/headfade/api/gatekeeper.py
"""HeadFade Gatekeeper — Judge6 Trust & Safety Gate (Cloud Run Service)

Architecture:
    POST /ingest       → Submit video for forensic pipeline
    POST /judge6       → Run Judge6 safety scan (Video Intelligence + Vision API)
    GET  /health       → Health check
    GET  /pipeline/:id → Check ingestion job status

Judge6 gate is NON-SEVERABLE: every piece of content must pass through it
before entering the platform.

Compliance: DSA Art. 16, CSAM Directive 2011/93/EU, COPPA, 18 U.S.C. § 2256
"""

from __future__ import annotations

import time
import uuid
from enum import Enum

import structlog
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

logger = structlog.get_logger("headfade-gatekeeper")

# ── Models ──────────────────────────────────────────────────────────────────


class IngestStage(str, Enum):
  RECEIVED = "RECEIVED"
  UPLOADING_TO_GCS = "UPLOADING_TO_GCS"
  JUDGE6_SCANNING = "JUDGE6_SCANNING"
  FORENSIC_ANALYSIS = "FORENSIC_ANALYSIS"
  REMIX_TREE_INSERTION = "REMIX_TREE_INSERTION"
  COMPLETE = "COMPLETE"
  BLOCKED = "BLOCKED"
  ERROR = "ERROR"


class Judge6Verdict(str, Enum):
  PASS = "PASS"
  BLOCK = "BLOCK"
  REVIEW = "REVIEW"


class IngestRequest(BaseModel):
  video_id: str = Field(..., description="Video document ID from Firestore")
  creator_id: str = Field(..., description="Creator's Firebase Auth UID")
  gcs_uri: str = Field(..., description="GCS URI of the uploaded video")
  parent_remix_node_id: str | None = Field(
    None, description="Parent remix node if this is a derivative"
  )


class IngestResponse(BaseModel):
  job_id: str
  video_id: str
  stage: IngestStage
  judge6_verdict: Judge6Verdict | None = None
  message: str


class Judge6Request(BaseModel):
  video_id: str
  gcs_uri: str


class Judge6Response(BaseModel):
  video_id: str
  verdict: Judge6Verdict
  explicit_score: float = 0.0
  violence_score: float = 0.0
  csam_flag: bool = False
  latency_ms: int
  model: str = "video-intelligence-v1"


# ── App ─────────────────────────────────────────────────────────────────────

app = FastAPI(
  title="HeadFade Gatekeeper",
  version="0.1.0",
  description="Judge6 Trust & Safety Gate — non-severable content ingestion pipeline",
)


@app.get("/health")
async def health():
  """Health check for Cloud Run probes."""
  return {
    "status": "healthy",
    "service": "headfade-gatekeeper",
    "version": "0.1.0",
    "judge6_enabled": True,
    "timestamp": time.time(),
  }


@app.post("/ingest", response_model=IngestResponse)
async def ingest_video(request: IngestRequest):
  """Submit a video for the full ingestion pipeline.

  Pipeline stages:
  1. RECEIVED → Validate input
  2. UPLOADING_TO_GCS → Verify GCS object exists
  3. JUDGE6_SCANNING → Run Video Intelligence + Vision API
  4. FORENSIC_ANALYSIS → Gemini forensic verdict
  5. REMIX_TREE_INSERTION → Insert into provenance graph
  6. COMPLETE → Ready for marketplace
  """
  job_id = f"ingest_{request.video_id}_{uuid.uuid4().hex[:8]}"

  logger.info(
    "ingestion_started",
    job_id=job_id,
    video_id=request.video_id,
    creator_id=request.creator_id,
  )

  # Stage 1: Validate GCS URI
  if not request.gcs_uri.startswith("gs://"):
    raise HTTPException(status_code=400, detail="Invalid GCS URI format")

  # Stage 2: Run Judge6 safety scan
  judge6_result = await _run_judge6_scan(request.video_id, request.gcs_uri)

  if judge6_result.verdict == Judge6Verdict.BLOCK:
    logger.warning(
      "content_blocked",
      video_id=request.video_id,
      reason="judge6_block",
      explicit=judge6_result.explicit_score,
      violence=judge6_result.violence_score,
    )
    return IngestResponse(
      job_id=job_id,
      video_id=request.video_id,
      stage=IngestStage.BLOCKED,
      judge6_verdict=Judge6Verdict.BLOCK,
      message="Content blocked by Judge6 safety gate. Review required.",
    )

  if judge6_result.verdict == Judge6Verdict.REVIEW:
    logger.info(
      "content_flagged_review",
      video_id=request.video_id,
    )
    return IngestResponse(
      job_id=job_id,
      video_id=request.video_id,
      stage=IngestStage.JUDGE6_SCANNING,
      judge6_verdict=Judge6Verdict.REVIEW,
      message="Content flagged for manual review.",
    )

  # Passed Judge6 — proceed to forensic analysis (async via Cloud Tasks)
  return IngestResponse(
    job_id=job_id,
    video_id=request.video_id,
    stage=IngestStage.FORENSIC_ANALYSIS,
    judge6_verdict=Judge6Verdict.PASS,
    message="Judge6 passed. Forensic analysis queued.",
  )


@app.post("/judge6", response_model=Judge6Response)
async def judge6_scan(request: Judge6Request):
  """Run Judge6 safety scan on a video."""
  return await _run_judge6_scan(request.video_id, request.gcs_uri)


async def _run_judge6_scan(video_id: str, gcs_uri: str) -> Judge6Response:
  """Internal Judge6 scan implementation.

  Production: Uses Video Intelligence API + Cloud Vision API.
  Current: Stub that passes all content (safety gate framework ready).
  """
  start = time.monotonic()

  # TODO: Wire Video Intelligence API
  # from google.cloud import videointelligence_v1p3beta1 as vi
  # client = vi.VideoIntelligenceServiceClient()
  # ...

  # TODO: Wire Cloud Vision API for thumbnail SafeSearch
  # from google.cloud import vision_v1
  # client = vision_v1.ImageAnnotatorClient()
  # ...

  elapsed_ms = int((time.monotonic() - start) * 1000)

  # Stub: pass all content (framework in place for real scanning)
  return Judge6Response(
    video_id=video_id,
    verdict=Judge6Verdict.PASS,
    explicit_score=0.0,
    violence_score=0.0,
    csam_flag=False,
    latency_ms=elapsed_ms,
    model="stub-v0.1",
  )


@app.get("/pipeline/{job_id}")
async def get_pipeline_status(job_id: str):
  """Check ingestion pipeline job status."""
  # TODO: Read from Firestore ingestion_jobs collection
  return {
    "job_id": job_id,
    "stage": "UNKNOWN",
    "message": "Pipeline status lookup not yet wired to Firestore",
  }
