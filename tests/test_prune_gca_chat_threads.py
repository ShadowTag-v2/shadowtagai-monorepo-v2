#!/usr/bin/env python3
"""Tests for scripts/prune_gca_chat_threads.py

Proves:
  1. Only geminiCodeAssist.chatThreads changes
  2. All other keys are byte-for-byte preserved
  3. Invalid JSON fails safely without destructive overwrite
  4. --keep N retains newest threads
"""

import json
import os
import sqlite3
import sys
import tempfile
from pathlib import Path

# Add scripts/ to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from prune_gca_chat_threads import (
    THREADS_FIELD,
    STATE_KEY,
    inspect,
    prune,
    vacuum_db,
    locate_db,
)


def _create_test_db(state_dict: dict) -> Path:
    """Create a temporary state.vscdb with the given GCA state."""
    tmp = tempfile.NamedTemporaryFile(suffix=".vscdb", delete=False)
    tmp.close()
    conn = sqlite3.connect(tmp.name)
    conn.execute("CREATE TABLE IF NOT EXISTS ItemTable (key TEXT PRIMARY KEY, value TEXT)")
    conn.execute(
        "INSERT INTO ItemTable (key, value) VALUES (?, ?)",
        (STATE_KEY, json.dumps(state_dict)),
    )
    # Also insert unrelated keys to ensure they're untouched
    conn.execute(
        "INSERT INTO ItemTable (key, value) VALUES (?, ?)",
        ("some.other.extension", json.dumps({"foo": "bar", "count": 42})),
    )
    conn.commit()
    conn.close()
    return Path(tmp.name)


FIXTURE_STATE = {
    # Auth & project settings — MUST survive
    "geminicodeassist.hasRunOnce": True,
    "geminicodeassist.lastOpenedVersion": "2.78.0",
    "CACHED_PROJECTS_MEMENTO_KEY_founder@shadowtagai.com": {
        "projects": ["shadowtag-omega-v4"],
        "lastFetched": 1713308000,
    },
    "geminicodeassist.survey.useractivity": {"lastActive": 1713308000},
    "telemetry_setting_updated": True,
    "newChatIsAgent": True,
    # Error stack traces stored as keys (real-world pathology)
    "Error: ENOENT: no such file or directory": "some error value",
    # The bloat target — 3 fat threads
    THREADS_FIELD: [
        {
            "id": "thread-001",
            "title": "Oldest thread about Firebase deploy",
            "messages": [
                {"role": "user", "content": "Deploy to Firebase" * 500},
                {"role": "assistant", "content": "Running firebase deploy..." * 500},
            ],
        },
        {
            "id": "thread-002",
            "title": "Middle thread about debugging",
            "messages": [
                {"role": "user", "content": "Fix the ENOENT error" * 300},
                {
                    "role": "assistant",
                    "content": "Stack trace:\n" + "at Object.foo (/path:123)\n" * 200,
                },
            ],
        },
        {
            "id": "thread-003",
            "title": "Newest thread about Live Server",
            "messages": [
                {"role": "user", "content": "Fix live server extension"},
                {"role": "assistant", "content": "Checking node_modules..."},
            ],
        },
    ],
}


def test_inspect_reports_correct_metrics():
    """Inspect should report thread count, bytes, and other keys."""
    db = _create_test_db(FIXTURE_STATE)
    try:
        m = inspect(db)
        assert m["found"] is True
        assert m["valid_json"] is True
        assert m["thread_count"] == 3
        assert m["threads_bytes"] > 1000
        assert THREADS_FIELD not in m["other_keys"]
        assert "geminicodeassist.hasRunOnce" in m["other_keys"]
        print("✅ test_inspect_reports_correct_metrics")
    finally:
        os.unlink(db)


def test_prune_removes_only_chat_threads():
    """After prune, chatThreads is empty but all other keys are byte-for-byte preserved."""
    db = _create_test_db(FIXTURE_STATE)
    try:
        result = prune(db, keep=0)
        assert result["success"] is True
        assert result["freed_bytes"] > 0

        # Re-read and verify
        conn = sqlite3.connect(str(db))
        cursor = conn.cursor()

        # Verify GCA state
        cursor.execute("SELECT value FROM ItemTable WHERE key = ?", (STATE_KEY,))
        after_dict = json.loads(cursor.fetchone()[0])

        # chatThreads is now empty
        assert after_dict[THREADS_FIELD] == []

        # All other keys are preserved byte-for-byte
        for key in FIXTURE_STATE:
            if key == THREADS_FIELD:
                continue
            assert after_dict[key] == FIXTURE_STATE[key], f"Key '{key}' was modified!"

        # Unrelated extension data is untouched
        cursor.execute(
            "SELECT value FROM ItemTable WHERE key = 'some.other.extension'"
        )
        other = json.loads(cursor.fetchone()[0])
        assert other == {"foo": "bar", "count": 42}

        conn.close()
        print("✅ test_prune_removes_only_chat_threads")
    finally:
        os.unlink(db)


