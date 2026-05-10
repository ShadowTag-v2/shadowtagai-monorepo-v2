# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, EmailStr

router = APIRouter()


class EmailWebhookPayload(BaseModel):
  matter_id: str
  tenant_id: str
  sender: EmailStr
  subject: str
  body_text: str
  attachments: list[dict[str, Any]] = []


def parse_and_route_email(payload: EmailWebhookPayload):
  """
  Background worker:
  1. Extracts unstructured text.
  2. Runs through Gemini 3.1 Pro (via PgRagGraph or direct invoke) to find trigger dates/deadlines.
  3. Normalizes into a standard Internal LawTrack Event JSON.
  4. Writes to encrypted `ingested_events` Postgres table.
  """
  # Logic implementation deferred to Model Integration phase
  print(f"BJR-Enforced Parsing Triggered for Matter: {payload.matter_id}")
  pass


@router.post("/webhook/email")
async def ingest_email_event(
  payload: EmailWebhookPayload, background_tasks: BackgroundTasks
):
  """
  Primary ingestion funnel for Cor.LawTrack MVP.
  Receives parsed JSON from a provider like Sendgrid/Mailgun and immediately hands off to background queue
  to prevent webhook timeouts and ensure the Zero-Trust parser has time to work.
  """
  if not payload.matter_id or not payload.tenant_id:
    raise HTTPException(
      status_code=400, detail="Matter and Tenant ID required for routing."
    )

  background_tasks.add_task(parse_and_route_email, payload)

  return {
    "status": "queued",
    "message": "Email payload accepted for parsing and timeline generation.",
  }
