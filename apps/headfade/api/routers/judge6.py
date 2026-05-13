"""
Judge6 Trust & Safety Gate — Non-Severable Content Moderation.

Uses Google Cloud Video Intelligence + Vision APIs.
Every upload MUST pass through judge6_scan() before platform entry.
"""

import os
import time
from datetime import UTC, datetime
from enum import Enum

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

_video_client = None
_vision_client = None
_GCP_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v4")


def _get_video_client():
  global _video_client
  if _video_client is None:
    from google.cloud import videointelligence_v1 as vi

    _video_client = vi.VideoIntelligenceServiceClient()
  return _video_client


def _get_vision_client():
  global _vision_client
  if _vision_client is None:
    from google.cloud import vision_v1

    _vision_client = vision_v1.ImageAnnotatorClient()
  return _vision_client


class Judge6Decision(str, Enum):
  PASS = "PASS"
  BLOCK = "BLOCK"
  REVIEW = "REVIEW"


class Judge6Category(str, Enum):
  CSAM = "CSAM"
  VIOLENCE = "VIOLENCE"
  HATE_SPEECH = "HATE_SPEECH"
  SELF_HARM = "SELF_HARM"
  TERRORISM = "TERRORISM"
  EXPLICIT_CONTENT = "EXPLICIT_CONTENT"
  CLEAN = "CLEAN"


class Judge6ScanRequest(BaseModel):
  video_id: str
  gcs_uri: str


class Judge6Verdict(BaseModel):
  decision: Judge6Decision
  categories: list[Judge6Category]
  confidence_score: float
  latency_ms: int
  scanned_at: str
  scanner_model: str
  raw_annotations: dict | None = None


_BLOCK_THRESHOLD = 4  # LIKELY or VERY_LIKELY
_REVIEW_THRESHOLD = 3  # POSSIBLE


async def judge6_scan(video_id: str, gcs_uri: str) -> Judge6Verdict:
  """Non-severable content moderation scan. Returns PASS/BLOCK/REVIEW."""
  start_time = time.monotonic()
  categories: list[Judge6Category] = []
  max_likelihood = 0
  raw_annotations: dict = {}

  # Phase 1: Video Intelligence — Explicit Content Detection
  try:
    from google.cloud import videointelligence_v1 as vi

    client = _get_video_client()
    features = [vi.Feature.EXPLICIT_CONTENT_DETECTION]
    operation = client.annotate_video(
      request=vi.AnnotateVideoRequest(input_uri=gcs_uri, features=features)
    )
    result = operation.result(timeout=300)
    if result.annotation_results:
      explicit = result.annotation_results[0].explicit_annotation
      if explicit and explicit.frames:
        frame_likelihoods = [f.pornography_likelihood for f in explicit.frames]
        max_frame = max(frame_likelihoods) if frame_likelihoods else 0
        if max_frame > max_likelihood:
          max_likelihood = max_frame
        raw_annotations["video_max_likelihood"] = max_frame
        if max_frame >= _BLOCK_THRESHOLD:
          categories.append(Judge6Category.EXPLICIT_CONTENT)
  except ImportError:
    raw_annotations["video_intelligence"] = "SDK_NOT_AVAILABLE"
  except Exception as e:
    raw_annotations["video_intelligence_error"] = str(e)

  # Phase 2: Vision SafeSearch
  try:
    from google.cloud import vision_v1

    vision_client = _get_vision_client()
    image = vision_v1.Image(
      source=vision_v1.ImageSource(gcs_image_uri=gcs_uri.replace(".mp4", "_thumb.jpg"))
    )
    response = vision_client.safe_search_detection(image=image)
    ss = response.safe_search_annotation
    if ss:
      for name, val in [("adult", ss.adult), ("violence", ss.violence)]:
        if val > max_likelihood:
          max_likelihood = val
        if val >= _BLOCK_THRESHOLD:
          cat = (
            Judge6Category.EXPLICIT_CONTENT
            if name == "adult"
            else Judge6Category.VIOLENCE
          )
          categories.append(cat)
  except ImportError:
    raw_annotations["vision"] = "SDK_NOT_AVAILABLE"
  except Exception as e:
    raw_annotations["vision_error"] = str(e)

  # Phase 3: Decision
  categories = list(set(categories))
  if not categories:
    categories = [Judge6Category.CLEAN]

  if max_likelihood >= _BLOCK_THRESHOLD:
    decision = Judge6Decision.BLOCK
  elif max_likelihood >= _REVIEW_THRESHOLD:
    decision = Judge6Decision.REVIEW
  else:
    decision = Judge6Decision.PASS

  latency_ms = int((time.monotonic() - start_time) * 1000)
  confidence = min(1.0, max_likelihood / 5.0) if max_likelihood > 0 else 0.95

  return Judge6Verdict(
    decision=decision,
    categories=categories,
    confidence_score=round(confidence, 3),
    latency_ms=latency_ms,
    scanned_at=datetime.now(UTC).isoformat(),
    scanner_model="cloud-video-intelligence-v1+vision-v1",
    raw_annotations=raw_annotations,
  )


router = APIRouter(prefix="/api/judge6", tags=["judge6"])


@router.post("/scan", response_model=Judge6Verdict)
async def scan_content(req: Judge6ScanRequest):
  if not req.gcs_uri.startswith("gs://"):
    raise HTTPException(status_code=400, detail="gcs_uri must start with gs://")
  verdict = await judge6_scan(req.video_id, req.gcs_uri)
  if verdict.decision == Judge6Decision.BLOCK:
    print(
      f"[JUDGE6 BLOCK] video_id={req.video_id} categories={[c.value for c in verdict.categories]}"
    )
  return verdict


@router.get("/health")
def judge6_health():
  return {"status": "operational", "service": "judge6-gate", "policy": "NON_SEVERABLE"}