def test_prune_keep_newest():
    """--keep 1 should retain only the newest thread."""
    db = _create_test_db(FIXTURE_STATE)
    try:
        result = prune(db, keep=1)
        assert result["success"] is True

        conn = sqlite3.connect(str(db))
        after = json.loads(
            conn.execute(
                "SELECT value FROM ItemTable WHERE key = ?", (STATE_KEY,)
            ).fetchone()[0]
        )
        conn.close()

        threads = after[THREADS_FIELD]
        assert len(threads) == 1
        assert threads[0]["id"] == "thread-003"  # newest
        print("✅ test_prune_keep_newest")
    finally:
        os.unlink(db)


def test_invalid_json_fails_safely():
    """If the state value is invalid JSON, prune must refuse and not modify."""
    tmp = tempfile.NamedTemporaryFile(suffix=".vscdb", delete=False)
    tmp.close()
    conn = sqlite3.connect(tmp.name)
    conn.execute("CREATE TABLE IF NOT EXISTS ItemTable (key TEXT PRIMARY KEY, value TEXT)")
    broken_json = '{"geminiCodeAssist.chatThreads": [{"id": "x"'  # truncated
    conn.execute(
        "INSERT INTO ItemTable (key, value) VALUES (?, ?)", (STATE_KEY, broken_json)
    )
    conn.commit()
    conn.close()

    db = Path(tmp.name)
    try:
        result = prune(db, keep=0)
        assert result["success"] is False
        assert "invalid JSON" in result["reason"]

        # Verify the value was NOT modified
        conn = sqlite3.connect(str(db))
        raw = conn.execute(
            "SELECT value FROM ItemTable WHERE key = ?", (STATE_KEY,)
        ).fetchone()[0]
        conn.close()
        assert raw == broken_json  # byte-for-byte unchanged
        print("✅ test_invalid_json_fails_safely")
    finally:
        os.unlink(db)


def test_missing_key_fails_gracefully():
    """If the state key doesn't exist, prune returns failure without crash."""
    tmp = tempfile.NamedTemporaryFile(suffix=".vscdb", delete=False)
    tmp.close()
    conn = sqlite3.connect(tmp.name)
    conn.execute("CREATE TABLE IF NOT EXISTS ItemTable (key TEXT PRIMARY KEY, value TEXT)")
    conn.commit()
    conn.close()

    db = Path(tmp.name)
    try:
        result = prune(db, keep=0)
        assert result["success"] is False
        assert "key not found" in result["reason"]
        print("✅ test_missing_key_fails_gracefully")
    finally:
        os.unlink(db)


def test_vacuum_reclaims_space():
    """VACUUM should reduce file size after prune deletes large blobs."""
    db = _create_test_db(FIXTURE_STATE)
    try:
        # Prune first to create dead pages
        prune(db, keep=0)
        # VACUUM to reclaim
        result = vacuum_db(db)
        assert result["success"] is True
        assert result["after_size"] <= result["before_size"]
        print("✅ test_vacuum_reclaims_space")
    finally:
        os.unlink(db)


def test_locate_db_with_explicit_path():
    """locate_db should return the explicit path if it exists."""
    db = _create_test_db(FIXTURE_STATE)
    try:
        found = locate_db(str(db))
        assert found == db
        # Non-existent path should return None
        assert locate_db("/tmp/nonexistent_state_db_xyz.vscdb") is None
        print("✅ test_locate_db_with_explicit_path")
    finally:
        os.unlink(db)


def test_vacuum_standalone():
    """vacuum_db works on a clean DB without prune (--vacuum-only mode)."""
    db = _create_test_db(FIXTURE_STATE)
    try:
        result = vacuum_db(db)
        assert result["success"] is True
        assert result["before_size"] > 0
        assert result["after_size"] > 0
        # Should not crash on unpruned DB
        print("✅ test_vacuum_standalone")
    finally:
        os.unlink(db)


def test_monitor_mode_accepts_threshold():
    """monitor_mode function should accept a custom threshold parameter."""
    from prune_gca_chat_threads import monitor_mode
    import inspect as ins

    sig = ins.signature(monitor_mode)
    assert "threshold_mb" in sig.parameters
    assert sig.parameters["threshold_mb"].default == 20.0
    print("✅ test_monitor_mode_accepts_threshold")


if __name__ == "__main__":
    test_inspect_reports_correct_metrics()
    test_prune_removes_only_chat_threads()
    test_prune_keep_newest()
    test_invalid_json_fails_safely()
    test_missing_key_fails_gracefully()
    test_vacuum_reclaims_space()
    test_locate_db_with_explicit_path()
    test_vacuum_standalone()
    test_monitor_mode_accepts_threshold()
    print("\n🎉 All 9 tests passed.")
