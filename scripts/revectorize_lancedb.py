#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Re-vectorize LanceDB workspace_knowledge with sentence-transformers embeddings.

Reads the existing 1,094 records from workspace_knowledge table,
generates 384-dim embeddings using all-MiniLM-L6-v2, and writes
them back with a proper 'vector' column for semantic search.
"""

import json
import logging
import sys
import time
from pathlib import Path

import lancedb
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Constants
LANCEDB_PATH = Path(__file__).parent.parent / "data" / "drive_ingest" / "lancedb"
JSONL_PATH = (
  Path(__file__).parent.parent / "data" / "drive_ingest" / "extractions.jsonl"
)
MODEL_NAME = "all-MiniLM-L6-v2"
BATCH_SIZE = 64
TABLE_NAME = "workspace_knowledge"
VECTORIZED_TABLE = "workspace_knowledge_v2"


def load_jsonl_records(path: Path) -> list[dict]:
  """Load all records from extractions.jsonl."""
  records = []
  with path.open() as f:
    for line in f:
      line = line.strip()
      if line:
        records.append(json.loads(line))
  logger.info("Loaded %d records from %s", len(records), path)
  return records


def generate_embeddings(texts: list[str], model_name: str = MODEL_NAME) -> np.ndarray:
  """Generate embeddings for texts using sentence-transformers."""
  from sentence_transformers import SentenceTransformer

  logger.info("Loading model: %s", model_name)
  model = SentenceTransformer(model_name)

  logger.info(
    "Generating embeddings for %d texts (batch_size=%d)...", len(texts), BATCH_SIZE
  )
  start = time.time()
  embeddings = model.encode(
    texts,
    batch_size=BATCH_SIZE,
    show_progress_bar=True,
    normalize_embeddings=True,
  )
  elapsed = time.time() - start
  logger.info(
    "Generated %d embeddings (%d-dim) in %.1fs (%.1f texts/sec)",
    len(embeddings),
    embeddings.shape[1],
    elapsed,
    len(texts) / elapsed,
  )
  return embeddings


def build_vectorized_table(
  db: lancedb.DBConnection, records: list[dict], embeddings: np.ndarray
) -> None:
  """Create a new LanceDB table with vector embeddings."""
  # Prepare data
  data = []
  for i, rec in enumerate(records):
    # Use raw_content from JSONL, fall back to existing text
    text_content = rec.get("raw_content", rec.get("text", ""))
    title = rec.get("source_file", rec.get("title", f"doc_{i}"))
    doc_id = rec.get("document_id", rec.get("id", f"doc_{i}"))

    data.append(
      {
        "id": doc_id,
        "title": title,
        "text": text_content[:4000],  # Cap at 4k chars for storage
        "format": rec.get("format", "unknown"),
        "content_hash": rec.get("content_hash", ""),
        "byte_size": rec.get("byte_size", 0),
        "vector": embeddings[i].tolist(),
      }
    )

  logger.info(
    "Writing %d vectorized records to table '%s'...", len(data), VECTORIZED_TABLE
  )

  # Drop existing v2 table if present
  existing_tables = db.table_names()
  if VECTORIZED_TABLE in existing_tables:
    db.drop_table(VECTORIZED_TABLE)
    logger.info("Dropped existing table '%s'", VECTORIZED_TABLE)

  tbl = db.create_table(VECTORIZED_TABLE, data=data)
  logger.info("Created table '%s' with %d rows", VECTORIZED_TABLE, tbl.count_rows())
  logger.info("Schema: %s", tbl.schema)
  return tbl


def test_semantic_search(db: lancedb.DBConnection) -> None:
  """Run test queries to verify semantic search works."""
  from sentence_transformers import SentenceTransformer

  model = SentenceTransformer(MODEL_NAME)
  tbl = db.open_table(VECTORIZED_TABLE)

  queries = [
    "HeadFade scalp micropigmentation AI",
    "CounselConduit legal privilege routing",
    "Stripe payment integration billing",
    "MLX Apple Neural Engine inference",
    "security audit compliance OWASP",
  ]

  for q in queries:
    qvec = model.encode(q, normalize_embeddings=True)
    results = tbl.search(qvec).limit(3).to_pandas()
    print(f"\n🔍 Query: '{q}'")
    for _, row in results.iterrows():
      dist = row.get("_distance", 0)
      title = str(row["title"])[:60]
      text_preview = str(row["text"])[:80]
      print(f"  [{dist:.3f}] {title}")
      print(f"    → {text_preview}...")


def main() -> int:
  """Main entry point."""
  logger.info("=== LanceDB Re-Vectorization Pipeline ===")
  logger.info("DB path: %s", LANCEDB_PATH)
  logger.info("JSONL path: %s", JSONL_PATH)

  # Load records
  records = load_jsonl_records(JSONL_PATH)
  if not records:
    logger.error("No records found in JSONL file")
    return 1

  # Prepare texts for embedding
  texts = []
  for rec in records:
    content = rec.get("raw_content", rec.get("text", ""))
    title = rec.get("source_file", rec.get("title", ""))
    # Combine title + content for richer embeddings
    combined = f"{title}\n{content[:2000]}"
    texts.append(combined)

  # Generate embeddings
  embeddings = generate_embeddings(texts)

  # Connect to LanceDB and build vectorized table
  db = lancedb.connect(str(LANCEDB_PATH))
  build_vectorized_table(db, records, embeddings)

  # Test semantic search
  test_semantic_search(db)

  logger.info("=== Re-vectorization complete ===")
  return 0


if __name__ == "__main__":
  sys.exit(main())
