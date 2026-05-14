# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any
import lancedb
import pyarrow as pa
from ..providers.embeddings import embed_text

TABLE_NAME = "ane_chunks"
EMBED_DIM = 1536


def connect(root: str):
    Path(root).mkdir(parents=True, exist_ok=True)
    return lancedb.connect(root)


def ensure_table(root: str):
    db = connect(root)
    schema = pa.schema(
        [
            pa.field("chunk_id", pa.string()),
            pa.field("doc_id", pa.string()),
            pa.field("repo_id", pa.string()),
            pa.field("rel_path", pa.string()),
            pa.field("chunk_type", pa.string()),
            pa.field("language", pa.string()),
            pa.field("title", pa.string()),
            pa.field("content", pa.string()),
            pa.field("section_path", pa.string()),
            pa.field("start_line", pa.int32()),
            pa.field("end_line", pa.int32()),
            pa.field("importance", pa.float32()),
            pa.field("sha256", pa.string()),
            pa.field("metadata_json", pa.string()),
            pa.field("embedding", pa.list_(pa.float32(), EMBED_DIM)),
        ]
    )
    if TABLE_NAME not in db.table_names():
        db.create_table(TABLE_NAME, schema=schema)
    return db.open_table(TABLE_NAME)


def _delete_existing(table, chunk_ids: list[str]):
    # robust per-id delete semantics; slower than a true merge, but correct
    for cid in chunk_ids:
        try:
            table.delete(f"chunk_id = '{cid}'")
        except Exception:
            pass


def upsert_chunks(root: str, chunks: list[dict[str, Any]]):
    table = ensure_table(root)
    rows = []
    chunk_ids = []
    for c in chunks:
        row = dict(c)
        row["embedding"] = embed_text(row["content"])
        rows.append(row)
        chunk_ids.append(str(row["chunk_id"]))
    if rows:
        _delete_existing(table, chunk_ids)
        table.add(rows)
    return {"upserted": len(rows)}


def delete_doc_chunks(root: str, doc_id: str):
    table = ensure_table(root)
    try:
        table.delete(f"doc_id = '{doc_id}'")
    except Exception:
        pass
    return {"deleted_doc_id": doc_id}


def search(root: str, query: str, limit: int = 8):
    table = ensure_table(root)
    qvec = embed_text(query)
    try:
        return table.search(qvec).limit(limit).to_list()
    except Exception:
        return []


def keyword_search(root: str, query: str, limit: int = 8):
    table = ensure_table(root)
    try:
        # fallback keyword-like filter by title/content if FTS isn't configured
        rows = table.to_list()
        q = query.lower()
        hits = [r for r in rows if q in str(r.get("title", "")).lower() or q in str(r.get("content", "")).lower()]
        return hits[:limit]
    except Exception:
        return []
