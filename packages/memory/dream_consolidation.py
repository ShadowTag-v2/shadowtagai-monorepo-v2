"""dream_consolidation.py — Hermes Cloud Drain Daemon.
=====================================================
Asynchronous background daemon that drains the Omni-Sync cloud queue
(.beads/cloud_sync_queue.json) to production Google Cloud targets:

  Box 12: Google Drive API  — Writes knowledge atoms as JSON files
  Box 13: BigQuery          — Inserts rows into epistemic_ledger table
  Box 14: Cloud Spanner     — Inserts rows into memories table

The Omni-Sync Multiplexer (scripts/omni_epistemic_sync.ts) writes to
the queue; this daemon reads and drains it. Separation of concerns
ensures the agent never blocks on network I/O during a coding turn.

Security:
  - ReadOnlyBashGuard: No subprocess writes during dream phase
  - PID lock: Prevents concurrent daemon instances
  - Graceful degradation: Individual API failures don't block others

Usage:
  python packages/memory/dream_consolidation.py               # Daemon mode (loop)
  python packages/memory/dream_consolidation.py --once         # Single pass
  python packages/memory/dream_consolidation.py --dry-run      # Preview only

Requires:
  pip install google-cloud-bigquery google-cloud-spanner google-api-python-client
"""

from __future__ import annotations

import json
import logging
import os
import signal
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s [HERMES-DRAIN] %(levelname)s %(message)s",
  datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("hermes_drain")

# =====================================================================
# Configuration
# =====================================================================
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BEADS_DIR = REPO_ROOT / ".beads"
QUEUE_FILE = BEADS_DIR / "cloud_sync_queue.json"
LOCK_FILE = BEADS_DIR / ".cloud-drain.lock"
POLL_INTERVAL = int(os.environ.get("HERMES_POLL_SECONDS", "30"))
DRY_RUN = "--dry-run" in sys.argv
ONCE = "--once" in sys.argv

# Google Cloud configuration
GCP_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v4")
BQ_DATASET = os.environ.get("HERMES_BQ_DATASET", "hermes_memory")
BQ_TABLE = os.environ.get("HERMES_BQ_TABLE", "epistemic_ledger")
SPANNER_INSTANCE = os.environ.get("HERMES_SPANNER_INSTANCE", "hermes-memory")
SPANNER_DATABASE = os.environ.get("HERMES_SPANNER_DB", "epistemic_store")
DRIVE_FOLDER_ID = os.environ.get("HERMES_DRIVE_FOLDER_ID", "")

# =====================================================================
# PID Mutex (prevents concurrent drain instances)
# =====================================================================
_shutdown = False


def _signal_handler(signum: int, _frame: Any) -> None:
  global _shutdown  # noqa: PLW0603
  logger.info("Received signal %d, shutting down gracefully...", signum)
  _shutdown = True


signal.signal(signal.SIGTERM, _signal_handler)
signal.signal(signal.SIGINT, _signal_handler)


def try_acquire_lock() -> bool:
  """PID-based file lock preventing concurrent drain instances."""
  BEADS_DIR.mkdir(parents=True, exist_ok=True)
  if LOCK_FILE.exists():
    try:
      lock_data = json.loads(LOCK_FILE.read_text())
      held_pid = lock_data.get("pid", -1)
      os.kill(held_pid, 0)  # Check if process is alive
      logger.info("Lock held by PID %d, exiting", held_pid)
      return False
    except (OSError, json.JSONDecodeError, ValueError):
      logger.warning("Breaking stale lock")

  LOCK_FILE.write_text(
    json.dumps(
      {
        "pid": os.getpid(),
        "acquired_at": datetime.now(UTC).isoformat(),
      }
    )
  )
  return True


def release_lock() -> None:
  """Release the PID lock if we hold it."""
  if LOCK_FILE.exists():
    try:
      data = json.loads(LOCK_FILE.read_text())
      if data.get("pid") == os.getpid():
        LOCK_FILE.unlink()
        logger.info("Lock released")
    except (json.JSONDecodeError, OSError):
      pass


# =====================================================================
# Cloud Client Initialization (lazy, graceful degradation)
# =====================================================================
_bq_client = None
_spanner_db = None
_drive_service = None


def _get_bq_client() -> Any:
  """Lazy-init BigQuery client. Returns None if unavailable."""
  global _bq_client  # noqa: PLW0603
  if _bq_client is not None:
    return _bq_client
  try:
    from google.cloud import bigquery

    _bq_client = bigquery.Client(project=GCP_PROJECT)
    logger.info("BigQuery client initialized (project=%s)", GCP_PROJECT)
    return _bq_client
  except Exception as e:
    logger.warning("BigQuery client unavailable: %s", e)
    return None


