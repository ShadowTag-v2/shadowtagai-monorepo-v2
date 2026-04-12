#!/usr/bin/env python3
"""
scripts/ingest_monitor.py — Continuous Web Ingest → Corpus → Swarm Monitor
---------------------------------------------------------------------------
Ties together all three pipeline stages in a loop:

  1. Web adapters → IngestStore  (Reddit, 4chan, news RSS, darkweb, …)
  2. web_to_corpus.py            (normalize items → extractions + FTS5)
  3. gemini_agent_swarm.py       (4-phase RAG → Judge 6 gate)
  → data/monitor/YYYY-MM-DD.json

Usage:
    python3 scripts/ingest_monitor.py                  # loop every 60 min
    python3 scripts/ingest_monitor.py --once           # single pass
    python3 scripts/ingest_monitor.py --interval 1800  # loop every 30 min
    python3 scripts/ingest_monitor.py --verified-only  # cite only VERIFIED sources
    python3 scripts/ingest_monitor.py --sources reddit,news  # limit adapters
"""

from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services"))

MONITOR_DIR = REPO_ROOT / "data/monitor"
WEB_DB = REPO_ROOT / "data/web_ingest/ingest.db"

DEFAULT_INTERVAL = 3600  # 1 hour


# ── Stage 1: Run Web Adapters ─────────────────────────────────────────────────


async def _run_adapter(name: str, adapter_fn) -> int:
    """Run one async adapter, persist results to IngestStore. Returns item count."""
    try:
        from ingestion.storage.sqlite_store import IngestStore

        store = IngestStore(str(WEB_DB))
        adapter = adapter_fn()
        count = 0
        async for item in adapter.fetch_items():
            if store.save_item(item):
                count += 1
        print(f"  [{name}] +{count} new items")
        return count
    except Exception as exc:
        print(f"  [{name}] FAILED: {exc}", file=sys.stderr)
        return 0


async def run_web_adapters(sources: list[str]) -> dict[str, int]:
    """Run the specified free adapters concurrently."""
    from ingestion.sources.fourchan_adapter import FourChanAdapter
    from ingestion.sources.reddit_adapter import RedditAdapter

    ADAPTERS: dict[str, object] = {
        "reddit": lambda: RedditAdapter(limit=25),
        "4chan": lambda: FourChanAdapter(),
    }

    # Optional adapters — only import if available
    try:
        from ingestion.sources.news_adapter import NewsRSSAdapter

        ADAPTERS["news"] = lambda: NewsRSSAdapter()
    except ImportError:
        pass

    try:
        from ingestion.sources.darkweb_adapter import DarkWebAdapter

        ADAPTERS["darkweb"] = lambda: DarkWebAdapter()
    except ImportError:
        pass

    active = {k: v for k, v in ADAPTERS.items() if not sources or k in sources}
    if not active:
        print(f"  [adapters] No matching adapters for: {sources}")
        return {}

    tasks = [_run_adapter(name, fn) for name, fn in active.items()]
    counts_list = await asyncio.gather(*tasks)
    return dict(zip(active.keys(), counts_list))


# ── Stage 2: Normalize to Corpus ─────────────────────────────────────────────


def run_web_to_corpus() -> dict[str, int]:
    """Run the web_to_corpus normalizer inline."""
    try:
        from scripts.web_to_corpus import normalize

        return normalize(dry_run=False)
    except ImportError:
        # Fall back to subprocess if import path differs
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts/web_to_corpus.py"), "--once"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        if result.returncode != 0:
            print(f"  [web_to_corpus] stderr: {result.stderr}", file=sys.stderr)
        return {"processed": -1, "skipped": 0, "errors": 0}


# ── Stage 3: Agent Swarm ──────────────────────────────────────────────────────


