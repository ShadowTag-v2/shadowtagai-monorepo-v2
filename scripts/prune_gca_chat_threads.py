#!/usr/bin/env python3
"""Surgical pruner for Gemini Code Assist (GCA) chat thread bloat.

The GCA extension stores entire conversation history + error stack traces
as JSON keys in the VS Code global state SQLite database (state.vscdb).
This can balloon to 25-60+ MB, causing:
  - Extension host unresponsiveness / crashes
  - Live Server silently failing (host too swamped)
  - General IDE sluggishness

API Functions (for testing):
  inspect(db_path)           → dict with metrics
  prune(db_path, keep=0)     → dict with success/freed_bytes
  vacuum_db(db_path)         → dict with before/after sizes
  locate_db(explicit=None)   → Path or None

CLI Modes:
  --write         Prune chatThreads and VACUUM (IDE MUST be closed)
  --write --keep N    Keep N newest threads
  --vacuum-only   Just VACUUM without pruning
  --monitor       Background watcher that yells if DB > 20MB

Usage:
  python3 scripts/prune_gca_chat_threads.py              # dry-run
  python3 scripts/prune_gca_chat_threads.py --write       # prune (IDE closed)
  python3 scripts/prune_gca_chat_threads.py --monitor     # background watch
"""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

BLOAT_THRESHOLD_MB = 20.0

STATE_KEY = "google.geminicodeassist"
THREADS_FIELD = "geminiCodeAssist.chatThreads"

SEARCH_PATHS = [
    "~/Library/Application Support/Antigravity/User/globalStorage/state.vscdb",
    "~/.antigravity/data/User/globalStorage/state.vscdb",
    "~/Library/Application Support/Code/User/globalStorage/state.vscdb",
]


def locate_db(explicit: str | None = None) -> Path | None:
    """Find the state database. Returns Path or None."""
    if explicit:
        p = Path(explicit)
        return p if p.exists() else None
    for raw in SEARCH_PATHS:
        p = Path(os.path.expanduser(raw))
        if p.exists():
            return p
    return None