def _get_spanner_db() -> Any:
  """Lazy-init Spanner database handle. Returns None if unavailable."""
  global _spanner_db  # noqa: PLW0603
  if _spanner_db is not None:
    return _spanner_db
  try:
    from google.cloud import spanner

    client = spanner.Client(project=GCP_PROJECT)
    instance = client.instance(SPANNER_INSTANCE)
    _spanner_db = instance.database(SPANNER_DATABASE)
    logger.info(
      "Spanner client initialized (instance=%s, db=%s)",
      SPANNER_INSTANCE,
      SPANNER_DATABASE,
    )
    return _spanner_db
  except Exception as e:
    logger.warning("Spanner client unavailable: %s", e)
    return None


def _get_drive_service() -> Any:
  """Lazy-init Google Drive API service. Returns None if unavailable."""
  global _drive_service  # noqa: PLW0603
  if _drive_service is not None:
    return _drive_service
  try:
    from googleapiclient.discovery import build

    # Use Application Default Credentials
    import google.auth

    credentials, _ = google.auth.default(
      scopes=["https://www.googleapis.com/auth/drive.file"]
    )
    _drive_service = build("drive", "v3", credentials=credentials)
    logger.info("Google Drive API initialized")
    return _drive_service
  except Exception as e:
    logger.warning("Drive API unavailable: %s", e)
    return None


# =====================================================================
# Box 13: BigQuery — epistemic_ledger table
# =====================================================================
def _ensure_bq_table(client: Any) -> str:
  """Ensure the BigQuery dataset and table exist. Returns full table ID."""
  table_id = f"{GCP_PROJECT}.{BQ_DATASET}.{BQ_TABLE}"
  try:
    client.get_table(table_id)
  except Exception:
    # Create dataset if needed
    from google.cloud import bigquery

    dataset_ref = bigquery.DatasetReference(GCP_PROJECT, BQ_DATASET)
    try:
      client.get_dataset(dataset_ref)
    except Exception:
      dataset = bigquery.Dataset(dataset_ref)
      dataset.location = "US"
      client.create_dataset(dataset, exists_ok=True)
      logger.info("Created BigQuery dataset: %s", BQ_DATASET)

    # Create table with schema
    schema = [
      bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
      bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
      bigquery.SchemaField("atom_type", "STRING"),
      bigquery.SchemaField("content", "STRING"),
      bigquery.SchemaField("supersedes", "STRING"),
      bigquery.SchemaField("source", "STRING"),
      bigquery.SchemaField("ingested_at", "TIMESTAMP"),
    ]
    table = bigquery.Table(table_id, schema=schema)
    client.create_table(table, exists_ok=True)
    logger.info("Created BigQuery table: %s", table_id)

  return table_id


def drain_to_bigquery(items: list[dict]) -> int:
  """Insert knowledge atoms into BigQuery epistemic_ledger. Returns count."""
  client = _get_bq_client()
  if not client or not items:
    return 0

  table_id = _ensure_bq_table(client)
  now = datetime.now(UTC).isoformat()

  rows = []
  for item in items:
    rows.append(
      {
        "id": item.get("id", ""),
        "timestamp": item.get("timestamp", now),
        "atom_type": item.get("atomType", "unknown"),
        "content": item.get("content", ""),
        "supersedes": item.get("supersedes") or "",
        "source": "omni_sync_mux",
        "ingested_at": now,
      }
    )

  if DRY_RUN:
    logger.info("[DRY-RUN] Would insert %d rows into %s", len(rows), table_id)
    return len(rows)

  errors = client.insert_rows_json(table_id, rows)
  if errors:
    logger.error("BigQuery insert errors: %s", errors)
    return 0

  logger.info("✅ BigQuery: Inserted %d rows into %s", len(rows), table_id)
  return len(rows)


# =====================================================================
# Box 14: Cloud Spanner — memories table
# =====================================================================
def _ensure_spanner_table(database: Any) -> None:
  """Ensure the Spanner memories table exists."""
  ddl = """
    CREATE TABLE IF NOT EXISTS memories (
        id STRING(64) NOT NULL,
        timestamp TIMESTAMP NOT NULL,
        atom_type STRING(32),
        content STRING(MAX),
        supersedes STRING(MAX),
        source STRING(64),
        ingested_at TIMESTAMP,
    ) PRIMARY KEY (id)
    """
  try:
    operation = database.update_ddl([ddl])
    operation.result(timeout=60)
    logger.info("Spanner table 'memories' ensured")
  except Exception as e:
    # Table likely already exists
    if "Duplicate" not in str(e) and "already exists" not in str(e):
      logger.warning("Spanner DDL warning: %s", e)


def drain_to_spanner(items: list[dict]) -> int:
  """Insert knowledge atoms into Spanner memories table. Returns count."""
  database = _get_spanner_db()
  if not database or not items:
    return 0

  _ensure_spanner_table(database)
  now = datetime.now(UTC).isoformat()

  if DRY_RUN:
    logger.info("[DRY-RUN] Would insert %d rows into Spanner", len(items))
    return len(items)

  def _insert_batch(transaction: Any) -> None:
    for item in items:
      transaction.insert(
        "memories",
        columns=[
          "id",
          "timestamp",
          "atom_type",
          "content",
          "supersedes",
          "source",
          "ingested_at",
        ],
        values=[
          [
            item.get("id", ""),
            item.get("timestamp", now),
            item.get("atomType", "unknown"),
            item.get("content", ""),
            item.get("supersedes") or "",
            "omni_sync_mux",
            now,
          ]
        ],
      )

  try:
    database.run_in_transaction(_insert_batch)
    logger.info("✅ Spanner: Inserted %d rows", len(items))
    return len(items)
  except Exception as e:
    logger.error("Spanner insert failed: %s", e)
    return 0


