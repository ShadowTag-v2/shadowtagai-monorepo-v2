#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
HUD Query Memory — Cor.Gemini Sovereign RAG v2
Queries local ChromaDB + beads_index.sqlite using all-MiniLM-L6-v2.
Fixes: explicit embed_fn binding (no SequentialMemoryService abstraction dead-end).

Usage: python scripts/hud_query_memory.py "your search query"
       python scripts/hud_query_memory.py "agent routing" --top=15
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

MONOREPO_ROOT = Path(__file__).parent.parent
CHROMA_PATH = MONOREPO_ROOT / ".chroma_db"
BEADS_DB = MONOREPO_ROOT / "data" / "beads_index.sqlite"
COLLECTION_NAME = "coryay_knowledge"
EMBED_MODEL = "all-MiniLM-L6-v2"


def _get_embedder():
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("[ERROR] Run: pip install sentence-transformers", file=sys.stderr)
        sys.exit(1)
    return SentenceTransformer(EMBED_MODEL)


def _get_chroma_collection():
    try:
        import chromadb
    except ImportError:
        print("[ERROR] Run: pip install chromadb", file=sys.stderr)
        sys.exit(1)
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    return client.get_or_create_collection(COLLECTION_NAME)


def query_chroma(query: str, top_k: int) -> list[dict]:
    model = _get_embedder()
    vec = model.encode(query).tolist()
    col = _get_chroma_collection()
    count = col.count()
    if count == 0:
        print(f"[WARN] '{COLLECTION_NAME}' is empty — run: python scripts/reindex_monorepo.py", file=sys.stderr)
        return []
    n = min(top_k, count)
    results = col.query(query_embeddings=[vec], n_results=n, include=["documents", "metadatas", "distances"])
    hits = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        hits.append(
            {
                "text": doc[:400],
                "source": meta.get("source", meta.get("filename", "unknown")),
                "chunk": meta.get("chunk", 0),
                "distance": round(float(dist), 4),
            }
        )
    return hits


def query_beads(query: str, top_k: int) -> list[dict]:
    """Full-text scan of beads_index.sqlite, corrected path binding."""
    # Resolve path relative to monorepo root — fixes the stale aiyou-stack path bug
    db_path = BEADS_DB
    if not db_path.exists():
        # Fallback: old location
        db_path = MONOREPO_ROOT / ".beads" / "beads_index.sqlite"
    if not db_path.exists():
        return []

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Try FTS5 table first
    try:
        cur.execute(
            "SELECT content, file_path FROM beads_fts WHERE beads_fts MATCH ? LIMIT ?",
            (query, top_k),
        )
        rows = cur.fetchall()
        conn.close()
        return [{"text": r[0][:300], "source": r[1]} for r in rows]
    except sqlite3.OperationalError:
        pass

    # Fallback: keyword scan on beads_registry (path only)
    try:
        term = query.split()[0] if query.split() else query
        cur.execute(
            "SELECT filepath FROM beads_registry WHERE filepath LIKE ? LIMIT ?",
            (f"%{term}%", top_k),
        )
        rows = cur.fetchall()
        conn.close()
        return [{"source": r[0], "text": "(path match only)"} for r in rows]
    except sqlite3.OperationalError:
        conn.close()
        return []


def main() -> None:
    parser = argparse.ArgumentParser(description="Query local sovereign RAG engine")
    parser.add_argument("query", nargs="+", help="Search query text")
    parser.add_argument("--top", type=int, default=10, help="Max results (default 10)")
    parser.add_argument("--chroma-only", action="store_true")
    parser.add_argument("--beads-only", action="store_true")
    args = parser.parse_args()

    query = " ".join(args.query)
    top_k = args.top

    print(f"\n[HUD] Query   : {query!r}")
    print(f"[HUD] Chroma  : {CHROMA_PATH}")
    print(f"[HUD] Beads   : {BEADS_DB}")
    print(f"[HUD] Model   : {EMBED_MODEL}\n")

    if not args.beads_only:
        hits = query_chroma(query, top_k)
        if hits:
            print(f"=== ChromaDB ({len(hits)} results) ===")
            for i, h in enumerate(hits, 1):
                print(f"[{i}] dist={h['distance']}  chunk={h['chunk']}  {h['source']}")
                print(f"     {h['text'][:200]}\n")
        else:
            print("=== ChromaDB: 0 results ===\n")

    if not args.chroma_only:
        hits = query_beads(query, top_k)
        if hits:
            print(f"=== Beads SQLite ({len(hits)} results) ===")
            for i, h in enumerate(hits, 1):
                print(f"[{i}] {h['source']}")
                if h["text"] != "(path match only)":
                    print(f"     {h['text'][:200]}\n")
        else:
            print("=== Beads SQLite: 0 results ===\n")


if __name__ == "__main__":
    main()
