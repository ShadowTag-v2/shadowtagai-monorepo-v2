#!/usr/bin/env python3
"""scripts/corpus_lancedb_embed.py — Create LanceDB semantic search table from Drive corpus.

Loads the 1,094 extracted documents from data/drive_ingest/extractions.jsonl,
embeds them using a local sentence transformer, and stores in LanceDB for
fast vector similarity search.

Usage:
    python3 scripts/corpus_lancedb_embed.py             # Build table
    python3 scripts/corpus_lancedb_embed.py --query "Stripe webhooks"
    python3 scripts/corpus_lancedb_embed.py --stats
"""
from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path

REPO = Path(__file__).parent.parent
JSONL = REPO / "data/drive_ingest/extractions.jsonl"
LANCE_DIR = REPO / "data/lance_corpus"
TABLE_NAME = "drive_docs"

def load_corpus():
    docs = []
    with JSONL.open(encoding="utf-8") as f:
        for line in f:
            try: docs.append(json.loads(line.strip()))
            except: pass
    return docs

def build_table():
    try:
        import lancedb
    except ImportError:
        print("Installing lancedb..."); import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "lancedb", "-q"])
        import lancedb

    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("Installing sentence-transformers..."); import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "sentence-transformers", "-q"])
        from sentence_transformers import SentenceTransformer

    print("Loading corpus...")
    docs = load_corpus()
    print(f"  {len(docs)} documents loaded")

    # Truncate content for embedding (max 512 tokens ~ 2048 chars)
    texts = [d.get("raw_content", "")[:2048] for d in docs]

    print("Loading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Embedding documents...")
    t0 = time.time()
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=64)
    dt = time.time() - t0
    print(f"  Embedded {len(embeddings)} docs in {dt:.1f}s ({len(embeddings)/dt:.0f} docs/s)")

    # Build LanceDB table
    print(f"Creating LanceDB table at {LANCE_DIR}...")
    db = lancedb.connect(str(LANCE_DIR))

    records = []
    for i, doc in enumerate(docs):
        records.append({
            "vector": embeddings[i].tolist(),
            "document_id": doc.get("document_id", f"doc_{i}"),
            "source_file": doc.get("source_file", ""),
            "format": doc.get("format", ""),
            "content": doc.get("raw_content", "")[:4096],  # Store truncated for display
            "byte_size": doc.get("byte_size", 0),
            "content_hash": doc.get("content_hash", ""),
        })

    # Drop existing table if present
    try: db.drop_table(TABLE_NAME)
    except: pass

    tbl = db.create_table(TABLE_NAME, records)
    print(f"  Table '{TABLE_NAME}' created: {len(records)} rows, {len(embeddings[0])}-dim vectors")
    return tbl

def query_table(q, top_k=5):
    import lancedb
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    db = lancedb.connect(str(LANCE_DIR))
    tbl = db.open_table(TABLE_NAME)
    vec = model.encode([q])[0].tolist()
    results = tbl.search(vec).limit(top_k).to_pandas()
    print(f"\n🔍 Semantic search: \"{q}\"")
    print(f"   Found: {len(results)} results")
    print("─" * 60)
    for i, row in results.iterrows():
        print(f"\n  [{i+1}] {row['source_file']}")
        print(f"      Score: {row.get('_distance', '?'):.4f} | Size: {row['byte_size']} bytes")
        preview = row['content'][:200].replace('\n', ' ')
        print(f"      ...{preview}...")

def show_stats():
    import lancedb
    db = lancedb.connect(str(LANCE_DIR))
    tbl = db.open_table(TABLE_NAME)
    df = tbl.to_pandas()
    print(f"{'═'*60}\n  LANCEDB CORPUS — Stats\n{'═'*60}")
    print(f"  Rows: {len(df)} | Dims: {len(df['vector'].iloc[0])}")
    print(f"  Total content: {df['byte_size'].sum():,} bytes")
    print(f"  Formats: {dict(df['format'].value_counts())}")
    print(f"  Path: {LANCE_DIR}\n{'═'*60}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--query", "-q", type=str, help="Semantic search query")
    p.add_argument("--stats", action="store_true")
    p.add_argument("--top", type=int, default=5)
    a = p.parse_args()
    if a.query: query_table(a.query, a.top)
    elif a.stats: show_stats()
    else: build_table()
