#!/usr/bin/env -S .venv/bin/python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
scripts/lance_embed_ingestor.py
Batch-embeds the SQLite corpus extractions into LanceDB using Gemini text-embedding.

Strategy:
  1. Read rows with embedding IS NULL from each CORPUS_DB (drive_ingest, web_ingest)
  2. Embed via Gemini text-embedding-004 in batches of 100
  3. Write embedding JSON back to SQLite AND upsert to LanceDB table
  4. LanceDB table lives at data/lancedb/<db_name>/ for ANN search

Run:
  GEMINI_API_KEY=... python3 scripts/lance_embed_ingestor.py
  GEMINI_API_KEY=... python3 scripts/lance_embed_ingestor.py --db drive_ingest --limit 5000
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sqlite3
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

logging.basicConfig(
  level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("lance_embed")

CORPUS_DBS = {
  "drive_ingest": REPO_ROOT / "data/drive_ingest/ingest.db",
  "web_ingest": REPO_ROOT / "data/web_ingest/ingest.db",
}
LANCE_ROOT = REPO_ROOT / "data/lancedb"
EMBED_MODEL = "models/gemini-embedding-2-preview"  # 3072-dim, best quality
EMBED_DIM = 3072
BATCH_SIZE = 100
MAX_TEXT_CHARS = 2_000  # truncate to stay within token limits


def _get_client():
  from google import genai

  return genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def _embed_batch(client, texts: list[str]) -> list[list[float]]:
  """Embed a batch via Gemini; returns list of float vectors."""
  from google.genai import types

  result = client.models.embed_content(
    model=EMBED_MODEL,
    contents=texts,
    config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
  )
  return [e.values for e in result.embeddings]


def _ensure_embedding_col(conn: sqlite3.Connection) -> None:
  cols = [r[1] for r in conn.execute("PRAGMA table_info(extractions)").fetchall()]
  if "embedding" not in cols:
    conn.execute("ALTER TABLE extractions ADD COLUMN embedding TEXT")
    conn.commit()


def _fetch_unembedded(conn: sqlite3.Connection, limit: int) -> list[dict]:
  rows = conn.execute(
    "SELECT id, name, text FROM extractions WHERE embedding IS NULL LIMIT ?",
    (limit,),
  ).fetchall()
  return [{"id": r[0], "name": r[1], "text": r[2]} for r in rows]


def _upsert_lance(db_name: str, rows: list[dict], vectors: list[list[float]]) -> None:
  import lancedb
  import pyarrow as pa

  db = lancedb.connect(str(LANCE_ROOT))
  table_name = db_name.replace("-", "_")
  schema = pa.schema(
    [
      pa.field("id", pa.int64()),
      pa.field("name", pa.utf8()),
      pa.field("text", pa.utf8()),
      pa.field("vector", pa.list_(pa.float32(), EMBED_DIM)),
    ]
  )
  records = [
    {"id": r["id"], "name": r["name"], "text": r["text"][:500], "vector": v}
    for r, v in zip(rows, vectors)
  ]
  # list_tables() returns ListTablesResponse with .tables list in lancedb>=0.20
  tbl_response = db.list_tables()
  existing = getattr(tbl_response, "tables", None) or list(tbl_response)
  if table_name in existing:
    tbl = db.open_table(table_name)
    tbl.add(records)
  else:
    db.create_table(table_name, data=records, schema=schema)
  logger.info("[lance] %s upserted %d rows", table_name, len(records))


def embed_db(db_name: str, db_path: Path, client, limit: int = 50_000) -> int:
  conn = sqlite3.connect(str(db_path))
  _ensure_embedding_col(conn)
  rows = _fetch_unembedded(conn, limit)
  if not rows:
    logger.info("[%s] No unembedded rows — already complete.", db_name)
    conn.close()
    return 0

  logger.info("[%s] Embedding %d rows in batches of %d", db_name, len(rows), BATCH_SIZE)
  total = 0
  for i in range(0, len(rows), BATCH_SIZE):
    batch = rows[i : i + BATCH_SIZE]
    texts = [r["text"][:MAX_TEXT_CHARS] for r in batch]
    try:
      vectors = _embed_batch(client, texts)
    except Exception as exc:
      logger.error("Embed batch %d failed: %s — sleeping 10s", i // BATCH_SIZE, exc)
      time.sleep(10)
      continue

    # Write back to SQLite
    conn.executemany(
      "UPDATE extractions SET embedding=? WHERE id=?",
      [(json.dumps(v), r["id"]) for r, v in zip(batch, vectors)],
    )
    conn.commit()
    _upsert_lance(db_name, batch, vectors)
    total += len(batch)
    logger.info("[%s] %d/%d embedded", db_name, total, len(rows))
    time.sleep(0.5)  # rate limit courtesy

  conn.close()
  return total


def main() -> None:
  parser = argparse.ArgumentParser()
  parser.add_argument("--db", choices=list(CORPUS_DBS), help="Only process one DB")
  parser.add_argument("--limit", type=int, default=50_000)
  args = parser.parse_args()

  client = _get_client()
  dbs = {args.db: CORPUS_DBS[args.db]} if args.db else CORPUS_DBS
  grand_total = 0
  for name, path in dbs.items():
    if not path.exists():
      logger.warning("DB not found: %s", path)
      continue
    n = embed_db(name, path, client, args.limit)
    grand_total += n
  logger.info("Done. Total embedded: %d", grand_total)


if __name__ == "__main__":
  main()
