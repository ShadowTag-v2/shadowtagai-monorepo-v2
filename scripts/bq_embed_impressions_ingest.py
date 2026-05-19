#!/usr/bin/env python3
"""
BigQuery Ingestion Pipeline — HeadFade embed_impressions ETL

Ingests embed impression events into the analytics.embed_impressions BigQuery
table. Designed to run as a Cloud Run job or invoked from a Cloud Task.

Table schema (pre-provisioned):
  - event_id: STRING (PRIMARY KEY equivalent via dedup)
  - embed_id: STRING
  - page_url: STRING
  - referrer: STRING
  - user_agent: STRING
  - viewport_width: INT64
  - viewport_height: INT64
  - visible_duration_ms: INT64
  - interaction_type: STRING (view|click|scroll|hover)
  - timestamp: TIMESTAMP
  - country_code: STRING
  - region: STRING
  - session_id: STRING

Usage:
    python3 scripts/bq_embed_impressions_ingest.py --events-file events.jsonl
    python3 scripts/bq_embed_impressions_ingest.py --stdin < events.jsonl
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
  from google.cloud import bigquery
except ImportError:
  print(
    "ERROR: google-cloud-bigquery not installed. "
    "Run: pip install google-cloud-bigquery",
    file=sys.stderr,
  )
  sys.exit(1)


PROJECT_ID = "shadowtag-omega-v4"
DATASET_ID = "analytics"
TABLE_ID = "embed_impressions"
FULL_TABLE = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

VALID_INTERACTION_TYPES = {"view", "click", "scroll", "hover"}


def validate_event(event: dict) -> dict | None:
  """Validate and normalize a single event. Returns None if invalid."""
  required = ["embed_id", "interaction_type"]
  for field in required:
    if field not in event:
      print(f"WARN: Missing required field '{field}', skipping event", file=sys.stderr)
      return None

  if event.get("interaction_type") not in VALID_INTERACTION_TYPES:
    print(
      f"WARN: Invalid interaction_type '{event.get('interaction_type')}', skipping",
      file=sys.stderr,
    )
    return None

  # Normalize and fill defaults
  now = datetime.now(timezone.utc).isoformat()
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


def load_events(source: str | None) -> list[dict]:
  """Load events from file or stdin."""
  lines: list[str] = []
  if source:
    path = Path(source)
    if not path.exists():
      print(f"ERROR: File not found: {source}", file=sys.stderr)
      sys.exit(1)
    lines = path.read_text().strip().splitlines()
  else:
    lines = sys.stdin.read().strip().splitlines()

  events = []
  for i, line in enumerate(lines):
    if not line.strip():
      continue
    try:
      raw = json.loads(line)
      validated = validate_event(raw)
      if validated:
        events.append(validated)
    except json.JSONDecodeError as exc:
      print(f"WARN: Invalid JSON on line {i + 1}: {exc}", file=sys.stderr)

  return events


def ingest(events: list[dict]) -> int:
  """Insert validated events into BigQuery. Returns count of inserted rows."""
  if not events:
    print("No valid events to ingest.")
    return 0

  client = bigquery.Client(project=PROJECT_ID)

  errors = client.insert_rows_json(FULL_TABLE, events)
  if errors:
    print(f"ERROR: BigQuery insert errors: {errors}", file=sys.stderr)
    return 0

  print(f"Successfully ingested {len(events)} events into {FULL_TABLE}")
  return len(events)


def main() -> int:
  parser = argparse.ArgumentParser(
    description="HeadFade embed_impressions BigQuery ingestion"
  )
  group = parser.add_mutually_exclusive_group(required=True)
  group.add_argument("--events-file", help="Path to JSONL file with events")
  group.add_argument("--stdin", action="store_true", help="Read events from stdin")
  args = parser.parse_args()

  source = args.events_file if args.events_file else None
  events = load_events(source)
  print(f"Loaded {len(events)} valid events")

  count = ingest(events)
  return 0 if count > 0 else 1


if __name__ == "__main__":
  raise SystemExit(main())
