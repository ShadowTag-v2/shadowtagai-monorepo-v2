#!/usr/bin/env python3
"""Dual-mode surgical pruner for geminiCodeAssist.chatThreads in IDE state DB.

Removes only the chat-thread history payload from the global state database,
preserving all other Gemini Code Assist settings (auth, projects, survey state, etc.).

Two modes:
    1. MONITOR — Runs in the background and yells at you (Mac notifications + speech)
       if the state DB crosses a size threshold.

       python3 scripts/prune_gca_chat_threads.py --monitor

    2. WRITE — Safely performs backup, surgical JSON prune, and SQLite VACUUM.
       IDE MUST BE CLOSED.

       python3 scripts/prune_gca_chat_threads.py --write

Other usage:
    # Dry run (default) — shows what would change
    python3 scripts/prune_gca_chat_threads.py --dry-run

    # Custom file target
    python3 scripts/prune_gca_chat_threads.py --file ~/path/to/state.vscdb --write

    # Keep the N newest threads
    python3 scripts/prune_gca_chat_threads.py --write --keep 3

IMPORTANT: Close the IDE completely before running with --write.
The SQLite DB is locked while the IDE is open.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


# ── Constants ──────────────────────────────────────────────────────────────────
STATE_KEY = "google.geminicodeassist"
THREADS_FIELD = "geminiCodeAssist.chatThreads"
BLOAT_THRESHOLD_MB = 20.0
MONITOR_INTERVAL_SECONDS = 600  # 10 minutes
MONITOR_COOLDOWN_SECONDS = 3600  # 1 hour after alert

DEFAULT_PATHS = [
    "~/Library/Application Support/Antigravity/User/globalStorage/state.vscdb",
    "~/.antigravity/data/User/globalStorage/state.vscdb",
    "~/Library/Application Support/Code/User/globalStorage/state.vscdb",
    "~/.config/Antigravity/User/globalStorage/state.vscdb",
    "~/.config/Code/User/globalStorage/state.vscdb",
]


def locate_db(explicit_path: str | None = None) -> Path | None:
    """Find the state database. Explicit path wins; otherwise probe defaults."""
    if explicit_path:
        p = Path(explicit_path).expanduser()
        return p if p.exists() else None
    for candidate in DEFAULT_PATHS:
        p = Path(candidate).expanduser()
        if p.exists():
            return p
    return None


def backup_db(db_path: Path, backup_dir: str | None = None) -> Path:
    """Create a timestamped backup of the state DB."""
    ts = datetime.now().strftime("%Y%m%dT%H%M%S")
    dest_dir = Path(backup_dir).expanduser() if backup_dir else db_path.parent
    dest_dir.mkdir(parents=True, exist_ok=True)
    backup = dest_dir / f"state.vscdb.backup.{ts}"
    shutil.copy2(db_path, backup)
    return backup


def inspect(db_path: Path) -> dict:
    """Read the GCA state and return metrics without modifying anything."""
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    cursor = conn.cursor()

    cursor.execute("SELECT value FROM ItemTable WHERE key = ?", (STATE_KEY,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"found": False}

    raw = row[0]
    total_bytes = len(raw.encode("utf-8")) if isinstance(raw, str) else len(raw)

    try:
        state_dict = json.loads(raw)
    except json.JSONDecodeError:
        return {"found": True, "total_bytes": total_bytes, "valid_json": False}

    threads_raw = json.dumps(state_dict.get(THREADS_FIELD, []))
    threads_bytes = len(threads_raw.encode("utf-8"))

    # Count threads
    threads = state_dict.get(THREADS_FIELD, [])
    if isinstance(threads, list):
        thread_count = len(threads)
    elif isinstance(threads, dict):
        thread_count = len(threads)
    else:
        thread_count = 0

    other_keys = [k for k in state_dict if k != THREADS_FIELD]

    return {
        "found": True,
        "valid_json": True,
        "total_bytes": total_bytes,
        "threads_bytes": threads_bytes,
        "thread_count": thread_count,
        "other_keys": other_keys,
        "other_keys_count": len(other_keys),
    }


def prune(db_path: Path, keep: int = 0) -> dict:
    """Remove chat threads from the state, keeping `keep` newest if requested."""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("SELECT value FROM ItemTable WHERE key = ?", (STATE_KEY,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return {"success": False, "reason": "key not found"}

    raw = row[0]
    before_bytes = len(raw.encode("utf-8")) if isinstance(raw, str) else len(raw)

    try:
        state_dict = json.loads(raw)
    except json.JSONDecodeError:
        conn.close()
        return {"success": False, "reason": "invalid JSON — refusing to touch"}

    if THREADS_FIELD not in state_dict:
        conn.close()
        return {"success": False, "reason": "chatThreads field not found"}

    threads = state_dict[THREADS_FIELD]
    threads_before = json.dumps(threads)
    threads_before_bytes = len(threads_before.encode("utf-8"))

    # Prune
    if keep > 0 and isinstance(threads, list) and len(threads) > keep:
        state_dict[THREADS_FIELD] = threads[-keep:]  # keep newest
    elif keep > 0 and isinstance(threads, dict):
        # dict-based threads: keep the last N entries
        keys = list(threads.keys())[-keep:]
        state_dict[THREADS_FIELD] = {k: threads[k] for k in keys}
    else:
        # Full prune
        if isinstance(threads, list):
            state_dict[THREADS_FIELD] = []
        elif isinstance(threads, dict):
            state_dict[THREADS_FIELD] = {}
        else:
            state_dict[THREADS_FIELD] = []

    new_value = json.dumps(state_dict)
    after_bytes = len(new_value.encode("utf-8"))
    threads_after_bytes = len(
        json.dumps(state_dict[THREADS_FIELD]).encode("utf-8")
    )

    cursor.execute(
        "UPDATE ItemTable SET value = ? WHERE key = ?", (new_value, STATE_KEY)
    )
    conn.commit()
    conn.close()

    return {
        "success": True,
        "before_bytes": before_bytes,
        "after_bytes": after_bytes,
        "threads_before_bytes": threads_before_bytes,
        "threads_after_bytes": threads_after_bytes,
        "freed_bytes": before_bytes - after_bytes,
    }


def vacuum_db(db_path: Path) -> dict:
    """Run VACUUM on the SQLite database to reclaim dead space."""
    before_size = db_path.stat().st_size
    try:
        conn = sqlite3.connect(str(db_path))
        conn.execute("VACUUM")
        conn.close()
        after_size = db_path.stat().st_size
        return {
            "success": True,
            "before_size": before_size,
            "after_size": after_size,
            "reclaimed": before_size - after_size,
        }
    except sqlite3.OperationalError as e:
        return {"success": False, "reason": str(e)}


# ── Monitor Mode ──────────────────────────────────────────────────────────────
def trigger_mac_notification(size_mb: float) -> None:
    """Fires a loud macOS notification and text-to-speech sound."""
    title = "🚨 IDE Bloat Alert"
    message = (
        f"state.vscdb has ballooned to {size_mb:.1f} MB! "
        "Cmd+Q your IDE and run the prune script."
    )
    print(f"\n🔊 Triggering alert! DB is {size_mb:.1f} MB.")

    try:
        subprocess.run(
            [
                "osascript", "-e",
                f'display notification "{message}" with title "{title}" '
                f'sound name "Basso"'
            ],
            check=False, capture_output=True, timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass  # Not on macOS or osascript hung

    try:
        subprocess.run(
            ["say", "Warning. IDE database is bloated. "
             "Please close the editor and vacuum."],
            check=False, capture_output=True, timeout=15,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass  # Not on macOS or say hung


def monitor_mode(db_path: Path, threshold_mb: float = BLOAT_THRESHOLD_MB) -> None:
    """Runs a noisy background monitor to check DB size."""
    print(f"👁️  Monitoring: {db_path}")
    print(f"   Threshold: {threshold_mb} MB")
    print(f"   Check interval: {MONITOR_INTERVAL_SECONDS}s")
    print(f"   Cooldown after alert: {MONITOR_COOLDOWN_SECONDS}s")
    print()

    while True:
        try:
            size_bytes = db_path.stat().st_size
            size_mb = size_bytes / (1024 * 1024)
            ts = datetime.now().strftime("%H:%M:%S")

            if size_mb > threshold_mb:
                print(f"[{ts}] ⚠️  {size_mb:.1f} MB — OVER THRESHOLD!")
                trigger_mac_notification(size_mb)
                time.sleep(MONITOR_COOLDOWN_SECONDS)
            else:
                print(f"[{ts}] ✅ {size_mb:.1f} MB — OK")
                time.sleep(MONITOR_INTERVAL_SECONDS)
        except FileNotFoundError:
            print(f"[{datetime.now():%H:%M:%S}] ❓ DB not found, retrying...")
            time.sleep(MONITOR_INTERVAL_SECONDS)


# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Prune geminiCodeAssist.chatThreads from IDE state DB"
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--dry-run", action="store_true", help="Inspect only, no changes"
    )
    mode.add_argument(
        "--write", action="store_true",
        help="Prune DB & reclaim space. IDE MUST BE CLOSED!",
    )
    mode.add_argument(
        "--monitor", action="store_true",
        help="Run in background & yell if DB > threshold",
    )
    mode.add_argument(
        "--vacuum-only", action="store_true",
        help="Only run VACUUM to reclaim dead space (no prune). IDE MUST BE CLOSED!",
    )
    parser.add_argument("--file", type=str, help="Explicit path to state.vscdb")
    parser.add_argument(
        "--backup-dir", type=str, help="Directory for backups (default: same as DB)"
    )
    parser.add_argument(
        "--keep",
        type=int,
        default=0,
        help="Keep the N newest threads (default: 0 = remove all)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=BLOAT_THRESHOLD_MB,
        help=f"Bloat threshold in MB for --monitor mode (default: {BLOAT_THRESHOLD_MB})",
    )
    args = parser.parse_args()

    db_path = locate_db(args.file)
    if not db_path:
        print("❌ Error: Could not locate state.vscdb.")
        print("Searched:", DEFAULT_PATHS)
        sys.exit(1)

    # ── Monitor mode ──────────────────────────────────────────────────────
    if args.monitor:
        try:
            monitor_mode(db_path, threshold_mb=args.threshold)
        except KeyboardInterrupt:
            print("\nExiting monitor.")
        return

    # ── Vacuum-only mode ──────────────────────────────────────────────────
    if args.vacuum_only:
        print(f"State DB: {db_path}")
        print(f"File size: {db_path.stat().st_size:,} bytes")
        print()
        print("──── VACUUM ONLY ────")
        vac = vacuum_db(db_path)
        if vac["success"]:
            print(f"   DB file before VACUUM: {vac['before_size']:>12,} bytes")
            print(f"   DB file after VACUUM:  {vac['after_size']:>12,} bytes")
            print(f"   Disk reclaimed:        {vac['reclaimed']:>12,} bytes")
            print("\n✅ VACUUM complete.")
        else:
            print(f"   ⚠️  VACUUM failed: {vac['reason']}")
            if "locked" in vac.get("reason", "").lower():
                print("   Close the IDE and re-run.")
            sys.exit(1)
        return

    # ── Inspect + Write/DryRun ────────────────────────────────────────────
    print(f"State DB: {db_path}")
    print(f"File size: {db_path.stat().st_size:,} bytes")
    print()

    metrics = inspect(db_path)
    if not metrics["found"]:
        print(f"Key '{STATE_KEY}' not found in database. Nothing to do.")
        sys.exit(0)

    if not metrics.get("valid_json", True):
        print("ERROR: State value is not valid JSON. Refusing to modify.")
        sys.exit(1)

    print(f"GCA state total:        {metrics['total_bytes']:>12,} bytes")
    print(f"chatThreads payload:    {metrics['threads_bytes']:>12,} bytes")
    print(f"Thread count:           {metrics['thread_count']:>12}")
    print(f"Other preserved keys:   {metrics['other_keys_count']:>12}")
    print(f"Preserved keys: {metrics['other_keys']}")
    print()

    if args.dry_run:
        print("──── DRY RUN ────")
        savings = metrics["threads_bytes"] - 2  # [] is 2 bytes
        print(f"Would free ~{savings:,} bytes by pruning chatThreads")
        if args.keep > 0:
            print(f"Would keep {args.keep} newest thread(s)")
        print("Run with --write to apply.")
        sys.exit(0)

    # ── Write mode ────────────────────────────────────────────────────────
    print("──── WRITE MODE ────")
    backup = backup_db(db_path, args.backup_dir)
    print(f"Backup created: {backup}")

    try:
        result = prune(db_path, keep=args.keep)
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e).lower():
            print()
            print("⚠️  ERROR: Database is locked by the active IDE instance.")
            print(
                "🚨 USER ACTION REQUIRED: Cmd+Q to completely quit "
                "Antigravity, then run this script again."
            )
            sys.exit(1)
        raise

    if not result["success"]:
        print(f"FAILED: {result['reason']}")
        sys.exit(1)

    print()
    print(f"📉 Before:    {result['before_bytes']:>12,} bytes")
    print(f"🔥 After:     {result['after_bytes']:>12,} bytes")
    print(f"⚡ Freed:     {result['freed_bytes']:>12,} bytes")
    print(
        f"   Threads:   {result['threads_before_bytes']:>12,} → "
        f"{result['threads_after_bytes']:,} bytes"
    )

    # ── VACUUM ────────────────────────────────────────────────────────────
    print()
    print("Running VACUUM to reclaim SQLite dead space...")
    vac = vacuum_db(db_path)
    if vac["success"]:
        print(f"   DB file before VACUUM: {vac['before_size']:>12,} bytes")
        print(f"   DB file after VACUUM:  {vac['after_size']:>12,} bytes")
        print(f"   Disk reclaimed:        {vac['reclaimed']:>12,} bytes")
    else:
        print(f"   ⚠️  VACUUM failed: {vac['reason']}")
        if "locked" in vac.get("reason", "").lower():
            print("   Close the IDE and re-run to VACUUM.")

    print()
    print("✅ Successfully pruned geminiCodeAssist.chatThreads")
    print("   Reopen the IDE to verify GCA still loads and auth is intact.")


if __name__ == "__main__":
    main()