def inspect(db_path: Path | str) -> dict:
    """Read-only inspection of the GCA state. Returns metrics dict."""
    db_path = Path(db_path)
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    cursor = conn.cursor()

    cursor.execute("SELECT value FROM ItemTable WHERE key = ?", (STATE_KEY,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"found": False, "valid_json": False}

    try:
        state_dict = json.loads(row[0])
    except json.JSONDecodeError:
        return {
            "found": True,
            "valid_json": False,
            "raw_bytes": len(row[0].encode("utf-8")),
        }

    gca_total_bytes = len(row[0].encode("utf-8"))
    threads = state_dict.get(THREADS_FIELD, [])
    threads_bytes = len(json.dumps(threads).encode("utf-8"))
    other_keys = [k for k in state_dict.keys() if k != THREADS_FIELD]

    return {
        "found": True,
        "valid_json": True,
        "gca_total_bytes": gca_total_bytes,
        "threads_bytes": threads_bytes,
        "thread_count": len(threads),
        "other_key_count": len(other_keys),
        "other_keys": other_keys,
    }


def prune(db_path: Path | str, keep: int = 0) -> dict:
    """Surgically prune chatThreads. Returns result dict.

    Args:
        db_path: Path to state.vscdb
        keep: Number of newest threads to retain (0 = remove all)
    """
    db_path = Path(db_path)

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        cursor.execute("SELECT value FROM ItemTable WHERE key = ?", (STATE_KEY,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return {"success": False, "reason": "key not found", "freed_bytes": 0}

        try:
            state_dict = json.loads(row[0])
        except json.JSONDecodeError:
            conn.close()
            return {"success": False, "reason": "invalid JSON", "freed_bytes": 0}

        before_bytes = len(row[0].encode("utf-8"))
        threads = state_dict.get(THREADS_FIELD, [])
        threads_before = len(json.dumps(threads).encode("utf-8"))

        # Keep N newest threads (threads are ordered oldest-first)
        if keep > 0 and len(threads) > keep:
            state_dict[THREADS_FIELD] = threads[-keep:]
        else:
            state_dict[THREADS_FIELD] = [] if keep == 0 else threads

        new_value = json.dumps(state_dict)
        after_bytes = len(new_value.encode("utf-8"))
        freed = before_bytes - after_bytes

        cursor.execute(
            "UPDATE ItemTable SET value = ? WHERE key = ?",
            (new_value, STATE_KEY),
        )
        conn.commit()
        conn.close()

        return {
            "success": True,
            "freed_bytes": freed,
            "before_bytes": before_bytes,
            "after_bytes": after_bytes,
            "threads_before": len(threads),
            "threads_after": len(state_dict[THREADS_FIELD]),
        }

    except sqlite3.OperationalError as e:
        return {"success": False, "reason": str(e), "freed_bytes": 0}


def vacuum_db(db_path: Path | str) -> dict:
    """VACUUM the database to reclaim dead space."""
    db_path = Path(db_path)
    before_size = db_path.stat().st_size

    try:
        conn = sqlite3.connect(str(db_path))
        conn.execute("VACUUM")
        conn.commit()
        conn.close()

        after_size = db_path.stat().st_size
        return {
            "success": True,
            "before_size": before_size,
            "after_size": after_size,
            "recovered": before_size - after_size,
        }
    except sqlite3.OperationalError as e:
        return {"success": False, "reason": str(e), "before_size": before_size, "after_size": before_size}


def trigger_mac_notification(size_mb: float) -> None:
    """Fires a macOS notification and text-to-speech sound."""
    title = "🚨 IDE Bloat Alert"
    message = f"state.vscdb has ballooned to {size_mb:.1f} MB! Cmd+Q your IDE and run the prune script."
    print(f"\n🔊 Triggering alert! DB is {size_mb:.1f} MB.")
    subprocess.run(["osascript", "-e", f'display notification "{message}" with title "{title}" sound name "Basso"'])
    subprocess.run(["say", "Warning. IDE database is bloated. Please close the editor and vacuum."])


def monitor_mode(threshold_mb: float = 20.0) -> None:
    """Runs a noisy background monitor to check DB size."""
    db_path = locate_db()
    if not db_path:
        print("❌ Error: Could not locate state.vscdb.")
        sys.exit(1)

    print(f"👁️  Monitoring DB size every 10 minutes. Threshold: {threshold_mb}MB")

    while True:
        size_mb = db_path.stat().st_size / (1024 * 1024)
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"  [{ts}] state.vscdb = {size_mb:.1f} MB", end="")

        if size_mb > threshold_mb:
            print(" ⚠️  OVER THRESHOLD")
            trigger_mac_notification(size_mb)
            time.sleep(3600)
        else:
            print(" ✅")
            time.sleep(600)


def cli_write(keep: int = 0) -> None:
    """CLI entry for --write mode."""
    db_path = locate_db()
    if not db_path:
        print("❌ Error: Could not locate state.vscdb.")
        sys.exit(1)

    initial_size = db_path.stat().st_size

    # Inspect first
    metrics = inspect(db_path)
    print(f"State DB: {db_path}")
    print(f"File size: {initial_size:,} bytes")

    if not metrics["found"]:
        print("google.geminicodeassist key not found.")
        return

    if not metrics["valid_json"]:
        print("❌ GCA state contains invalid JSON. Refusing to modify.")
        return

    print(f"GCA state total:          {metrics['gca_total_bytes']:,} bytes")
    print(f"chatThreads payload:      {metrics['threads_bytes']:,} bytes")
    print(f"Thread count:                      {metrics['thread_count']}")
    print(f"Other preserved keys:             {metrics['other_key_count']}")
    print(f"Preserved keys: {metrics['other_keys']}")

    # Backup
    print("\n──── WRITE MODE ────")
    backup_path = f"{db_path}.backup.{datetime.now().strftime('%Y%m%dT%H%M%S')}"
    shutil.copy2(str(db_path), backup_path)
    print(f"Backup created: {backup_path}")
    print(f"Before:    {metrics['gca_total_bytes']:,} bytes")

    # Prune
    result = prune(db_path, keep=keep)
    if not result["success"]:
        if "database is locked" in result.get("reason", ""):
            print("\n⚠️ ERROR: Database is locked by the active IDE instance.")
            print("🚨 USER ACTION REQUIRED: Cmd+Q to completely quit Antigravity, then run again.")
        else:
            print(f"❌ Prune failed: {result.get('reason', 'unknown')}")
        return

    print(f"After:          {result['after_bytes']:,} bytes")
    print(f"Freed:     {result['freed_bytes']:,} bytes")
    print(f"Threads:   {metrics['threads_bytes']:,} → 2 bytes")
    print("✅ Successfully pruned geminiCodeAssist.chatThreads")
    print("   Reopen the IDE to verify GCA still loads and auth is intact.")

    # VACUUM
    print("\nRunning VACUUM...")
    vac = vacuum_db(db_path)
    if vac["success"]:
        pct = (vac["recovered"] / vac["before_size"] * 100) if vac["before_size"] > 0 else 0
        print(f"VACUUM recovered {pct:.1f}% — from {vac['before_size'] / 1024 / 1024:.1f} MB down to {vac['after_size'] / 1024 / 1024:.1f} MB")


def cli_dry_run() -> None:
    """CLI entry for dry-run mode (default)."""
    db_path = locate_db()
    if not db_path:
        print("❌ Error: Could not locate state.vscdb.")
        sys.exit(1)

    initial_size = db_path.stat().st_size
    print(f"State DB: {db_path}")
    print(f"File size: {initial_size:,} bytes ({initial_size / 1024 / 1024:.1f} MB)")

    metrics = inspect(db_path)
    if not metrics["found"]:
        print("google.geminicodeassist key not found.")
        return

    if not metrics.get("valid_json"):
        print(f"⚠️ GCA state contains invalid JSON ({metrics.get('raw_bytes', 0):,} bytes)")
        return

    print(f"GCA state total:          {metrics['gca_total_bytes']:,} bytes")
    print(f"chatThreads payload:      {metrics['threads_bytes']:,} bytes")
    print(f"Thread count:                      {metrics['thread_count']}")
    print(f"Other preserved keys:             {metrics['other_key_count']}")
    print(f"Preserved keys: {metrics['other_keys'][:5]}...")

    would_free = metrics["threads_bytes"]
    print("\n──── DRY RUN (no changes made) ────")
    print(f"Would free:    ~{would_free:,} bytes ({would_free / 1024 / 1024:.1f} MB)")
    print("Run with --write to prune (IDE must be closed first).")


if __name__ == "__main__":
    args = sys.argv[1:]

    if "--monitor" in args:
        try:
            monitor_mode()
        except KeyboardInterrupt:
            print("\nExiting monitor.")
    elif "--write" in args:
        keep = 0
        if "--keep" in args:
            idx = args.index("--keep")
            if idx + 1 < len(args):
                keep = int(args[idx + 1])
        cli_write(keep=keep)
    elif "--vacuum-only" in args:
        db_path = locate_db()
        if db_path:
            result = vacuum_db(db_path)
            if result["success"]:
                print(f"VACUUM: {result['before_size']:,} → {result['after_size']:,} bytes")
            else:
                print(f"VACUUM failed: {result.get('reason')}")
    else:
        cli_dry_run()
