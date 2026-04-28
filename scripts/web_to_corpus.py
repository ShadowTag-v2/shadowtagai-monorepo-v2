#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""scripts/web_to_corpus.py — Web Scrape → Corpus Normalizer.
----------------------------------------------------------
Reads new items from data/web_ingest/ingest.db (IngestStore.items schema),
converts them into the langextract extractions schema (class/text/attrs),
and writes them into the extractions + FTS5 tables so that rag_evolve.py's
search_corpus() picks them up automatically.

Each extraction is trust-stamped:
  {"trust": "high|medium|low", "citable": true|false, "label": "VERIFIED|SYNTHESIS-ONLY"}

Source trust is determined by source prefix match — no Gemini calls, zero cost.

Usage:
    python3 scripts/web_to_corpus.py              # incremental pass
    python3 scripts/web_to_corpus.py --once        # same (alias)
    python3 scripts/web_to_corpus.py --dry-run     # print what would be written
    python3 scripts/web_to_corpus.py --stats       # show extraction counts by source
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
WEB_DB = REPO_ROOT / "data/web_ingest/ingest.db"

# ── Source Trust Registry ─────────────────────────────────────────────────────
# Key = prefix of `source` field in items table (matched with startswith)
# Order matters: more-specific keys first.
TRUST: dict[str, dict] = {
    # Verified / citable
    "news/reuters": {"trust": "high", "citable": True, "label": "VERIFIED"},
    "news/apnews": {"trust": "high", "citable": True, "label": "VERIFIED"},
    "news/bbc": {"trust": "high", "citable": True, "label": "VERIFIED"},
    "news/bloomberg": {"trust": "high", "citable": True, "label": "VERIFIED"},
    "news/nature": {"trust": "high", "citable": True, "label": "VERIFIED"},
    "news/sciencedaily": {"trust": "high", "citable": True, "label": "VERIFIED"},
    "news/cnbc": {"trust": "medium", "citable": True, "label": "VERIFIED"},
    "news/cnn": {"trust": "medium", "citable": True, "label": "VERIFIED"},
    "news/wired": {"trust": "medium", "citable": True, "label": "VERIFIED"},
    "news/techcrunch": {"trust": "medium", "citable": True, "label": "VERIFIED"},
    "news/theverge": {"trust": "medium", "citable": True, "label": "VERIFIED"},
    "news/arstechnica": {"trust": "medium", "citable": True, "label": "VERIFIED"},
    "news/venturebeat": {"trust": "medium", "citable": True, "label": "VERIFIED"},
    "news/yahoo": {"trust": "medium", "citable": True, "label": "VERIFIED"},
    "news/": {"trust": "medium", "citable": True, "label": "VERIFIED"},
    # Synthesis-only (social / unverified)
    "reddit/": {"trust": "low", "citable": False, "label": "SYNTHESIS-ONLY"},
    "4chan/": {"trust": "low", "citable": False, "label": "SYNTHESIS-ONLY"},
    "twitter_bypass/": {"trust": "low", "citable": False, "label": "SYNTHESIS-ONLY"},
    "instagram/": {"trust": "low", "citable": False, "label": "SYNTHESIS-ONLY"},
    "linkedin/": {"trust": "medium", "citable": False, "label": "SYNTHESIS-ONLY"},
    "darkweb/": {"trust": "low", "citable": False, "label": "SYNTHESIS-ONLY"},
    # last30days skill output — social/signal sources
    "last30days/hn": {"trust": "medium", "citable": False, "label": "SYNTHESIS-ONLY"},
    "last30days/polymarket": {"trust": "medium", "citable": False, "label": "SYNTHESIS-ONLY"},
    "last30days/web/": {"trust": "medium", "citable": False, "label": "SYNTHESIS-ONLY"},
    "last30days/reddit/": {"trust": "low", "citable": False, "label": "SYNTHESIS-ONLY"},
    "last30days/x/": {"trust": "low", "citable": False, "label": "SYNTHESIS-ONLY"},
    "last30days/youtube/": {"trust": "low", "citable": False, "label": "SYNTHESIS-ONLY"},
    "last30days/tiktok/": {"trust": "low", "citable": False, "label": "SYNTHESIS-ONLY"},
    "last30days/instagram/": {"trust": "low", "citable": False, "label": "SYNTHESIS-ONLY"},
    "last30days/bluesky/": {"trust": "low", "citable": False, "label": "SYNTHESIS-ONLY"},
    "last30days/truthsocial/": {"trust": "low", "citable": False, "label": "SYNTHESIS-ONLY"},
}

_DEFAULT_TRUST = {"trust": "low", "citable": False, "label": "SYNTHESIS-ONLY"}


def _trust_for(source: str) -> dict:
    for prefix, meta in TRUST.items():
        if source.startswith(prefix):
            return meta
    return _DEFAULT_TRUST


# ── Class Heuristic ───────────────────────────────────────────────────────────

_STAT_RE = re.compile(r"\b\d+\.?\d*\s*%|\b\d{4,}\b|\bpercent\b|\bGDP\b|\bmillion\b|\bbillion\b", re.IGNORECASE)
_RESEARCH_RE = re.compile(r"\bstudy\b|\bpaper\b|\bresearch\b|\bjournal\b|\barXiv\b|\bpreprint\b", re.IGNORECASE)
_SOCIAL_RE = re.compile(r"\bthink\b|\bfeel\b|\bIMO\b|\bLMK\b|\breddit\b|\b4chan\b|\bunpopular opinion\b", re.IGNORECASE)


