#!/usr/bin/env python3
"""Surgical pruner for geminiCodeAssist.chatThreads in Antigravity/VS Code state DB.

Removes only the chat-thread history payload from the global state database,
preserving all other Gemini Code Assist settings (auth, projects, survey state, etc.).

Usage:
    # Dry run (default) — shows what would change
    python3 scripts/prune_gca_chat_threads.py --dry-run

    # Actually prune (creates timestamped backup first)
    python3 scripts/prune_gca_chat_threads.py --write

    # Custom file target
    python3 scripts/prune_gca_chat_threads.py --file ~/path/to/state.vscdb --write

    # Keep the N newest threads
    python3 scripts/prune_gca_chat_threads.py --write --keep 3

IMPORTANT: Close the IDE completely before running with --write.
The SQLite DB is locked while the IDE is open.
"""

import argparse
import json
import os
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path


# ── Constants ──────────────────────────────────────────────────────────────────
STATE_KEY = "google.geminicodeassist"
THREADS_FIELD = "geminiCodeAssist.chatThreads"

DEFAULT_PATHS = [
    "~/Library/Application Support/Antigravity/User/globalStorage/state.vscdb",
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


def main():
    parser = argparse.ArgumentParser(
        description="Prune geminiCodeAssist.chatThreads from IDE state DB"
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--dry-run", action="store_true", help="Inspect only, no changes"
    )
    mode.add_argument(
        "--write", action="store_true", help="Actually prune (creates backup first)"
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
    args = parser.parse_args()

    db_path = locate_db(args.file)
    if not db_path:
        print("ERROR: Could not locate state.vscdb")
        print("Searched:", DEFAULT_PATHS)
        sys.exit(1)

    print(f"State DB: {db_path}")
    print(f"File size: {db_path.stat().st_size:,} bytes")
    print()

    # ── Inspect ────────────────────────────────────────────────────────────
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

    # ── Write ──────────────────────────────────────────────────────────────
    print("──── WRITE MODE ────")
    backup = backup_db(db_path, args.backup_dir)
    print(f"Backup created: {backup}")

    try:
        result = prune(db_path, keep=args.keep)
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e).lower():
            print()
            print("⚠️  DATABASE IS LOCKED by the running IDE.")
            print("   Close Antigravity completely, then re-run this script")
            print("   from a standalone Terminal:")
            print()
            print(
                "   python3 scripts/prune_gca_chat_threads.py --write"
            )
            sys.exit(1)
        raise

    if not result["success"]:
        print(f"FAILED: {result['reason']}")
        sys.exit(1)

    print()
    print(f"Before:  {result['before_bytes']:>12,} bytes")
    print(f"After:   {result['after_bytes']:>12,} bytes")
    print(f"Freed:   {result['freed_bytes']:>12,} bytes")
    print(
        f"Threads: {result['threads_before_bytes']:>12,} → "
        f"{result['threads_after_bytes']:,} bytes"
    )
    print()
    print("✅ Successfully pruned geminiCodeAssist.chatThreads")
    print("   Reopen the IDE to verify GCA still loads and auth is intact.")


if __name__ == "__main__":
    main()
