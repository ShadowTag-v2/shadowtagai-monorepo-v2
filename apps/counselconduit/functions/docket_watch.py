# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Continuous Docket Watch — Cloud Function for Court Polling.

Polls CourtListener and PACER RSS feeds for new filings in tracked cases.
Designed to run as a Google Cloud Function on a 15-minute Cloud Scheduler trigger.

Architecture:
    Cloud Scheduler (every 15 min) → Cloud Function → CourtListener API
    → Firestore (docket_events/) → Pub/Sub notification → CounselConduit

Environment Variables:
    COURTLISTENER_API_TOKEN: CourtListener API token for higher rate limits
    GOOGLE_CLOUD_PROJECT: GCP project ID (shadowtag-omega-v4)
    NOTIFICATION_TOPIC: Pub/Sub topic for docket alerts
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

import functions_framework
import httpx
from google.cloud import firestore, pubsub_v1

logger = logging.getLogger(__name__)

COURTLISTENER_BASE = "https://www.courtlistener.com/api/rest/v4"
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v4")
NOTIFICATION_TOPIC = os.environ.get(
  "NOTIFICATION_TOPIC", f"projects/{PROJECT_ID}/topics/docket-alerts"
)


def _get_tracked_cases(db: firestore.Client) -> list[dict[str, Any]]:
  """Fetch all cases being watched from Firestore.

  Collection: tracked_cases/
  Document schema: {
      case_id: str,
      case_name: str,
      court: str,
      docket_number: str,
      last_checked: datetime,
      client_id: str,
  }
  """
  cases = []
  for doc in db.collection("tracked_cases").stream():
    data = doc.to_dict()
    data["doc_id"] = doc.id
    cases.append(data)
  return cases


def _poll_courtlistener(
  docket_number: str,
  *,
  since: datetime | None = None,
  api_token: str | None = None,
) -> list[dict[str, Any]] | None:
  """Poll CourtListener for new docket entries.

  Args:
      docket_number: Case docket number (e.g., "1:24-cv-00123").
      since: Only return entries filed after this datetime.
      api_token: Optional API token for higher rate limits.

  Returns:
      List of new docket entry dicts, or None if polling failed.
  """
  headers = {"Accept": "application/json"}
  if api_token:
    headers["Authorization"] = f"Token {api_token}"

  params: dict[str, str] = {
    "q": docket_number,
    "type": "r",  # r = RECAP docket entries
    "order_by": "dateFiled desc",
  }
  if since:
    params["filed_after"] = since.strftime("%Y-%m-%d")

  try:
    with httpx.Client(timeout=15.0) as client:
      response = client.get(
        f"{COURTLISTENER_BASE}/search/",
        params=params,
        headers=headers,
      )

      if response.status_code == 429:
        logger.warning("CourtListener rate limited — will retry next cycle")
        return None

      if response.status_code != 200:
        logger.error("CourtListener returned %d", response.status_code)
        return None

      data = response.json()
      return data.get("results", [])

  except httpx.TimeoutException:
    logger.warning("CourtListener timed out for %s", docket_number)
    return None
  except Exception:
    logger.exception("CourtListener polling failed for %s", docket_number)
    return None


def _store_and_notify(
  db: firestore.Client,
  publisher: pubsub_v1.PublisherClient,
  case: dict[str, Any],
  entries: list[dict[str, Any]],
) -> int:
  """Store new docket entries in Firestore and send Pub/Sub notifications.

  Returns:
      Number of new entries stored.
  """
  new_count = 0
  batch = db.batch()

  for entry in entries:
    entry_id = entry.get("id") or entry.get("absolute_url", "")
    if not entry_id:
      continue

    # Deduplicate by checking if we already have this entry
    doc_ref = db.collection("docket_events").document(str(entry_id))
    if doc_ref.get().exists:
      continue

    # Store the new entry
    event_data = {
      "case_id": case.get("case_id", ""),
      "case_name": case.get("case_name", ""),
      "client_id": case.get("client_id", ""),
      "docket_number": case.get("docket_number", ""),
      "entry_id": str(entry_id),
      "description": entry.get("description", ""),
      "date_filed": entry.get("dateFiled", ""),
      "court": entry.get("court", case.get("court", "")),
      "absolute_url": entry.get("absolute_url", ""),
      "discovered_at": datetime.now(tz=timezone.utc),
    }
    batch.set(doc_ref, event_data)
    new_count += 1

    # Publish notification
    try:
      message = json.dumps(
        {
          "type": "docket_alert",
          "case_name": case.get("case_name", ""),
          "docket_number": case.get("docket_number", ""),
          "description": entry.get("description", ""),
          "date_filed": entry.get("dateFiled", ""),
          "client_id": case.get("client_id", ""),
        }
      ).encode()
      publisher.publish(NOTIFICATION_TOPIC, message)
    except Exception:
      logger.exception("Failed to publish notification for entry %s", entry_id)

  if new_count > 0:
    batch.commit()

  return new_count


@functions_framework.http
def docket_watch(request: Any) -> tuple[str, int]:
  """Cloud Function entry point — polls all tracked cases for new filings.

  Triggered by Cloud Scheduler every 15 minutes.
  """
  db = firestore.Client(project=PROJECT_ID)
  publisher = pubsub_v1.PublisherClient()
  api_token = os.environ.get("COURTLISTENER_API_TOKEN")

  cases = _get_tracked_cases(db)
  logger.info("Polling %d tracked cases", len(cases))

  total_new = 0
  for case in cases:
    docket_number = case.get("docket_number", "")
    if not docket_number:
      continue

    last_checked = case.get("last_checked")
    entries = _poll_courtlistener(
      docket_number,
      since=last_checked,
      api_token=api_token,
    )

    if entries is not None:
      if entries:
        new_count = _store_and_notify(db, publisher, case, entries)
        total_new += new_count
        if new_count > 0:
          logger.info(
            "%d new entries for %s (%s)",
            new_count,
            case.get("case_name", ""),
            docket_number,
          )

      # Always update last_checked on successful response
      db.collection("tracked_cases").document(case["doc_id"]).update(
        {
          "last_checked": datetime.now(tz=timezone.utc),
        }
      )

  result = {"cases_polled": len(cases), "new_entries": total_new}
  logger.info("Docket watch complete: %s", result)
  return json.dumps(result), 200
