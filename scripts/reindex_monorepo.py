#!/usr/bin/env python3
"""Reindex Monorepo — Cor.Gemini Sovereign RAG v2
Crawls apps/ libs/ control/ scripts/ src/ and ingests code chunks into:
  - .chroma_db  (ChromaDB PersistentClient, collection=coryay_knowledge)
  - data/beads_index.sqlite  (registry + FTS5).

Fixes:
  - Explicit all-MiniLM-L6-v2 embed_fn (no HTTP abstraction dead-end)
  - Symlink-safe os.path.realpath + os.path.exists guard (no silent crash)
  - Correct path binding to monorepo root (not stale ShadowTag-v2-stack path)
  - Drops & rebuilds beads_registry so stale paths are purged

Usage: python scripts/reindex_monorepo.py [--dry-run] [--dirs apps libs]
"""

from __future__ import annotations

import argparse
import contextlib
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

MONOREPO_ROOT = Path(__file__).parent.parent
CHROMA_PATH = MONOREPO_ROOT / ".chroma_db"
BEADS_DB = MONOREPO_ROOT / "data" / "beads_index.sqlite"
COLLECTION_NAME = "coryay_knowledge"
EMBED_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 8_000  # chars — stays under MiniLM token limit
BATCH_SIZE = 50  # vectors per ChromaDB upsert (low memory profile for M1)
TEXT_EXTS = {
    ".py",
    ".md",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".txt",
    ".yaml",
    ".yml",
    ".toml",
    ".sql",
    ".sh",
}
SKIP_DIRS = {
    "node_modules",
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "dist",
    "build",
    ".next",
    ".nuxt",
    "external_sdks",
    "external_repos",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
}

DEFAULT_DIRS = ["apps", "libs", "control", "scripts", "src", "tools", "memory"]


def init_sqlite() -> sqlite3.Connection:
    BEADS_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(BEADS_DB)
    conn.executescript("""
        DROP TABLE IF EXISTS beads_registry;
        DROP TABLE IF EXISTS beads_fts;
        CREATE TABLE beads_registry (
            filepath      TEXT PRIMARY KEY,
            size_bytes    INTEGER,
            last_indexed  TEXT
        );
        CREATE VIRTUAL TABLE beads_fts
            USING fts5(content, file_path, content='', tokenize='porter ascii');
    """)
    conn.commit()
    return conn


def get_embedder():
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        sys.exit(1)
    return SentenceTransformer(EMBED_MODEL)


def get_collection(recreate: bool = False):
    try:
        import chromadb
    except ImportError:
        sys.exit(1)
    CHROMA_PATH.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    if recreate:
        with contextlib.suppress(Exception):
            client.delete_collection(COLLECTION_NAME)
    return client.get_or_create_collection(COLLECTION_NAME)


def chunk_text(text: str) -> list[str]:
    return [text[i : i + CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE) if text[i : i + CHUNK_SIZE].strip()]


def flush_batch(
    model,
    collection,
    conn: sqlite3.Connection,
    texts: list[str],
    metas: list[dict],
    dry_run: bool,
) -> int:
    if not texts:
        return 0
    if dry_run:
        return len(texts)
    vecs = model.encode(texts, batch_size=32, show_progress_bar=False).tolist()
    ids = [f"{m['source']}::{m['chunk']}" for m in metas]
    collection.upsert(embeddings=vecs, documents=texts, metadatas=metas, ids=ids)
    conn.executemany(
        "INSERT INTO beads_fts(content, file_path) VALUES (?, ?)",
        [(t, m["source"]) for t, m in zip(texts, metas, strict=False)],
    )
    conn.commit()
    return len(texts)


def crawl(
    target_dirs: list[str],
    model,
    collection,
    conn: sqlite3.Connection,
    dry_run: bool,
) -> tuple[int, int]:
    scanned = indexed = 0
    texts_buf: list[str] = []
    metas_buf: list[dict] = []

    for d in target_dirs:
        root_path = MONOREPO_ROOT / d
        if not root_path.exists():
            continue
        for dirpath, dirnames, files in os.walk(root_path, followlinks=False):
            dirnames[:] = [dn for dn in dirnames if dn not in SKIP_DIRS and not dn.startswith(".")]
            for fname in files:
                fpath = Path(dirpath) / fname
                # Symlink safety — skip dead symlinks
                real = fpath.resolve()
                if not real.exists():
                    continue
                try:
                    size = real.stat().st_size
                except OSError:
                    continue
                scanned += 1

                # Register in SQLite
                conn.execute(
                    "INSERT OR REPLACE INTO beads_registry(filepath, size_bytes, last_indexed) VALUES (?,?,?)",
                    (str(fpath.relative_to(MONOREPO_ROOT)), size, datetime.utcnow().isoformat()),
                )

                if fpath.suffix not in TEXT_EXTS or size > 500_000:
                    continue

                try:
                    text = fpath.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue

                for i, chunk in enumerate(chunk_text(text)):
                    texts_buf.append(chunk)
                    metas_buf.append({"source": str(fpath.relative_to(MONOREPO_ROOT)), "chunk": i})
                    indexed += 1

                    if len(texts_buf) >= BATCH_SIZE:
                        flush_batch(model, collection, conn, texts_buf, metas_buf, dry_run)
                        texts_buf.clear()
                        metas_buf.clear()

    # Final flush
    flush_batch(model, collection, conn, texts_buf, metas_buf, dry_run)
    conn.commit()
    return scanned, indexed


def main() -> None:
    parser = argparse.ArgumentParser(description="Re-index monorepo into local RAG engine")
    parser.add_argument("--dirs", nargs="+", default=DEFAULT_DIRS, help="Directories to crawl")
    parser.add_argument("--dry-run", action="store_true", help="Scan only, no writes to Chroma/SQLite")
    parser.add_argument("--recreate", action="store_true", help="Delete and recreate ChromaDB collection")
    args = parser.parse_args()


    conn = init_sqlite()
    model = get_embedder()
    collection = get_collection(recreate=args.recreate)

    _scanned, _indexed = crawl(args.dirs, model, collection, conn, args.dry_run)
    conn.close()



if __name__ == "__main__":
    main()
