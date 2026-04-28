# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""LanceDB vector store for the ShadowTag-v4 FastAPI workspace knowledge base.

Embedding: Vertex AI text-embedding-004 (768-dim) via ADC.
DB path:   <monorepo_root>/data/lancedb/   (canonical, consistent across callers)
Table:     workspace_knowledge  (workspace_id INT32 field for per-workspace filtering)
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import lancedb
import pyarrow as pa

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
_MONOREPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent  # 4 levels up from here
DB_PATH = str(_MONOREPO_ROOT / "data" / "lancedb")
TABLE_NAME = "workspace_knowledge"
EMBED_DIM = 768
VERTEX_PROJECT = "shadowtag-omega-v4"
VERTEX_LOCATION = "us-central1"
EMBED_MODEL_ID = "text-embedding-004"

SCHEMA = pa.schema(
    [
        pa.field("workspace_id", pa.int32()),
        pa.field("source", pa.string()),
        pa.field("text", pa.string()),
        pa.field("vector", pa.list_(pa.float32(), EMBED_DIM)),
    ],
)


# ---------------------------------------------------------------------------
# Lazy Vertex AI init (avoids import-time auth failures during unit tests)
# ---------------------------------------------------------------------------
_embed_model = None


def _get_model():
    global _embed_model
    if _embed_model is None:
        import vertexai
        from vertexai.language_models import TextEmbeddingModel

        vertexai.init(project=VERTEX_PROJECT, location=VERTEX_LOCATION)
        _embed_model = TextEmbeddingModel.from_pretrained(EMBED_MODEL_ID)
    return _embed_model


def get_gemini_embedding(text: str) -> list[float]:
    """Embed text via Vertex AI text-embedding-004 (768-dim)."""
    from vertexai.language_models import TextEmbeddingInput

    model = _get_model()
    for attempt in range(4):
        try:
            result = model.get_embeddings([TextEmbeddingInput(text, "RETRIEVAL_DOCUMENT")])
            return list(result[0].values)
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2**attempt)
    raise RuntimeError("unreachable")


# ---------------------------------------------------------------------------
# DB / table helpers
# ---------------------------------------------------------------------------
def _open_db() -> lancedb.DBConnection:
    Path(DB_PATH).mkdir(parents=True, exist_ok=True)
    return lancedb.connect(DB_PATH)


def _ensure_table(db: lancedb.DBConnection):
    if TABLE_NAME not in db.table_names():
        return db.create_table(TABLE_NAME, schema=SCHEMA)
    return db.open_table(TABLE_NAME)


# ---------------------------------------------------------------------------
# Public API  (matches the shape expected by routers/knowledge.py)
# ---------------------------------------------------------------------------
def ingest_document(workspace_id: int, text: str, source: str = "") -> int:
    """Chunk, embed, and store a document. Returns number of chunks written."""
    chunks = [c.strip() for c in text.split("\n\n") if len(c.strip()) >= 50]
    if not chunks:
        return 0

    db = _open_db()
    tbl = _ensure_table(db)

    rows: list[dict[str, Any]] = []
    for chunk in chunks:
        rows.append(
            {
                "workspace_id": workspace_id,
                "source": source,
                "text": chunk,
                "vector": get_gemini_embedding(chunk),
            },
        )

    tbl.add(rows)
    return len(rows)


def search_workspace_knowledge(workspace_id: int, query: str, limit: int = 5) -> str:
    """Vector search filtered to workspace_id. Returns formatted context string."""
    db = _open_db()
    tbl = _ensure_table(db)
    try:
        qvec = get_gemini_embedding(query)
        results = tbl.search(qvec).where(f"workspace_id = {workspace_id}").limit(limit).to_list()
        if not results:
            return "No internal documents found matching this query."
        return "\n---\n".join(f"Source: {r.get('source', '?')}\n{r['text']}" for r in results)
    except Exception as exc:
        return f"Internal search failed: {exc}"


# ---------------------------------------------------------------------------
# Legacy compat shim — routers/knowledge.py calls vector_db_manager.add_documents()
# ---------------------------------------------------------------------------
class _VectorDbManager:
    """Thin adapter so the existing router doesn't need rewriting."""

    def add_documents(self, documents: list[dict]) -> None:
        db = _open_db()
        tbl = _ensure_table(db)
        rows = []
        for doc in documents:
            rows.append(
                {
                    "workspace_id": int(doc.get("workspace_id", 1)),
                    "source": str(doc.get("source", "")),
                    "text": str(doc.get("text", doc.get("id", ""))),
                    "vector": [float(v) for v in doc["vector"]],
                },
            )
        if rows:
            tbl.add(rows)


vector_db_manager = _VectorDbManager()
