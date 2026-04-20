"""
Drive Embedder - Sovereign Memory Ingestion Protocol

Embeds every .md file in the local data/drive_ingest/markdown/ directory
into the LanceDB workspace_knowledge table using Vertex AI embeddings.

This is a standalone ingestion script, separate from the 7-step pipeline.
"""

import json
import logging
import sys
import time
from pathlib import Path

import lancedb
import pyarrow as pa

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent.parent
DRIVE_DIR = REPO_ROOT / "data" / "drive_ingest" / "markdown"
LANCEDB_DIR = REPO_ROOT / "data" / "lancedb"
STATE_PATH = REPO_ROOT / "data" / "drive_ingest" / "fast_ingest_state.json"


def embed_batch(texts: list[str], token: str) -> list[list[float]]:
    """Embed a batch via Vertex AI text-embedding-005."""
    import os
    import requests
    import google.auth
    import google.auth.transport.requests as gauth_requests

    project = os.environ.get("GCP_PROJECT_ID", "shadowtag-omega-v4")
    region = "us-central1"
    endpoint = (
        f"https://{region}-aiplatform.googleapis.com/v1/projects/"
        f"{project}/locations/{region}/publishers/google/models/text-embedding-005:predict"
    )
    payload = {"instances": [{"content": t[:3000]} for t in texts]}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    resp = requests.post(endpoint, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    return [p["embeddings"]["values"] for p in resp.json()["predictions"]]


def load_state() -> dict:
    """Load ingestion state."""
    if STATE_PATH.exists():
        with open(STATE_PATH) as f:
            return json.load(f)
    return {"processed": [], "count": 0}


def save_state(state: dict) -> None:
    """Save ingestion state."""
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def get_or_create_table(db):
    """Get or create workspace_knowledge table."""
    schema = pa.schema([
        pa.field("id", pa.string()),
        pa.field("title", pa.string()),
        pa.field("source", pa.string()),
        pa.field("text", pa.string()),
        pa.field("vector", pa.list_(pa.float32(), 768)),
        pa.field("domain", pa.string()),
        pa.field("ingested_at", pa.string()),
    ])
    result = db.list_tables()
    table_names = result.tables if hasattr(result, "tables") else list(result)
    if "workspace_knowledge" in table_names:
        return db.open_table("workspace_knowledge")
    return db.create_table("workspace_knowledge", schema=schema)


def run(cfg=None) -> dict:
    """Run drive embedder ingestion."""
    logger.info("Drive Embedder — starting")

    if not DRIVE_DIR.exists():
        logger.warning(f"Drive directory not found: {DRIVE_DIR}")
        return {"status": "no_drive_dir"}

    import google.auth
    import google.auth.transport.requests as gauth_requests

    creds, _ = google.auth.default()
    creds.refresh(gauth_requests.Request())
    token = creds.token

    db = lancedb.connect(str(LANCEDB_DIR))
    tbl = get_or_create_table(db)
    state = load_state()
    processed = set(state.get("processed", []))

    md_files = list(DRIVE_DIR.rglob("*.md"))
    new_files = [f for f in md_files if str(f) not in processed]
    logger.info(f"Found {len(md_files)} markdown files, {len(new_files)} new")

    if not new_files:
        return {"status": "up_to_date", "total": len(md_files)}

    ingested = 0
    batch_texts = []
    batch_meta = []

    for fpath in new_files:
        try:
            content = fpath.read_text(errors="replace")
        except Exception:
            continue

        batch_texts.append(content[:3000])
        batch_meta.append({
            "id": str(fpath.relative_to(REPO_ROOT)),
            "title": fpath.stem,
            "source": "drive_ingest",
            "text": content[:2000],
            "domain": "",
            "ingested_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        })

        if len(batch_texts) >= 5:
            try:
                vectors = embed_batch(batch_texts, token)
                rows = [{**m, "vector": v} for m, v in zip(batch_meta, vectors)]
                tbl.add(rows)
                ingested += len(rows)
            except Exception as e:
                logger.warning(f"Batch embed failed: {e}")
            batch_texts.clear()
            batch_meta.clear()
            time.sleep(0.5)

        processed.add(str(fpath))

    # Flush
    if batch_texts:
        try:
            vectors = embed_batch(batch_texts, token)
            rows = [{**m, "vector": v} for m, v in zip(batch_meta, vectors)]
            tbl.add(rows)
            ingested += len(rows)
        except Exception as e:
            logger.warning(f"Final batch failed: {e}")

    state["processed"] = list(processed)
    state["count"] = len(processed)
    save_state(state)

    stats = {"ingested": ingested, "total_files": len(md_files)}
    logger.info(f"Drive Embedder complete: {stats}")
    return stats


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
