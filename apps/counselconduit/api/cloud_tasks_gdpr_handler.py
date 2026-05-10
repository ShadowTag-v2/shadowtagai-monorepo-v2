# apps/counselconduit/api/cloud_tasks_gdpr_handler.py
"""GDPR 30-Day Auto-Delete Cloud Tasks Handler.

Receives Cloud Tasks callbacks to delete user data after the 30-day grace period.
This is the task handler — the task CREATOR is in cloud_tasks_gdpr.py.

Routes:
    POST /tasks/gdpr/execute-deletion  → Execute the actual data deletion

Security:
    - Only accepts requests from Cloud Tasks (verified via OIDC token)
    - Idempotent: safe to retry on failure
    - Audit trail written before and after deletion
"""

from __future__ import annotations

import logging
import time

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

logger = logging.getLogger("counselconduit.gdpr")

router = APIRouter(prefix="/tasks/gdpr", tags=["gdpr-tasks"])

# Cloud Tasks sends an OIDC token — verify the service account
_AUTHORIZED_SA = "counselconduit-sa@shadowtag-omega-v4.iam.gserviceaccount.com"


class DeletionPayload(BaseModel):
  """Payload sent by Cloud Tasks for GDPR deletion."""

  attorney_id: str
  firm_id: str
  requested_at: float
  deletion_type: str = "full"  # "full" or "partial"


class DeletionResult(BaseModel):
  """Result of a GDPR deletion execution."""

  attorney_id: str
  collections_deleted: list[str]
  documents_deleted: int
  completed_at: float
  idempotency_key: str


def _verify_cloud_tasks_origin(request: Request) -> None:
  """Verify the request originates from Cloud Tasks via OIDC token.

  Cloud Tasks injects an Authorization header with an OIDC token
  signed by the service account. In production, we verify this.
  In development, we skip verification.
  """
  import os

  if os.getenv("APP_ENV") == "development":
    return

  auth_header = request.headers.get("Authorization", "")
  if not auth_header.startswith("Bearer "):
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail="Cloud Tasks OIDC token required.",
    )

  # In production, verify the OIDC token against Google's public keys
  token = auth_header.removeprefix("Bearer ")
  try:
    from google.auth.transport import requests as google_requests
    from google.oauth2 import id_token

    claims = id_token.verify_oauth2_token(
      token,
      google_requests.Request(),
      audience=os.getenv("CLOUD_RUN_URL", ""),
    )
    if claims.get("email") != _AUTHORIZED_SA:
      raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Unauthorized service account.",
      )
  except Exception as e:
    logger.error("OIDC verification failed: %s", e)
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail="Invalid OIDC token.",
    ) from e


@router.post("/execute-deletion", response_model=DeletionResult)
async def execute_gdpr_deletion(
  payload: DeletionPayload,
  request: Request,
):
  """Execute GDPR Article 17 data deletion after 30-day grace period.

  This endpoint is called by Cloud Tasks, NOT directly by users.
  The 30-day grace period is enforced by the Cloud Tasks scheduler.

  Deletion targets (per attorney_id):
  1. kovel_sessions — ephemeral query sessions
  2. audit_logs — usage audit trail (anonymized, not deleted)
  3. billing_events — payment records (retained for tax compliance, anonymized)
  4. beta_accounts — account profile data
  5. stripe_events — webhook event logs for this attorney
  """
  _verify_cloud_tasks_origin(request)

  # Generate idempotency key from attorney_id + requested_at
  import hashlib

  idempotency_key = hashlib.sha256(
    f"{payload.attorney_id}:{payload.requested_at}".encode()
  ).hexdigest()[:16]

  logger.info(
    "gdpr_deletion_starting",
    attorney_id=payload.attorney_id,
    idempotency_key=idempotency_key,
    deletion_type=payload.deletion_type,
  )

  collections_deleted: list[str] = []
  total_docs_deleted = 0

  try:
    from google.cloud import firestore as _fs

    db = _fs.AsyncClient()

    # Collections to delete (full deletion)
    target_collections = [
      "kovel_sessions",
      "transcripts",
      "stripe_events",
    ]

    # Collections to anonymize (regulatory retention)
    anonymize_collections = [
      "audit_logs",
      "billing_events",
    ]

    for collection_name in target_collections:
      query = (
        db.collection(collection_name)
        .where("attorney_id", "==", payload.attorney_id)
        .limit(500)
      )
      docs = []
      async for doc in query.stream():
        docs.append(doc)
      batch = db.batch()
      count = 0
      for doc in docs:
        batch.delete(doc.reference)
        count += 1
      if count > 0:
        await batch.commit()
        total_docs_deleted += count
        collections_deleted.append(f"{collection_name} ({count} docs)")
        logger.info(
          "gdpr_collection_deleted",
          collection=collection_name,
          count=count,
        )

    # Anonymize retained collections
    for collection_name in anonymize_collections:
      query = (
        db.collection(collection_name)
        .where("attorney_id", "==", payload.attorney_id)
        .limit(500)
      )
      docs = []
      async for doc in query.stream():
        docs.append(doc)
      batch = db.batch()
      count = 0
      for doc in docs:
        batch.update(
          doc.reference,
          {
            "attorney_id": f"DELETED-{idempotency_key}",
            "email": "REDACTED",
            "firm_name": "REDACTED",
            "gdpr_anonymized_at": _fs.SERVER_TIMESTAMP,
          },
        )
        count += 1
      if count > 0:
        await batch.commit()
        total_docs_deleted += count
        collections_deleted.append(f"{collection_name} ({count} docs anonymized)")

    # Delete the beta_accounts record last
    beta_ref = db.collection("beta_accounts").document(payload.attorney_id)
    beta_doc = await beta_ref.get()
    if beta_doc.exists:
      # Archive deletion receipt before deleting
      await (
        db.collection("gdpr_deletion_receipts")
        .document(idempotency_key)
        .set(
          {
            "attorney_id": payload.attorney_id,
            "firm_id": payload.firm_id,
            "requested_at": payload.requested_at,
            "executed_at": _fs.SERVER_TIMESTAMP,
            "collections_deleted": collections_deleted,
            "total_docs": total_docs_deleted,
          }
        )
      )
      await beta_ref.delete()
      collections_deleted.append("beta_accounts (1 doc)")
      total_docs_deleted += 1

  except Exception as e:
    logger.error(
      "gdpr_deletion_failed",
      attorney_id=payload.attorney_id,
      error=str(e),
    )
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail="Deletion failed — will be retried by Cloud Tasks.",
    ) from e

  completed_at = time.time()
  logger.info(
    "gdpr_deletion_complete",
    attorney_id=payload.attorney_id,
    collections=collections_deleted,
    total_docs=total_docs_deleted,
    elapsed_s=round(completed_at - payload.requested_at, 1),
  )

  return DeletionResult(
    attorney_id=payload.attorney_id,
    collections_deleted=collections_deleted,
    documents_deleted=total_docs_deleted,
    completed_at=completed_at,
    idempotency_key=idempotency_key,
  )