def _classify(text: str, source: str) -> str:
    """Rule-based langextract class assignment. No API calls."""
    if "4chan" in source or "reddit" in source or _SOCIAL_RE.search(text or ""):
        return "concept"
    if _RESEARCH_RE.search(text or "") or "nature" in source or "arxiv" in source.lower():
        return "methodology" if "method" in (text or "").lower() else "evidence"
    if _STAT_RE.search(text or ""):
        return "evidence"
    return "claim"


# ── DB Helpers ────────────────────────────────────────────────────────────────


def _ensure_langextract_tables(conn: sqlite3.Connection) -> None:
    """Create extractions + processed + FTS5 if missing (idempotent)."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            source TEXT,
            title TEXT,
            content TEXT,
            url TEXT,
            author TEXT,
            metadata TEXT,
            ingested_at TEXT
        );
        CREATE TABLE IF NOT EXISTS processed (
            file_id TEXT PRIMARY KEY,
            name    TEXT,
            status  TEXT,
            count   INTEGER DEFAULT 0,
            ts      TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS extractions (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id TEXT,
            name    TEXT,
            class   TEXT,
            text    TEXT,
            attrs   TEXT
        );
    """)
    # FTS5 — build only if absent
    row = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='extractions_fts'").fetchone()
    if not row:
        conn.execute("CREATE VIRTUAL TABLE extractions_fts USING fts5(text, name, class, content='extractions', content_rowid='id')")
        conn.execute("INSERT INTO extractions_fts(extractions_fts) VALUES('rebuild')")
    # Trigger — create only if absent
    trg = conn.execute("SELECT name FROM sqlite_master WHERE type='trigger' AND name='extractions_ai'").fetchone()
    if not trg:
        conn.execute("""
            CREATE TRIGGER extractions_ai AFTER INSERT ON extractions BEGIN
                INSERT INTO extractions_fts(rowid, text, name, class)
                VALUES (new.id, new.text, new.name, new.class);
            END
        """)
    conn.commit()


def _already_processed(conn: sqlite3.Connection, item_id: str) -> bool:
    return bool(conn.execute("SELECT 1 FROM processed WHERE file_id=?", (item_id,)).fetchone())


# ── Main Normalizer ────────────────────────────────────────────────────────────


def normalize(dry_run: bool = False) -> dict[str, int]:
    """Incremental pass: read new items → write extractions.
    Returns {"processed": N, "skipped": N, "errors": N}.
    """
    if not WEB_DB.exists():
        return {"processed": 0, "skipped": 0, "errors": 0}

    conn = sqlite3.connect(str(WEB_DB))
    conn.row_factory = sqlite3.Row

    # Ensure both schemas coexist in the same DB
    _ensure_langextract_tables(conn)

    # Fetch all items not yet in processed table
    rows = conn.execute("""
        SELECT id, source, title, content, url, author, metadata, ingested_at
        FROM items
        WHERE id NOT IN (SELECT file_id FROM processed)
        ORDER BY ingested_at ASC
    """).fetchall()

    stats = {"processed": 0, "skipped": 0, "errors": 0}

    for row in rows:
        item_id = row["id"]
        source = row["source"] or ""
        title = row["title"] or ""
        content = row["content"] or ""
        url = row["url"] or ""
        ingested_at = row["ingested_at"] or ""

        # Skip near-empty items
        text = content.strip() or title.strip()
        if len(text) < 30:
            stats["skipped"] += 1
            continue

        trust = _trust_for(source)
        extraction_class = _classify(text, source)

        # Parse metadata for engagement signals
        try:
            meta = json.loads(row["metadata"] or "{}")
        except Exception:
            meta = {}

        attrs = json.dumps(
            {
                "source_url": url,
                "trust": trust["trust"],
                "citable": trust["citable"],
                "label": trust["label"],
                "adapter": source,
                "score": meta.get("score", meta.get("like_count", 0)),
                "ingested_at": ingested_at,
            },
        )

        # Display name: "source_prefix: title[:60]"
        name = f"{source}: {title[:60]}"

        if dry_run:
            stats["processed"] += 1
            continue

        try:
            conn.execute(
                "INSERT INTO extractions (file_id, name, class, text, attrs) VALUES (?,?,?,?,?)",
                (item_id, name, extraction_class, text[:4000], attrs),
            )
            conn.execute(
                "INSERT OR IGNORE INTO processed (file_id, name, status, count) VALUES (?,?,?,?)",
                (item_id, name, "ok", 1),
            )
            stats["processed"] += 1
        except Exception:
            stats["errors"] += 1

    if not dry_run:
        conn.commit()

    conn.close()
    return stats


def show_stats() -> None:
    if not WEB_DB.exists():
        return
    conn = sqlite3.connect(str(WEB_DB))
    rows = conn.execute("SELECT source, COUNT(*) FROM items GROUP BY source ORDER BY COUNT(*) DESC").fetchall()
    conn.execute("SELECT COUNT(*) FROM extractions").fetchone()
    conn.execute("SELECT COUNT(*) FROM items").fetchone()
    conn.close()
    for _src, _cnt in rows:
        pass


# ── CLI ────────────────────────────────────────────────────────────────────────


def main() -> None:
    ap = argparse.ArgumentParser(description="Normalize web scrape items into corpus extractions")
    ap.add_argument("--once", action="store_true", help="Run one pass (default behavior)")
    ap.add_argument("--dry-run", action="store_true", help="Print what would be written, no DB writes")
    ap.add_argument("--stats", action="store_true", help="Show extraction counts by source")
    args = ap.parse_args()

    if args.stats:
        show_stats()
        return

    normalize(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
