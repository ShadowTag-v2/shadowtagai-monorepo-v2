#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations

import argparse
import os
import uuid
from pathlib import Path
from typing import Any

import lancedb
import vertexai
from lancedb.pydantic import LanceModel, Vector
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel


def getenv_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v4")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

DB_URI = os.environ.get(
    "LANCEDB_URI",
    "/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.lancedb",
)
TABLE_NAME = os.environ.get("LANCEDB_TABLE", "pnkln_knowledge")
EMBED_MODEL_NAME = os.environ.get("VERTEX_EMBED_MODEL", "text-embedding-004")
EMBED_DIM = int(os.environ.get("VERTEX_EMBED_DIM", "768"))
TOP_K = int(os.environ.get("pnkln_TOP_K", "8"))
RECREATE_TABLE = getenv_bool("pnkln_RECREATE_TABLE", False)

_vertex_inited = False
_model: TextEmbeddingModel | None = None


def ensure_vertex() -> TextEmbeddingModel:
    global _vertex_inited, _model
    if not _vertex_inited:
        from google.oauth2.credentials import Credentials

        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", ["https://www.googleapis.com/auth/cloud-platform"])
        vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=creds)
        _vertex_inited = True
    if _model is None:
        _model = TextEmbeddingModel.from_pretrained(EMBED_MODEL_NAME)
    return _model


class pnklnDoc(LanceModel):
    id: str
    text: str
    vector: Vector(EMBED_DIM)
    source: str
    kind: str = "note"


def embed_texts(
    texts: list[str],
    task_type: str = "RETRIEVAL_DOCUMENT",
) -> list[list[float]]:
    model = ensure_vertex()
    inputs = [TextEmbeddingInput(text=t, task_type=task_type) for t in texts]
    embeddings = model.get_embeddings(
        inputs,
        output_dimensionality=EMBED_DIM,
    )
    return [list(item.values) for item in embeddings]


def ensure_db() -> Any:
    Path(DB_URI).mkdir(parents=True, exist_ok=True)
    return lancedb.connect(DB_URI)


def ensure_table(db: Any) -> Any:
    existing = set(db.table_names())

    if RECREATE_TABLE and TABLE_NAME in existing:
        db.drop_table(TABLE_NAME)
        existing.remove(TABLE_NAME)

    if TABLE_NAME not in existing:
        return db.create_table(TABLE_NAME, schema=pnklnDoc)

    return db.open_table(TABLE_NAME)


def create_index_if_requested(table: Any) -> None:
    index_type = os.environ.get("LANCEDB_INDEX_TYPE", "").strip().upper()
    if not index_type:
        return
    try:
        if index_type == "IVF_PQ":
            table.create_index(
                vector_column_name="vector",
                index_type="IVF_PQ",
            )
    except Exception as exc:
        print(f"Index creation skipped or failed harmlessly: {exc}")


def seed_if_empty(table: Any) -> None:
    if table.count_rows() > 0:
        return

    docs = [
        {
            "id": "1",
            "text": "pnkln uses LanceDB for local vector retrieval.",
            "source": "bootstrap",
            "kind": "system",
        },
        {
            "id": "2",
            "text": "pnkln uses Vertex AI text embeddings with gemini-embedding-001.",
            "source": "bootstrap",
            "kind": "system",
        },
        {
            "id": "3",
            "text": "gemini-3.1-flash-lite-preview is the required Google model for pnkln command tests.",
            "source": "bootstrap",
            "kind": "system",
        },
    ]

    vectors = embed_texts([d["text"] for d in docs], task_type="RETRIEVAL_DOCUMENT")
    rows = [{**doc, "vector": vec} for doc, vec in zip(docs, vectors)]
    table.add(rows)


def add_text(table: Any, text: str, source: str, kind: str = "note") -> None:
    vector = embed_texts([text], task_type="RETRIEVAL_DOCUMENT")[0]
    table.add(
        [
            {
                "id": str(uuid.uuid4()),
                "text": text,
                "vector": vector,
                "source": source,
                "kind": kind,
            }
        ]
    )


