#!/usr/bin/env python3
# Copyright 2026 ShadowTag AI. All rights reserved.
"""Pathway Ingest — File watcher for vault/ingest/ directory.

Watches the ingest directory for new files and routes them through
the zero-trust pipeline. Uses watchdog for filesystem events with
a polling fallback for robustness.

Usage:
    python scripts/vault/pathway_ingest.py                # foreground
    python scripts/vault/pathway_ingest.py --once          # single scan
    python scripts/vault/pathway_ingest.py --poll-interval 10  # custom interval
"""

from __future__ import annotations

import argparse
import logging
import signal
import sys
import time
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [VAULT-INGEST] %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("vault.ingest")

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
INGEST_DIR = REPO_ROOT / "vault" / "ingest"

_running = True


def _signal_handler(sig: int, _frame: object) -> None:
    global _running
    logger.info("Received signal %d, stopping ingest watcher...", sig)
    _running = False


signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)


def process_new_files() -> int:
    """Scan ingest dir and route files through zero-trust pipeline.

    Returns the number of files processed.
    """
    # Import here to avoid circular deps and allow standalone testing
    # Import from sibling module using path resolution
    import importlib.util
    ztp_path = Path(__file__).resolve().parent / "zero_trust_pipeline.py"
    spec = importlib.util.spec_from_file_location("zero_trust_pipeline", ztp_path)
    ztp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ztp)
    scan_directory = ztp.scan_directory

    if not INGEST_DIR.exists():
        INGEST_DIR.mkdir(parents=True, exist_ok=True)
        return 0

    files = [f for f in INGEST_DIR.iterdir() if f.is_file() and f.name != ".gitkeep"]
    if not files:
        return 0

    logger.info("Found %d file(s) in ingest/", len(files))
    results = scan_directory(INGEST_DIR)

    # Remove processed files from ingest (they've been moved to serve/ or quarantine/)
    processed = 0
    for r in results:
        if r["status"] in ("clean", "quarantined"):
            src = Path(r["file"])
            if src.exists():
                src.unlink()
                processed += 1
                logger.info("Removed processed file: %s", src.name)
        elif r["status"] == "rejected":
            # Move rejected files to quarantine with _REJECTED suffix
            src = Path(r["file"])
            if src.exists():
                reject_dir = REPO_ROOT / "vault" / "quarantine"
                reject_dir.mkdir(parents=True, exist_ok=True)
                dest = reject_dir / f"REJECTED_{src.name}"
                src.rename(dest)
                processed += 1
                logger.warning("Moved rejected file: %s → quarantine/", src.name)

    return processed


def try_watchdog_watcher(poll_interval: float) -> bool:
    """Attempt to use watchdog for filesystem events. Returns False if unavailable."""
    try:
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
    except ImportError:
        logger.info("watchdog not installed, falling back to polling")
        return False

    class IngestHandler(FileSystemEventHandler):
        def on_created(self, event):  # noqa: ANN001, ANN201
            if not event.is_directory:
                logger.info("New file detected: %s", event.src_path)
                process_new_files()

    observer = Observer()
    INGEST_DIR.mkdir(parents=True, exist_ok=True)
    observer.schedule(IngestHandler(), str(INGEST_DIR), recursive=False)
    observer.start()
    logger.info("Watchdog observer started on %s", INGEST_DIR)

    try:
        while _running:
            time.sleep(poll_interval)
    finally:
        observer.stop()
        observer.join()

    return True


def polling_loop(interval: float) -> None:
    """Simple polling fallback when watchdog is not available."""
    logger.info("Polling %s every %.0fs", INGEST_DIR, interval)
    while _running:
        process_new_files()
        for _ in range(int(interval)):
            if not _running:
                break
            time.sleep(1)


def main() -> int:
    parser = argparse.ArgumentParser(description="Vault Ingest Watcher")
    parser.add_argument("--once", action="store_true", help="Single scan then exit")
    parser.add_argument("--poll-interval", type=float, default=30.0, help="Seconds between polls")
    parser.add_argument("--no-watchdog", action="store_true", help="Force polling mode")
    args = parser.parse_args()

    INGEST_DIR.mkdir(parents=True, exist_ok=True)

    if args.once:
        count = process_new_files()
        logger.info("Single scan: %d file(s) processed", count)
        return 0

    if not args.no_watchdog and try_watchdog_watcher(args.poll_interval):
        return 0

    polling_loop(args.poll_interval)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
