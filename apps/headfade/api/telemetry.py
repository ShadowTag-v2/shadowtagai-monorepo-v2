# apps/headfade/api/telemetry.py
"""HeadFade Telemetry — BQ Embed Impressions via Cloud Tasks.

Dispatches embed impression events to the CounselConduit BQ ingestion
endpoint via Cloud Tasks (OIDC-authenticated HTTP target).

Architecture:
    HeadFade embed event → Cloud Tasks → POST /tasks/bq-ingest → BigQuery
"""

from __future__ import annotations

import logging
import os
import time
import uuid

from google.cloud import tasks_v2

logger = logging.getLogger("headfade.telemetry")

# Configuration
_PROJECT = os.getenv("GCP_PROJECT", "shadowtag-omega-v4")
_LOCATION = os.getenv("GCP_LOCATION", "us-central1")
_QUEUE = os.getenv("BQ_INGEST_QUEUE", "bq-ingest-queue")
_TARGET_URL = os.getenv(
  "BQ_INGEST_URL",
  "https://counselconduit-767252945109.us-central1.run.app/tasks/bq-ingest",
)
_SERVICE_ACCOUNT = os.getenv(
  "CLOUD_TASKS_SA",
  "counselconduit-sa@shadowtag-omega-v4.iam.gserviceaccount.com",
)

# Lazy client singleton
_client: tasks_v2.CloudTasksClient | None = None


def _get_client() -> tasks_v2.CloudTasksClient:
  """Get or create the Cloud Tasks client singleton."""
  global _client
  if _client is None:
    _client = tasks_v2.CloudTasksClient()
  return _client


def dispatch_embed_impression(
  *,
  video_id: str,
  creator_id: str,
  viewer_id: str | None = None,
  embed_url: str,
  referrer: str | None = None,
) -> str | None:
  """Dispatch an embed impression event to BigQuery via Cloud Tasks.

  Args:
      video_id: The video being viewed.
      creator_id: The video creator's UID.
      viewer_id: The viewer's UID (None if anonymous).
      embed_url: The URL where the embed is displayed.
      referrer: HTTP referrer if available.

  Returns:
      The Cloud Tasks task name if dispatched, None on error.
  """
  import json

  try:
    client = _get_client()
    parent = client.queue_path(_PROJECT, _LOCATION, _QUEUE)

    payload = {
      "event_type": "embed_impression",
      "event_id": f"emb_{uuid.uuid4().hex[:12]}",
      "video_id": video_id,
      "creator_id": creator_id,
      "viewer_id": viewer_id or "anonymous",
      "embed_url": embed_url,
      "referrer": referrer or "",
      "timestamp": time.time(),
    }

    task = tasks_v2.Task(
      http_request=tasks_v2.HttpRequest(
        http_method=tasks_v2.HttpMethod.POST,
        url=_TARGET_URL,
        headers={"Content-Type": "application/json"},
        body=json.dumps(payload).encode(),
        oidc_token=tasks_v2.OidcToken(
          service_account_email=_SERVICE_ACCOUNT,
          audience=_TARGET_URL,
        ),
      ),
    )

    response = client.create_task(
      request=tasks_v2.CreateTaskRequest(parent=parent, task=task)
    )
    logger.info(
      "embed_impression_dispatched",
      extra={
        "task_name": response.name,
        "video_id": video_id,
      },
    )
    return response.name

  except Exception:
    logger.exception("Failed to dispatch embed impression event")
    return None
