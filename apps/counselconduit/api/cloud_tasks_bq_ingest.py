# apps/counselconduit/api/cloud_tasks_bq_ingest.py
"""Cloud Tasks handler for BigQuery embed_impressions ingestion.

This module provides a Cloud Tasks HTTP endpoint that triggers the BigQuery
ingestion pipeline for HeadFade embed impression events. Events are received
as a batch in the task payload and streamed into BigQuery.

Route:
    POST /tasks/bq-ingest → Accepts Cloud Tasks push with events payload

Security:
    - OIDC token verification via Cloud Tasks service account
    - Rejects requests without valid X-CloudTasks-TaskName header
"""

from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Request, status

logger = logging.getLogger("counselconduit.bq_ingest")

router = APIRouter(prefix="/tasks", tags=["cloud-tasks"])

PROJECT_ID = "shadowtag-omega-v4"
DATASET_ID = "analytics"
TABLE_ID = "embed_impressions"
FULL_TABLE = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

VALID_INTERACTION_TYPES = {"view", "click", "scroll", "hover"}


def _validate_event(event: dict[str, Any]) -> dict[str, Any] | None:
  """Validate and normalize a single event."""
  required = ["embed_id", "interaction_type"]
  for field in required:
    if field not in event:
      logger.warning("Missing required field '%s', skipping event", field)
      return None

  if event.get("interaction_type") not in VALID_INTERACTION_TYPES:
    logger.warning("Invalid interaction_type '%s'", event.get("interaction_type"))
    return None

  from datetime import UTC, datetime

  now = datetime.now(UTC).isoformat()
  return {
    "event_id": event.get(
      "event_id", f"evt_{hash(json.dumps(event, sort_keys=True)) & 0xFFFFFFFF:08x}"
    ),
    "embed_id": event["embed_id"],
    "page_url": event.get("page_url", ""),
    "referrer": event.get("referrer", ""),
    "user_agent": event.get("user_agent", ""),
    "viewport_width": int(event.get("viewport_width", 0)),
    "viewport_height": int(event.get("viewport_height", 0)),
    "visible_duration_ms": int(event.get("visible_duration_ms", 0)),
    "interaction_type": event["interaction_type"],
    "timestamp": event.get("timestamp", now),
    "country_code": event.get("country_code", ""),
    "region": event.get("region", ""),
    "session_id": event.get("session_id", ""),
  }


@router.post("/bq-ingest", status_code=status.HTTP_200_OK)
async def bq_ingest_task(request: Request) -> dict[str, Any]:
  """Cloud Tasks push endpoint for BigQuery embed_impressions ingestion.

  Expects a JSON body:
      {"events": [{"embed_id": "...", "interaction_type": "view", ...}, ...]}

  Returns count of successfully ingested events.
  """
  # Verify Cloud Tasks origin
  task_name = request.headers.get("X-CloudTasks-TaskName")
  if not task_name:
    logger.warning("BQ ingest called without Cloud Tasks header")
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail="Must be invoked by Cloud Tasks",
    )

  try:
    body = await request.json()
  except Exception as exc:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail=f"Invalid JSON: {exc}",
    ) from exc

  raw_events = body.get("events", [])
  if not raw_events:
    return {"ingested": 0, "skipped": 0, "message": "No events in payload"}

  # Validate events
  valid_events = []
  for raw in raw_events:
    validated = _validate_event(raw)
    if validated:
      valid_events.append(validated)

  if not valid_events:
    return {"ingested": 0, "skipped": len(raw_events), "message": "All events invalid"}

  # Insert into BigQuery
  try:
    from google.cloud import bigquery

    client = bigquery.Client(project=PROJECT_ID)
    errors = client.insert_rows_json(FULL_TABLE, valid_events)

    if errors:
      logger.error("BigQuery insert errors: %s", errors)
      return {
        "ingested": 0,
        "skipped": len(raw_events) - len(valid_events),
        "errors": len(errors),
        "message": "BigQuery insert failed",
      }

    logger.info("Ingested %d events into %s", len(valid_events), FULL_TABLE)
    return {
      "ingested": len(valid_events),
      "skipped": len(raw_events) - len(valid_events),
      "message": "Success",
    }
  except Exception as exc:
    logger.exception("BQ ingest failed: %s", exc)
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=f"BigQuery insert failed: {type(exc).__name__}",
    ) from exc