def ingest_jsonl(table: Any, jsonl_path: str) -> None:
    import json
    import hashlib

    print("Loading existing LanceDB vectors to checkpoint resume state...")
    try:
        # lancedb queries return dicts or PyArrow, so we use to_arrow or to_list
        existing_ids = set([r["id"] for r in table.search().limit(10000000).select(["id"]).to_list()])
    except Exception as e:
        print(f"Checkpoint check warning (normal for fresh DB): {e}")
        existing_ids = set()
    print(f"Found {len(existing_ids)} vectors in LanceDB table '{TABLE_NAME}'.")

    docs_to_embed = []
    batch_size = 250
    total_added = 0

    def process_batch():
        nonlocal total_added
        if not docs_to_embed:
            return
        print(f"Embedding batch of {len(docs_to_embed)} memories...")
        texts = [d["text"] for d in docs_to_embed]
        vectors = embed_texts(texts, task_type="RETRIEVAL_DOCUMENT")
        rows = [{**doc, "vector": vec} for doc, vec in zip(docs_to_embed, vectors)]
        table.add(rows)
        total_added += len(rows)
        docs_to_embed.clear()

    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue

            text = row.get("text", "").strip()
            if not text:
                continue

            fid = row.get("file_id", "unknown")
            doc_id = hashlib.md5(f"{fid}_{text}".encode()).hexdigest()

            if doc_id in existing_ids:
                continue

            doc_class = row.get("class", "note")
            source = row.get("source") or fid
            docs_to_embed.append(
                {
                    "id": doc_id,
                    "text": text[:9000],  # safety cutoff for vertex token limit per instance
                    "kind": doc_class,
                    "source": source,
                }
            )

            if len(docs_to_embed) >= batch_size:
                process_batch()

    process_batch()
    print(f"Ingestion complete. Added {total_added} net-new vectors.")


def search(table: Any, query: str, top_k: int = TOP_K) -> list[dict[str, Any]]:
    query_vector = embed_texts([query], task_type="RETRIEVAL_QUERY")[0]
    return table.search(query_vector).limit(top_k).to_list()


def smoke_test() -> int:
    db = ensure_db()
    table = ensure_table(db)
    seed_if_empty(table)
    create_index_if_requested(table)

    query = "What does pnkln use for embeddings?"
    results = search(table, query, top_k=3)

    print(f"Project: {PROJECT_ID}")
    print(f"Location: {LOCATION}")
    print(f"DB URI: {DB_URI}")
    print(f"Table: {TABLE_NAME}")
    print(f"Embedding model: {EMBED_MODEL_NAME}")
    print(f"Embedding dim: {EMBED_DIM}")
    print(f"Rows: {table.count_rows()}")
    print(f"Query: {query}")
    print("Results:")
    for i, row in enumerate(results, start=1):
        print(f"{i}. id={row.get('id')} source={row.get('source')} text={row.get('text')}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="pnkln LanceDB + Vertex AI embeddings bootstrap")
    parser.add_argument("--smoke-test", action="store_true", help="Run smoke test")
    parser.add_argument("--add-text", type=str, default=None, help="Add a text record")
    parser.add_argument("--ingest", type=str, default=None, help="Path to extractions.jsonl to batch ingest")
    parser.add_argument("--source", type=str, default="manual", help="Source for added text")
    parser.add_argument("--kind", type=str, default="note", help="Kind for added text")
    parser.add_argument("--query", type=str, default=None, help="Run a query")
    parser.add_argument("--top-k", type=int, default=TOP_K, help="Top K results")
    args = parser.parse_args()

    db = ensure_db()
    table = ensure_table(db)
    seed_if_empty(table)

    if args.add_text:
        add_text(table, args.add_text, args.source, args.kind)
        print("Added text record.")

    if args.ingest:
        if not os.path.exists(args.ingest):
            print(f"Error: Could not find JSONL file: {args.ingest}")
            return 1
        ingest_jsonl(table, args.ingest)
        return 0

    if args.query:
        results = search(table, args.query, args.top_k)
        for i, row in enumerate(results, start=1):
            print(f"{i}. id={row.get('id')} source={row.get('source')} text={row.get('text')}")
        return 0

    if args.smoke_test:
        return smoke_test()

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
