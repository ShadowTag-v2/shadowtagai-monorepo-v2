#!/usr/bin/env python3
"""scripts/last30days_to_ingest.py — last30days skill → IngestStore bridge.
------------------------------------------------------------------------
Runs the last30days research skill for a given topic and funnels its
structured JSON output into data/web_ingest/ingest.db so that
web_to_corpus.py and rag_evolve.py pick it up on the next pass.

Usage:
    python3 scripts/last30days_to_ingest.py "AI funding Q1 2026"
    python3 scripts/last30days_to_ingest.py "LLM inference" --quick
    python3 scripts/last30days_to_ingest.py "legal AI tools" --deep --search reddit,hn
    python3 scripts/last30days_to_ingest.py "topic" --dry-run   # print without saving
    python3 scripts/last30days_to_ingest.py "topic" --mock      # use fixtures (no API calls)

Source prefixes written to ingest.db (honoured by web_to_corpus.py trust registry):
    last30days/reddit/<subreddit>    → low  / SYNTHESIS-ONLY
    last30days/x/<handle>            → low  / SYNTHESIS-ONLY
    last30days/hn                    → medium / SYNTHESIS-ONLY
    last30days/youtube/<channel>     → low  / SYNTHESIS-ONLY
    last30days/tiktok/<author>       → low  / SYNTHESIS-ONLY
    last30days/instagram/<author>    → low  / SYNTHESIS-ONLY
    last30days/bluesky/<handle>      → low  / SYNTHESIS-ONLY
    last30days/truthsocial/<handle>  → low  / SYNTHESIS-ONLY
    last30days/polymarket            → medium / SYNTHESIS-ONLY
    last30days/web/<domain>          → medium / SYNTHESIS-ONLY
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SKILL_SCRIPT = Path.home() / ".claude/skills/last30days/scripts/last30days.py"
WEB_DB = REPO_ROOT / "data/web_ingest/ingest.db"

# Add ingestion package to path
sys.path.insert(0, str(REPO_ROOT / "apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services"))


def _uid(prefix: str, url: str) -> str:
    h = hashlib.md5(url.encode()).hexdigest()[:10]
    return f"l30d_{prefix}_{h}"


def _parse_dt(s: str | None) -> datetime:
    if not s:
        return datetime.utcnow()
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(s[:19], fmt[: len(s[:19])])
        except ValueError:
            continue
    return datetime.utcnow()


def report_to_items(report: dict) -> list[dict]:
    """Flatten a last30days Report JSON into IngestStore-compatible dicts."""
    items: list[dict] = []
    topic = report.get("topic", "unknown")

    # ── Reddit ──────────────────────────────────────────────────────────────
    for r in report.get("reddit", []):
        sub = r.get("subreddit", "misc")
        comments = " | ".join(r.get("comment_insights", []))
        body = r.get("title", "")
        if comments:
            body = f"{body}\n\n{comments}"
        items.append(
            {
                "id": _uid(f"reddit_{sub}", r.get("url", r.get("id", ""))),
                "source": f"last30days/reddit/{sub}",
                "title": r.get("title", ""),
                "content": body,
                "url": r.get("url", ""),
                "published_at": r.get("date"),
                "author": r.get("subreddit"),
                "metadata": {
                    "topic": topic,
                    "score": r.get("score"),
                    "via": "last30days",
                    "engagement": r.get("engagement"),
                },
            },
        )

    # ── X / Twitter ─────────────────────────────────────────────────────────
    for x in report.get("x", []):
        handle = x.get("author_handle", "unknown")
        items.append(
            {
                "id": _uid(f"x_{handle}", x.get("url", x.get("id", ""))),
                "source": f"last30days/x/{handle}",
                "title": x.get("text", "")[:120],
                "content": x.get("text", ""),
                "url": x.get("url", ""),
                "published_at": x.get("date"),
                "author": handle,
                "metadata": {
                    "topic": topic,
                    "score": x.get("score"),
                    "via": "last30days",
                    "engagement": x.get("engagement"),
                },
            },
        )

    # ── Hacker News ──────────────────────────────────────────────────────────
    for h in report.get("hackernews", []):
        comments = " | ".join(h.get("comment_insights", []))
        body = h.get("title", "")
        if comments:
            body = f"{body}\n\n{comments}"
        items.append(
            {
                "id": _uid("hn", h.get("url", h.get("hn_url", h.get("id", "")))),
                "source": "last30days/hn",
                "title": h.get("title", ""),
                "content": body,
                "url": h.get("url") or h.get("hn_url", ""),
                "published_at": h.get("date"),
                "author": h.get("author"),
                "metadata": {
                    "topic": topic,
                    "score": h.get("score"),
                    "hn_url": h.get("hn_url"),
                    "via": "last30days",
                    "engagement": h.get("engagement"),
                },
            },
        )

    # ── YouTube ──────────────────────────────────────────────────────────────
    for y in report.get("youtube", []):
        channel = y.get("channel_name", "unknown").replace(" ", "_")
        highlights = " | ".join(y.get("transcript_highlights", []))
        body = y.get("transcript_snippet", "") or y.get("title", "")
        if highlights:
            body = f"{body}\n\n{highlights}"
        items.append(
            {
                "id": _uid(f"yt_{channel}", y.get("url", y.get("id", ""))),
                "source": f"last30days/youtube/{channel}",
                "title": y.get("title", ""),
                "content": body,
                "url": y.get("url", ""),
                "published_at": y.get("date"),
                "author": y.get("channel_name"),
                "metadata": {
                    "topic": topic,
                    "score": y.get("score"),
                    "via": "last30days",
                    "engagement": y.get("engagement"),
                },
            },
        )

    # ── TikTok ───────────────────────────────────────────────────────────────
    for t in report.get("tiktok", []):
        author = t.get("author_name", "unknown").replace(" ", "_")
        body = t.get("caption_snippet") or t.get("text", "")
        items.append(
            {
                "id": _uid(f"tt_{author}", t.get("url", t.get("id", ""))),
                "source": f"last30days/tiktok/{author}",
                "title": (t.get("text") or "")[:120],
                "content": body,
                "url": t.get("url", ""),
                "published_at": t.get("date"),
                "author": t.get("author_name"),
                "metadata": {
                    "topic": topic,
                    "score": t.get("score"),
                    "hashtags": t.get("hashtags"),
                    "via": "last30days",
                    "engagement": t.get("engagement"),
                },
            },
        )

    # ── Instagram ────────────────────────────────────────────────────────────
    for ig in report.get("instagram", []):
        author = ig.get("author_name", "unknown").replace(" ", "_")
        body = ig.get("caption_snippet") or ig.get("text", "")
        items.append(
            {
                "id": _uid(f"ig_{author}", ig.get("url", ig.get("id", ""))),
                "source": f"last30days/instagram/{author}",
                "title": (ig.get("text") or "")[:120],
                "content": body,
                "url": ig.get("url", ""),
                "published_at": ig.get("date"),
                "author": ig.get("author_name"),
                "metadata": {
                    "topic": topic,
                    "score": ig.get("score"),
                    "hashtags": ig.get("hashtags"),
                    "via": "last30days",
                    "engagement": ig.get("engagement"),
                },
            },
        )

    # ── Bluesky ──────────────────────────────────────────────────────────────
    for b in report.get("bluesky", []):
        handle = b.get("author_handle", "unknown")
        items.append(
            {
                "id": _uid(f"bsky_{handle}", b.get("url", b.get("id", ""))),
                "source": f"last30days/bluesky/{handle}",
                "title": b.get("text", "")[:120],
                "content": b.get("text", ""),
                "url": b.get("url", ""),
                "published_at": b.get("date"),
                "author": b.get("display_name") or b.get("author_handle"),
                "metadata": {
                    "topic": topic,
                    "score": b.get("score"),
                    "via": "last30days",
                    "engagement": b.get("engagement"),
                },
            },
        )

    # ── Truth Social ─────────────────────────────────────────────────────────
    for ts in report.get("truthsocial", []):
        handle = ts.get("author_handle", "unknown")
        items.append(
            {
                "id": _uid(f"ts_{handle}", ts.get("url", ts.get("id", ""))),
                "source": f"last30days/truthsocial/{handle}",
                "title": ts.get("text", "")[:120],
                "content": ts.get("text", ""),
                "url": ts.get("url", ""),
                "published_at": ts.get("date"),
                "author": ts.get("display_name") or handle,
                "metadata": {
                    "topic": topic,
                    "score": ts.get("score"),
                    "via": "last30days",
                    "engagement": ts.get("engagement"),
                },
            },
        )

    # ── Polymarket ───────────────────────────────────────────────────────────
    for pm in report.get("polymarket", []):
        outcomes = ", ".join(f"{n}={p}" for n, p in (pm.get("outcome_prices") or []))
        body = f"{pm.get('question', '')}\nOutcomes: {outcomes}"
        if pm.get("price_movement"):
            body += f"\n{pm['price_movement']}"
        items.append(
            {
                "id": _uid("pm", pm.get("url", pm.get("id", ""))),
                "source": "last30days/polymarket",
                "title": pm.get("title", ""),
                "content": body,
                "url": pm.get("url", ""),
                "published_at": pm.get("date"),
                "author": "polymarket",
                "metadata": {
                    "topic": topic,
                    "score": pm.get("score"),
                    "end_date": pm.get("end_date"),
                    "via": "last30days",
                    "engagement": pm.get("engagement"),
                },
            },
        )

    # ── Web search ───────────────────────────────────────────────────────────
    for w in report.get("web", []):
        domain = w.get("source_domain", "web").replace(".", "_")
        items.append(
            {
                "id": _uid(f"web_{domain}", w.get("url", w.get("id", ""))),
                "source": f"last30days/web/{domain}",
                "title": w.get("title", ""),
                "content": w.get("snippet", ""),
                "url": w.get("url", ""),
                "published_at": w.get("date"),
                "author": w.get("source_domain"),
                "metadata": {"topic": topic, "score": w.get("score"), "via": "last30days"},
            },
        )

    return items


def run_last30days(topic: str, extra_args: list[str]) -> dict:
    """Run last30days.py and return parsed JSON report."""
    if not SKILL_SCRIPT.exists():
        sys.exit(
            f"[ERROR] Skill not found: {SKILL_SCRIPT}\n"
            "Run: git clone https://github.com/mvanhorn/last30days-skill.git /tmp/last30days-skill && "
            "bash /tmp/last30days-skill/scripts/sync.sh",
        )

    cmd = [sys.executable, str(SKILL_SCRIPT), topic, "--emit=json", *extra_args]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=360)
    if result.returncode != 0:
        sys.exit(f"[ERROR] last30days.py exited {result.returncode}")

    # Extract JSON: the emit=json mode prints a single JSON object to stdout
    stdout = result.stdout.strip()
    # Find the outermost JSON object (may have leading log lines)
    brace = stdout.find("{")
    if brace == -1:
        sys.exit("[ERROR] No JSON found in last30days output")
    return json.loads(stdout[brace:])


def save_to_ingest_store(items: list[dict], dry_run: bool) -> tuple[int, int]:
    """Upsert items into IngestStore. Returns (new, skipped)."""
    from ingestion.classification.tier_classifier import IngestedItem
    from ingestion.storage.sqlite_store import IngestStore

    store = IngestStore(WEB_DB)
    new_count = 0
    skip_count = 0

    for raw in items:
        item = IngestedItem(
            id=raw["id"],
            source=raw["source"],
            title=raw.get("title") or "",
            content=raw.get("content") or "",
            url=raw.get("url") or "",
            published_at=_parse_dt(raw.get("published_at")),
            author=raw.get("author"),
            metadata=raw.get("metadata") or {},
        )
        if dry_run:
            new_count += 1
        else:
            saved = store.save_item(item, tier=3)
            if saved:
                new_count += 1
            else:
                skip_count += 1

    return new_count, skip_count


def main() -> None:
    parser = argparse.ArgumentParser(description="Pipe last30days research into IngestStore")
    parser.add_argument("topic", help="Research topic")
    parser.add_argument("--quick", action="store_true", help="Faster run (fewer results)")
    parser.add_argument("--deep", action="store_true", help="Comprehensive run")
    parser.add_argument("--search", help="Comma-separated sources (reddit,hn,x,web,...)")
    parser.add_argument("--mock", action="store_true", help="Use fixtures (no API calls)")
    parser.add_argument("--dry-run", action="store_true", help="Print items without saving")
    args = parser.parse_args()

    extra: list[str] = []
    if args.quick:
        extra.append("--quick")
    if args.deep:
        extra.append("--deep")
    if args.search:
        extra.append(f"--search={args.search}")
    if args.mock:
        extra.append("--mock")

    report = run_last30days(args.topic, extra)

    items = report_to_items(report)
    total = len(items)

    if total == 0:
        return

    _new, _skipped = save_to_ingest_store(items, dry_run=args.dry_run)
    if not args.dry_run:
        pass


if __name__ == "__main__":
    main()
