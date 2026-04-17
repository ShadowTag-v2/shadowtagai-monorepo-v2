#!/usr/bin/env python3
"""Surgical pruner for Gemini Code Assist (GCA) chat thread bloat.

The GCA extension stores entire conversation history + error stack traces
as JSON keys in the VS Code global state SQLite database (state.vscdb).
This can balloon to 25-60+ MB, causing:
  - Extension host unresponsiveness / crashes
  - Live Server silently failing (host too swamped)
  - General IDE sluggishness

This script:
  --write    Prunes chatThreads and VACUUMs the DB (IDE MUST be closed)
  --monitor  Background watcher that yells if DB > 20MB

Usage:
  # Preview (dry-run):
  python3 scripts/prune_gca_chat_threads.py

  # Prune (IDE must be closed first - Cmd+Q):
  python3 scripts/prune_gca_chat_threads.py --write

  # Background monitor:
  python3 scripts/prune_gca_chat_threads.py --monitor
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

BLOAT_THRESHOLD_MB = 20.0

PATHS = [
    "~/Library/Application Support/Antigravity/User/globalStorage/state.vscdb",
    "~/.antigravity/data/User/globalStorage/state.vscdb",
    "~/Library/Application Support/Code/User/globalStorage/state.vscdb",
]


def get_db_path() -> str | None:
    for p in PATHS:
        full_path = os.path.expanduser(p)
        if os.path.exists(full_path):
            return full_path
    return None


def trigger_mac_notification(size_mb: float) -> None:
    """Fires a macOS notification and text-to-speech sound."""
    title = "🚨 IDE Bloat Alert"
    message = (
        f"state.vscdb has ballooned to {size_mb:.1f} MB! "
        "Cmd+Q your IDE and run the prune script."
    )
    print(f"\n🔊 Triggering alert! DB is {size_mb:.1f} MB.")

    subprocess.run(
        [
            "osascript",
            "-e",
            f'display notification "{message}" with title "{title}" sound name "Basso"',
        ]
    )
    subprocess.run(
        [
            "say",
            "Warning. IDE database is bloated. Please close the editor and vacuum.",
        ]
    )


def monitor_mode() -> None:
    """Runs a noisy background monitor to check DB size."""
    db_path = get_db_path()
    if not db_path:
        print("❌ Error: Could not locate state.vscdb.")
        sys.exit(1)

    print(
        f"👁️  Monitoring DB size every 10 minutes. Threshold: {BLOAT_THRESHOLD_MB}MB"
    )

    while True:
        size_mb = os.path.getsize(db_path) / (1024 * 1024)
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"  [{ts}] state.vscdb = {size_mb:.1f} MB", end="")

        if size_mb > BLOAT_THRESHOLD_MB:
            print(" ⚠️  OVER THRESHOLD")
            trigger_mac_notification(size_mb)
            time.sleep(3600)  # Sleep 1 hour after warning to prevent spam
        else:
            print(" ✅")
            time.sleep(600)


def inspect_db(db_path: str) -> dict:
    """Read-only inspection of the GCA state. Returns metrics dict."""
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    cursor = conn.cursor()

    key = "google.geminicodeassist"
    cursor.execute("SELECT value FROM ItemTable WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"found": False}

    state_dict = json.loads(row[0])
    gca_total_bytes = len(row[0].encode("utf-8"))

    chat_threads = state_dict.get("geminiCodeAssist.chatThreads", [])
    chat_payload_bytes = len(json.dumps(chat_threads).encode("utf-8"))
    thread_count = len(chat_threads)

    preserved_keys = [
        k for k in state_dict.keys() if k != "geminiCodeAssist.chatThreads"
    ]

    return {
        "found": True,
        "gca_total_bytes": gca_total_bytes,
        "chat_payload_bytes": chat_payload_bytes,
        "thread_count": thread_count,
        "preserved_key_count": len(preserved_keys),
        "preserved_keys": preserved_keys,
    }


def prune_and_vacuum() -> None:
    """Surgically prunes the Gemini chat threads and reclaims SQLite dead space."""
    db_path = get_db_path()
    if not db_path:
        print("❌ Error: Could not locate state.vscdb.")
        sys.exit(1)

    initial_db_size = os.path.getsize(db_path)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        key = "google.geminicodeassist"
        cursor.execute("SELECT value FROM ItemTable WHERE key = ?", (key,))
        row = cursor.fetchone()

        print(f"State DB: {db_path}")
        print(f"File size: {initial_db_size:,} bytes")

        if row:
            state_dict = json.loads(row[0])
            gca_total_bytes = len(row[0].encode("utf-8"))

            chat_payload_bytes = len(
                json.dumps(
                    state_dict.get("geminiCodeAssist.chatThreads", [])
                ).encode("utf-8")
            )
            thread_count = len(
                state_dict.get("geminiCodeAssist.chatThreads", [])
            )

            print(f"GCA state total:          {gca_total_bytes:,} bytes")
            print(f"chatThreads payload:      {chat_payload_bytes:,} bytes")
            print(f"Thread count:                      {thread_count}")

            if "geminiCodeAssist.chatThreads" in state_dict:
                preserved_keys = [
                    k
                    for k in state_dict.keys()
                    if k != "geminiCodeAssist.chatThreads"
                ]
                print(f"Other preserved keys:             {len(preserved_keys)}")
                print(f"Preserved keys: {preserved_keys}")

                print("\n──── WRITE MODE ────")
                backup_path = (
                    f"{db_path}.backup."
                    f"{datetime.now().strftime('%Y%m%dT%H%M%S')}"
                )
                shutil.copy2(db_path, backup_path)
                print(f"Backup created: {backup_path}")
                print(f"Before:    {gca_total_bytes:,} bytes")

                # Prune the bloated chat history
                state_dict["geminiCodeAssist.chatThreads"] = []
                new_value = json.dumps(state_dict)
                after_bytes = len(new_value.encode("utf-8"))
                freed_bytes = gca_total_bytes - after_bytes

                cursor.execute(
                    "UPDATE ItemTable SET value = ? WHERE key = ?",
                    (new_value, key),
                )
                conn.commit()

                print(f"After:          {after_bytes:,} bytes")
                print(f"Freed:     {freed_bytes:,} bytes")
                print(f"Threads:   {chat_payload_bytes:,} → 2 bytes")
                print("✅ Successfully pruned geminiCodeAssist.chatThreads")
                print(
                    "   Reopen the IDE to verify GCA still loads and auth is intact."
                )

        # Run VACUUM to physically shrink the .vscdb file
        print("\nRunning VACUUM...")
        conn.execute("VACUUM")
        conn.commit()

        final_size = os.path.getsize(db_path)
        recovered = initial_db_size - final_size
        pct = (recovered / initial_db_size * 100) if initial_db_size > 0 else 0
        print(
            f"VACUUM recovered {pct:.1f}% — "
            f"from {initial_db_size / 1024 / 1024:.1f} MB "
            f"down to {final_size / 1024 / 1024:.1f} MB"
        )

        conn.close()

    except sqlite3.OperationalError as e:
        if "database is locked" in str(e).lower():
            print("\n⚠️ ERROR: Database is locked by the active IDE instance.")
            print(
                "🚨 USER ACTION REQUIRED: Cmd+Q to completely quit Antigravity, "
                "then run this script again."
            )
        else:
            print(f"SQLite Error: {e}")


def dry_run() -> None:
    """Read-only inspection and report."""
    db_path = get_db_path()
    if not db_path:
        print("❌ Error: Could not locate state.vscdb.")
        sys.exit(1)

    initial_db_size = os.path.getsize(db_path)
    print(f"State DB: {db_path}")
    print(f"File size: {initial_db_size:,} bytes ({initial_db_size / 1024 / 1024:.1f} MB)")

    metrics = inspect_db(db_path)
    if not metrics["found"]:
        print("google.geminicodeassist key not found in state DB.")
        return

    print(f"GCA state total:          {metrics['gca_total_bytes']:,} bytes")
    print(f"chatThreads payload:      {metrics['chat_payload_bytes']:,} bytes")
    print(f"Thread count:                      {metrics['thread_count']}")
    print(f"Other preserved keys:             {metrics['preserved_key_count']}")
    print(f"Preserved keys: {metrics['preserved_keys'][:5]}...")

    would_free = metrics["chat_payload_bytes"]
    print(f"\n──── DRY RUN (no changes made) ────")
    print(f"Would free:    ~{would_free:,} bytes ({would_free / 1024 / 1024:.1f} MB)")
    print(f"Run with --write to prune (IDE must be closed first).")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        try:
            monitor_mode()
        except KeyboardInterrupt:
            print("\nExiting monitor.")
    elif len(sys.argv) > 1 and sys.argv[1] == "--write":
        prune_and_vacuum()
    else:
        dry_run()
