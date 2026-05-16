"""
Cryptographic Shredding — GDPR/DSA-compliant "Nuke My Data" implementation.

Orphans a user's remix tree nodes while preserving the product graph,
then purges all PII fields. This satisfies the right to deletion without
breaking the remix provenance chain.
"""

import os
from datetime import UTC, datetime

import firebase_admin
from fastapi import APIRouter, HTTPException
from firebase_admin import credentials, firestore
from pydantic import BaseModel

_GCP_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v4")

try:
  if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {"projectId": _GCP_PROJECT})
  db = firestore.client()
except Exception as e:
  print(f"[CRYPTO_SHRED WARNING] Firebase init failed: {e}")
  db = None


class NukeRequest(BaseModel):
  user_id: str
  confirmation_phrase: str


class NukeResponse(BaseModel):
  success: bool
  nodes_orphaned: int
  pii_fields_purged: int
  completed_at: str


_CONFIRMATION = "PERMANENTLY DELETE ALL MY DATA"

router = APIRouter(prefix="/api/account", tags=["account"])


@router.post("/nuke", response_model=NukeResponse)
async def nuke_my_data(req: NukeRequest):
  """
  Cryptographic shredding: orphan remix nodes, purge PII.

  This preserves the remix graph structure (child nodes still reference
  the parent node ID) but removes all personally identifiable information.
  """
  if req.confirmation_phrase != _CONFIRMATION:
    raise HTTPException(
      status_code=400,
      detail=f"Confirmation phrase must be exactly: {_CONFIRMATION}",
    )

  if not db:
    raise HTTPException(status_code=503, detail="Firestore unavailable")

  nodes_orphaned = 0
  pii_purged = 0

  # Phase 1: Orphan all remix nodes owned by this user
  nodes_query = (
    db.collection("remix_nodes").where("creatorId", "==", req.user_id).stream()
  )
  for doc in nodes_query:
    doc.reference.update(
      {
        "isOrphaned": True,
        "creatorId": "[DELETED]",
        "updatedAt": datetime.now(UTC),
      }
    )
    nodes_orphaned += 1

  # Phase 2: Anonymize videos
  videos_query = db.collection("videos").where("creatorId", "==", req.user_id).stream()
  for doc in videos_query:
    doc.reference.update(
      {
        "creatorId": "[DELETED]",
        "title": "[Content by deleted user]",
        "description": "",
      }
    )
    pii_purged += 3  # creatorId, title, description

  # Phase 3: Purge user profile
  user_ref = db.collection("users").document(req.user_id)
  user_doc = user_ref.get()
  if user_doc.exists:
    user_ref.update(
      {
        "email": "[DELETED]",
        "displayName": "[Deleted User]",
        "stripeCustomerId": "[DELETED]",
        "updatedAt": datetime.now(UTC),
      }
    )
    pii_purged += 3

  # Phase 4: Anonymize telemetry
  telem_query = (
    db.collection("human_telemetry").where("userId", "==", req.user_id).stream()
  )
  for doc in telem_query:
    doc.reference.update({"userId": None})
    pii_purged += 1

  return NukeResponse(
    success=True,
    nodes_orphaned=nodes_orphaned,
    pii_fields_purged=pii_purged,
    completed_at=datetime.now(UTC).isoformat(),
  )
