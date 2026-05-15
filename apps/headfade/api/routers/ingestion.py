"""
HeadFade Ingestion Pipeline — Serverless Content Ingest Orchestrator.

State machine: RECEIVED → UPLOADING_TO_GCS → JUDGE6_SCANNING →
               FORENSIC_ANALYSIS → REMIX_TREE_INSERTION → COMPLETE
               (or BLOCKED / ERROR at any stage)

Zero static API keys — all auth via ADC (Workload Identity Federation).
"""

import os
import uuid
from datetime import UTC, datetime
from enum import Enum

import firebase_admin
from fastapi import APIRouter, HTTPException
from firebase_admin import credentials, firestore
from google.cloud import storage
from pydantic import BaseModel

from routers.judge6 import Judge6Decision, judge6_scan

_GCP_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v4")
_GCS_BUCKET = os.environ.get("HEADFADE_GCS_BUCKET", "headfade-cdn-origin")
_SIGNED_URL_EXPIRY = int(os.environ.get("SIGNED_URL_EXPIRY_SECS", "900"))

# Firestore client (reuse from global init if available)
try:
  if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {"projectId": _GCP_PROJECT})
  db = firestore.client()
except Exception as e:
  print(f"[INGESTION WARNING] Firebase init failed: {e}")
  db = None

# GCS client for signed URL generation
_gcs_client = None


def _get_gcs_client():
  global _gcs_client
  if _gcs_client is None:
    _gcs_client = storage.Client(project=_GCP_PROJECT)
  return _gcs_client


class IngestionStage(str, Enum):
  RECEIVED = "RECEIVED"
  UPLOADING_TO_GCS = "UPLOADING_TO_GCS"
  JUDGE6_SCANNING = "JUDGE6_SCANNING"
  FORENSIC_ANALYSIS = "FORENSIC_ANALYSIS"
  REMIX_TREE_INSERTION = "REMIX_TREE_INSERTION"
  COMPLETE = "COMPLETE"
  BLOCKED = "BLOCKED"
  ERROR = "ERROR"


class IngestRequest(BaseModel):
  title: str
  description: str
  ground_truth: str = "UNKNOWN"
  creator_id: str
  parent_remix_node_id: str | None = None


class IngestResponse(BaseModel):
  job_id: str
  video_id: str
  signed_upload_url: str
  stage: IngestionStage


class IngestStatusResponse(BaseModel):
  job_id: str
  video_id: str
  stage: IngestionStage
  judge6_decision: str | None = None
  error: str | None = None


router = APIRouter(prefix="/api/ingest", tags=["ingestion"])


def _generate_signed_upload_url(video_id: str) -> str:
  """Generate a GCS signed URL for direct client-side upload."""
  try:
    client = _get_gcs_client()
    bucket = client.bucket(_GCS_BUCKET)
    blob = bucket.blob(f"uploads/{video_id}.mp4")
    url = blob.generate_signed_url(
      version="v4",
      expiration=_SIGNED_URL_EXPIRY,
      method="PUT",
      content_type="video/mp4",
    )
    return url
  except Exception as e:
    raise HTTPException(
      status_code=500,
      detail=f"Failed to generate signed upload URL: {e}",
    )


def _create_ingestion_job(job_id: str, video_id: str, req: IngestRequest) -> None:
  """Create the ingestion job and video document in Firestore."""
  if not db:
    return

  batch = db.batch()
  now = datetime.now(UTC)

  # Create video document
  video_ref = db.collection("videos").document(video_id)
  batch.set(
    video_ref,
    {
      "id": video_id,
      "creatorId": req.creator_id,
      "gcsUri": f"gs://{_GCS_BUCKET}/uploads/{video_id}.mp4",
      "title": req.title,
      "description": req.description,
      "groundTruth": req.ground_truth.upper(),
      "status": "UPLOADING",
      "createdAt": now,
    },
  )

  # Create ingestion job document
  job_ref = db.collection("ingestion_jobs").document(job_id)
  batch.set(
    job_ref,
    {
      "id": job_id,
      "videoId": video_id,
      "creatorId": req.creator_id,
      "stage": IngestionStage.RECEIVED.value,
      "parentRemixNodeId": req.parent_remix_node_id,
      "createdAt": now,
      "updatedAt": now,
    },
  )

  batch.commit()


def _update_job_stage(
  job_id: str,
  stage: IngestionStage,
  extra_fields: dict | None = None,
) -> None:
  """Update the ingestion job stage in Firestore."""
  if not db:
    return
  update = {"stage": stage.value, "updatedAt": datetime.now(UTC)}
  if extra_fields:
    update.update(extra_fields)
  db.collection("ingestion_jobs").document(job_id).update(update)