# =====================================================================
# Box 12: Google Drive API — knowledge atom JSON files
# =====================================================================
def drain_to_drive(items: list[dict]) -> int:
  """Upload knowledge atoms as JSON files to Google Drive. Returns count."""
  service = _get_drive_service()
  if not service or not items or not DRIVE_FOLDER_ID:
    if not DRIVE_FOLDER_ID:
      logger.info("HERMES_DRIVE_FOLDER_ID not set — skipping Drive upload")
    return 0

  if DRY_RUN:
    logger.info(
      "[DRY-RUN] Would upload %d files to Drive folder %s", len(items), DRIVE_FOLDER_ID
    )
    return len(items)

  from googleapiclient.http import MediaInMemoryUpload

  count = 0
  for item in items:
    try:
      content_bytes = json.dumps(item, indent=2).encode("utf-8")
      media = MediaInMemoryUpload(content_bytes, mimetype="application/json")
      ts_slug = item.get("timestamp", "unknown")[:19].replace(":", "-")
      file_metadata = {
        "name": f"hermes_{ts_slug}_{item.get('atomType', 'atom')}.json",
        "parents": [DRIVE_FOLDER_ID],
        "mimeType": "application/json",
      }
      service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id",
      ).execute()
      count += 1
    except Exception as e:
      logger.error("Drive upload failed for item: %s", e)

  if count:
    logger.info("✅ Drive: Uploaded %d files to folder %s", count, DRIVE_FOLDER_ID)
  return count


# =====================================================================
# Queue Management
# =====================================================================
def load_queue() -> list[dict]:
  """Load pending items from cloud_sync_queue.json."""
  if not QUEUE_FILE.exists():
    return []
  try:
    data = json.loads(QUEUE_FILE.read_text())
    return data if isinstance(data, list) else []
  except (json.JSONDecodeError, OSError):
    return []


def clear_queue() -> None:
  """Clear the queue after successful drain."""
  if DRY_RUN:
    logger.info("[DRY-RUN] Would clear queue")
    return
  QUEUE_FILE.write_text("[]")
  logger.info("Queue cleared")


def archive_failed(items: list[dict]) -> None:
  """Archive items that failed all 3 targets for manual retry."""
  if not items:
    return
  archive_path = BEADS_DIR / f"cloud_drain_failed_{int(time.time())}.json"
  archive_path.write_text(json.dumps(items, indent=2))
  logger.warning("Archived %d failed items to %s", len(items), archive_path.name)


# =====================================================================
# Main Drain Loop
# =====================================================================
def drain_once() -> dict[str, int]:
  """Execute a single drain pass. Returns counts per target."""
  items = load_queue()
  if not items:
    return {"bigquery": 0, "spanner": 0, "drive": 0, "total": 0}

  logger.info("Processing %d queued items...", len(items))

  results = {
    "bigquery": drain_to_bigquery(items),
    "spanner": drain_to_spanner(items),
    "drive": drain_to_drive(items),
    "total": len(items),
  }

  # Clear queue if at least one target succeeded
  any_success = any(v > 0 for k, v in results.items() if k != "total")
  if any_success or DRY_RUN:
    clear_queue()
  else:
    logger.warning("All targets failed — queue preserved for retry")
    archive_failed(items)

  return results


def daemon_loop() -> None:
  """Run the drain loop continuously with POLL_INTERVAL sleep."""
  logger.info(
    "Hermes Cloud Drain Daemon started (poll=%ds, project=%s, dry_run=%s)",
    POLL_INTERVAL,
    GCP_PROJECT,
    DRY_RUN,
  )

  while not _shutdown:
    try:
      results = drain_once()
      if results["total"] > 0:
        logger.info(
          "Drain pass complete: BQ=%d, Spanner=%d, Drive=%d (of %d items)",
          results["bigquery"],
          results["spanner"],
          results["drive"],
          results["total"],
        )
    except Exception as e:
      logger.error("Drain pass failed: %s", e)

    # Sleep in small increments to respond to shutdown signal quickly
    for _ in range(POLL_INTERVAL):
      if _shutdown:
        break
      time.sleep(1)

  logger.info("Daemon shutdown complete")


# =====================================================================
# Entry Point
# =====================================================================
if __name__ == "__main__":
  if not try_acquire_lock():
    sys.exit(0)

  try:
    if ONCE:
      results = drain_once()
      logger.info("Single pass results: %s", results)
    else:
      daemon_loop()
  finally:
    release_lock()
