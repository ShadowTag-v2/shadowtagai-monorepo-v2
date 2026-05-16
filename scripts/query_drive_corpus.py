#!/usr/bin/env python3
"""scripts/query_drive_corpus.py — Query the Drive Ingest Extraction Corpus.

Loads the 1,086+ extracted documents from data/drive_ingest/extractions.jsonl
and provides keyword search, semantic filtering, and export capabilities.

Usage:
    python3 scripts/query_drive_corpus.py "NIST compliance"
    python3 scripts/query_drive_corpus.py --list-sources
    python3 scripts/query_drive_corpus.py --stats
    python3 scripts/query_drive_corpus.py "Stripe" --format json
    python3 scripts/query_drive_corpus.py "patent" --top 5
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
JSONL_PATH = REPO_ROOT / "data/drive_ingest/extractions.jsonl"
MARKDOWN_DIR = REPO_ROOT / "data/drive_ingest/markdown"


def load_corpus() -> list[dict]:
    """Load all documents from the JSONL extraction file."""
    if not JSONL_PATH.exists():
        print(f"ERROR: Corpus not found at {JSONL_PATH}", file=sys.stderr)
        sys.exit(1)

    docs = []
    for line in JSONL_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                docs.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return docs


def search_corpus(docs: list[dict], query: str, top: int = 10) -> list[dict]:
    """Search documents by keyword(s). Returns ranked results."""
    terms = query.lower().split()
    scored = []
    for doc in docs:
        content = doc.get("raw_content", "").lower()
        source = doc.get("source_file", "").lower()
        score = 0
        for term in terms:
            # Count occurrences in content
            score += len(re.findall(re.escape(term), content))
            # Boost for matches in source filename
            if term in source:
                score += 5
        if score > 0:
            scored.append((score, doc))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in scored[:top]]


def print_stats(docs: list[dict]) -> None:
    """Print corpus statistics."""
    formats = {}
    total_bytes = 0
    for doc in docs:
        fmt = doc.get("format", "unknown")
        formats[fmt] = formats.get(fmt, 0) + 1
        total_bytes += doc.get("byte_size", 0)

    md_count = len(list(MARKDOWN_DIR.glob("*.md"))) if MARKDOWN_DIR.exists() else 0

    print("═" * 60)
    print("  DRIVE INGEST CORPUS — Statistics")
    print("═" * 60)
    print(f"  Total documents:     {len(docs):,}")
    print(f"  Unique sources:      {len(set(d.get('source_file','') for d in docs)):,}")
    print(f"  Total content:       {total_bytes:,} bytes ({total_bytes/1024/1024:.1f} MB)")
    print(f"  Markdown files:      {md_count:,}")
    print(f"  Formats:             {formats}")
    print("═" * 60)


def print_sources(docs: list[dict]) -> None:
    """List all source files."""
    sources = sorted(set(d.get("source_file", "") for d in docs))
    for i, s in enumerate(sources, 1):
        print(f"  {i:4d}. {s}")
    print(f"\n  Total: {len(sources)} sources")


def print_results(results: list[dict], query: str, fmt: str = "text") -> None:
    """Print search results."""
    if fmt == "json":
        output = []
        for doc in results:
            output.append({
                "source_file": doc.get("source_file", ""),
                "format": doc.get("format", ""),
                "byte_size": doc.get("byte_size", 0),
                "content_preview": doc.get("raw_content", "")[:500],
            })
        print(json.dumps(output, indent=2))
        return

    print(f"\n🔍 Search results for: \"{query}\"")
    print(f"   Found: {len(results)} documents")
    print("─" * 60)

    for i, doc in enumerate(results, 1):
        source = doc.get("source_file", "unknown")
        fmt_type = doc.get("format", "?")
        size = doc.get("byte_size", 0)
        content = doc.get("raw_content", "")

        # Find and show context around the query terms
        preview = ""
        lower_content = content.lower()
        for term in query.lower().split():
            idx = lower_content.find(term)
            if idx >= 0:
                start = max(0, idx - 80)
                end = min(len(content), idx + len(term) + 80)
                snippet = content[start:end].replace("\n", " ").strip()
                preview = f"...{snippet}..."
                break

        if not preview:
            preview = content[:160].replace("\n", " ").strip() + "..."

        print(f"\n  [{i}] {source}")
        print(f"      Format: {fmt_type} | Size: {size:,} bytes")
        print(f"      {preview}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Query the Drive Ingest Corpus")
    ap.add_argument("query", nargs="?", help="Search query (keywords)")
    ap.add_argument("--stats", action="store_true", help="Show corpus statistics")
    ap.add_argument("--list-sources", action="store_true", help="List all source files")
    ap.add_argument("--top", type=int, default=10, help="Number of results (default: 10)")
    ap.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )
    args = ap.parse_args()

    docs = load_corpus()

    if args.stats:
        print_stats(docs)
        return

    if args.list_sources:
        print_sources(docs)
        return

    if not args.query:
        print_stats(docs)
        print("\nUsage: python3 scripts/query_drive_corpus.py \"search terms\"")
        return

    results = search_corpus(docs, args.query, top=args.top)
    print_results(results, args.query, fmt=args.format)


if __name__ == "__main__":
    main()