@router.post("/start", response_model=IngestResponse)
async def start_ingestion(req: IngestRequest):
  """
  Initiate content ingestion. Returns a signed GCS upload URL.

  Flow:
  1. Generate video ID and job ID
  2. Create Firestore documents
  3. Return signed URL for direct upload
  4. Client uploads to GCS, then calls /confirm to trigger Judge6
  """
  video_id = str(uuid.uuid4()).replace("-", "")[:24]
  job_id = f"ingest_{video_id}"

  signed_url = _generate_signed_upload_url(video_id)
  _create_ingestion_job(job_id, video_id, req)

  return IngestResponse(
    job_id=job_id,
    video_id=video_id,
    signed_upload_url=signed_url,
    stage=IngestionStage.RECEIVED,
  )


@router.post("/confirm/{job_id}")
async def confirm_upload_and_scan(job_id: str):
  """
  Confirm upload completion and trigger Judge6 + forensic analysis.

  Called after the client successfully uploads to GCS via the signed URL.
  This is where the NON-SEVERABLE Judge6 gate is enforced.
  """
  if not db:
    raise HTTPException(status_code=503, detail="Firestore unavailable")

  # Fetch the job
  job_doc = db.collection("ingestion_jobs").document(job_id).get()
  if not job_doc.exists:
    raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

  job = job_doc.to_dict()
  video_id = job["videoId"]
  gcs_uri = f"gs://{_GCS_BUCKET}/uploads/{video_id}.mp4"

  # --- JUDGE6 GATE (NON-SEVERABLE) ---
  _update_job_stage(job_id, IngestionStage.JUDGE6_SCANNING)
  db.collection("videos").document(video_id).update({"status": "SCANNING"})

  verdict = await judge6_scan(video_id, gcs_uri)

  if verdict.decision == Judge6Decision.BLOCK:
    _update_job_stage(
      job_id,
      IngestionStage.BLOCKED,
      {"judge6Verdict": verdict.model_dump()},
    )
    db.collection("videos").document(video_id).update({"status": "BLOCKED"})
    return {
      "status": "BLOCKED",
      "job_id": job_id,
      "reason": "Content blocked by Judge6 Trust & Safety gate",
      "categories": [c.value for c in verdict.categories],
    }

  # --- FORENSIC ANALYSIS ---
  _update_job_stage(
    job_id,
    IngestionStage.FORENSIC_ANALYSIS,
    {"judge6Verdict": verdict.model_dump()},
  )
  db.collection("videos").document(video_id).update({"status": "ANALYZING"})

  # Note: Forensic analysis is handled async by the arbiter engine.
  # For now, we mark the pipeline as progressing to the next stage.

  # --- REMIX TREE INSERTION ---
  _update_job_stage(job_id, IngestionStage.REMIX_TREE_INSERTION)

  parent_id = job.get("parentRemixNodeId")
  parent_depth = 0
  if parent_id and db:
    parent_doc = db.collection("remix_nodes").document(parent_id).get()
    if parent_doc.exists:
      parent_depth = parent_doc.to_dict().get("depth", 0)
      # Increment child count
      db.collection("remix_nodes").document(parent_id).update(
        {"childCount": firestore.Increment(1)}
      )

  # Create remix node
  import hashlib

  content_hash = hashlib.sha256(f"{video_id}:{gcs_uri}".encode()).hexdigest()
  node_id = f"rn_{video_id}"

  now = datetime.now(UTC)
  db.collection("remix_nodes").document(node_id).set(
    {
      "id": node_id,
      "videoId": video_id,
      "parentNodeId": parent_id,
      "creatorId": job["creatorId"],
      "nodeType": "REMIX" if parent_id else "ORIGINAL",
      "contentHash": content_hash,
      "depth": parent_depth + 1 if parent_id else 0,
      "childCount": 0,
      "isOrphaned": False,
      "createdAt": now,
      "updatedAt": now,
    }
  )

  # Complete
  _update_job_stage(
    job_id,
    IngestionStage.COMPLETE,
    {"remixNodeId": node_id},
  )
  db.collection("videos").document(video_id).update(
    {
      "status": "PUBLISHED",
      "remixNodeId": node_id,
    }
  )

  return {
    "status": "COMPLETE",
    "job_id": job_id,
    "video_id": video_id,
    "judge6_decision": verdict.decision.value,
    "remix_node_id": node_id,
  }


@router.get("/status/{job_id}", response_model=IngestStatusResponse)
async def get_ingestion_status(job_id: str):
  """Check the status of an ingestion job."""
  if not db:
    raise HTTPException(status_code=503, detail="Firestore unavailable")

  doc = db.collection("ingestion_jobs").document(job_id).get()
  if not doc.exists:
    raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

  job = doc.to_dict()
  j6 = job.get("judge6Verdict", {})

  return IngestStatusResponse(
    job_id=job_id,
    video_id=job["videoId"],
    stage=IngestionStage(job["stage"]),
    judge6_decision=j6.get("decision") if j6 else None,
    error=job.get("error"),
  )
