# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""embed_to_lancedb.py — Vectorize extracted JSONL into LanceDB workspace_knowledge table.

Reads .beads/knowledge_base/extraction_results.jsonl, embeds text via
Gemini Embedding API (models/gemini-embedding-001), and writes vectors
into data/lancedb/workspace_knowledge.

Usage:
    python scripts/embed_to_lancedb.py
"""

import json
import logging
import os
import time
from pathlib import Path

import lancedb
import pyarrow as pa
from dotenv import load_dotenv
from google import genai

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent
JSONL_PATH = REPO_ROOT / ".beads" / "knowledge_base" / "extraction_results.jsonl"
LANCEDB_PATH = REPO_ROOT / "data" / "lancedb" / "workspace_knowledge"
BATCH_SIZE = 50
MODEL_ID = "models/gemini-embedding-001"


def embed_batch(client: genai.Client, texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts using Gemini Embedding API."""
    embeddings = []
    for text in texts:
        try:
            resp = client.models.embed_content(
                model=MODEL_ID,
                contents=text,
            )
            embeddings.append(resp.embeddings[0].values)
        except Exception as e:
            logger.exception("Embedding failed: %s", e)
            embeddings.append([0.0] * 768)  # zero vector fallback
    return embeddings


def main() -> None:
    """Main embedding pipeline."""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        logger.error("No GEMINI_API_KEY or GOOGLE_API_KEY found in environment")
        return

    client = genai.Client(api_key=api_key)

    # Open or create LanceDB table
    db = lancedb.connect(str(LANCEDB_PATH))
    schema = pa.schema(
        [
            pa.field("doc_id", pa.string()),
            pa.field("text", pa.string()),
            pa.field("vector", pa.list_(pa.float32(), 768)),
        ],
    )

    try:
        table = db.open_table("documents")
        logger.info("Opened existing LanceDB table 'documents'")
    except Exception:
        table = db.create_table("documents", schema=schema)
        logger.info("Created new LanceDB table 'documents'")

    if not JSONL_PATH.exists():
        logger.error("JSONL not found: %s", JSONL_PATH)
        return

    records_to_insert = []
    text_batch = []
    total_processed = 0

    with open(JSONL_PATH) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                logger.warning("Skipping malformed JSON at line %d", line_num)
                continue

            raw_text = data.get("text", data.get("content", ""))
            doc_id = data.get("id", data.get("doc_id", f"doc_{line_num}"))

            if not raw_text:
                continue

            # Truncate long texts to fit embedding model limits
            raw_text = raw_text[:8000]
            text_batch.append((doc_id, raw_text))

            if len(text_batch) >= BATCH_SIZE:
                vectors = embed_batch(client, [t[1] for t in text_batch])
                for row, vec in zip(text_batch, vectors, strict=False):
                    records_to_insert.append(
                        {
                            "doc_id": row[0],
                            "text": row[1][:2000],  # store truncated text
                            "vector": vec,
                        },
                    )
                text_batch = []
                total_processed += BATCH_SIZE
                logger.info("Processed %d documents", total_processed)
                time.sleep(0.5)  # rate limiting

    # Flush remaining
    if text_batch:
        vectors = embed_batch(client, [t[1] for t in text_batch])
        for row, vec in zip(text_batch, vectors, strict=False):
            records_to_insert.append(
                {
                    "doc_id": row[0],
                    "text": row[1][:2000],
                    "vector": vec,
                },
            )
        total_processed += len(text_batch)

    if records_to_insert:
        try:
            table.add(records_to_insert)
            logger.info("Inserted %d records into LanceDB", len(records_to_insert))
        except Exception as e:
            logger.exception("Failed to insert into LanceDB: %s", e)

    logger.info("Embedding complete. Total processed: %d", total_processed)


if __name__ == "__main__":
    main()