def run_swarm(verified_only: bool = False) -> dict:
    """Run gemini_agent_swarm.py as subprocess, capture JSON output."""
    swarm_script = REPO_ROOT / "scripts/gemini_agent_swarm.py"
    if not swarm_script.exists():
        print("  [swarm] gemini_agent_swarm.py not found — skipping", file=sys.stderr)
        return {"skipped": True}

    cmd = [sys.executable, str(swarm_script), "--output-json"]
    if verified_only:
        cmd.append("--verified-only")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=600,
        )
        if result.returncode != 0:
            print(f"  [swarm] exit {result.returncode}: {result.stderr[:200]}", file=sys.stderr)
            return {"error": result.stderr[:500]}
        # Attempt to parse last JSON blob from stdout
        for line in reversed(result.stdout.splitlines()):
            line = line.strip()
            if line.startswith("{"):
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    pass
        return {"stdout": result.stdout[-500:]}
    except subprocess.TimeoutExpired:
        return {"error": "swarm timed out after 600s"}
    except Exception as exc:
        return {"error": str(exc)}


# ── Single Pass ───────────────────────────────────────────────────────────────


def run_once(sources: list[str], verified_only: bool) -> dict:
    ts = datetime.now(UTC).isoformat()
    print(f"\n[monitor] Pass starting at {ts}")

    # Stage 1
    print("[monitor] Stage 1: web adapters …")
    ingest_counts = asyncio.run(run_web_adapters(sources))

    # Stage 2
    print("[monitor] Stage 2: web_to_corpus …")
    corpus_stats = run_web_to_corpus()
    print(
        f"  processed={corpus_stats.get('processed')} skipped={corpus_stats.get('skipped')} errors={corpus_stats.get('errors')}"
    )

    # Stage 3
    print("[monitor] Stage 3: gemini agent swarm …")
    swarm_result = run_swarm(verified_only=verified_only)
    judge6 = swarm_result.get("architect_directive", {}).get("judge6_gate", "unknown")
    print(f"  judge6_gate={judge6}")

    output = {
        "ts": ts,
        "ingest": ingest_counts,
        "corpus": corpus_stats,
        "swarm": swarm_result,
    }

    # Write output
    MONITOR_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now(UTC).strftime("%Y-%m-%d")
    out_file = MONITOR_DIR / f"{date_str}.json"
    existing: list[dict] = []
    if out_file.exists():
        try:
            existing = json.loads(out_file.read_text())
            if not isinstance(existing, list):
                existing = [existing]
        except Exception:
            existing = []
    existing.append(output)
    out_file.write_text(json.dumps(existing, indent=2))
    print(f"[monitor] Written → {out_file}")

    return output


# ── Loop ──────────────────────────────────────────────────────────────────────


def run_loop(interval: int, sources: list[str], verified_only: bool) -> None:
    print(
        f"[monitor] Loop mode: interval={interval}s sources={sources or 'all'} verified_only={verified_only}"
    )
    while True:
        run_once(sources, verified_only)
        print(f"[monitor] Sleeping {interval}s …")
        time.sleep(interval)


# ── CLI ───────────────────────────────────────────────────────────────────────


def main() -> None:
    ap = argparse.ArgumentParser(description="Continuous web ingest → corpus → swarm monitor")
    ap.add_argument("--once", action="store_true", help="Single pass, no loop")
    ap.add_argument(
        "--interval",
        type=int,
        default=DEFAULT_INTERVAL,
        metavar="SECONDS",
        help="Loop cadence (default 3600)",
    )
    ap.add_argument(
        "--verified-only", action="store_true", help="Pass --verified-only to rag_evolve / swarm"
    )
    ap.add_argument(
        "--sources",
        default="",
        metavar="NAMES",
        help="Comma-separated adapters to run (default: all)",
    )
    args = ap.parse_args()

    sources = [s.strip() for s in args.sources.split(",") if s.strip()]

    if args.once:
        run_once(sources, args.verified_only)
    else:
        run_loop(args.interval, sources, args.verified_only)


if __name__ == "__main__":
    main()
