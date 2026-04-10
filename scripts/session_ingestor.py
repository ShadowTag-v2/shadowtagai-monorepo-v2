#!/usr/bin/env python3
"""
ShadowTag-v2 Session Ingestor
======================
Reads TELEPORT_MANIFEST.json, finds session files in ~/.claude/projects/,
extracts conversation text, embeds via Gemini text-embedding-004, and
POSTs to ShadowTag-v2 RAG /api/v1/ShadowTag-v2/graph/insert.

Processes JUDGE_LEVEL first (priority 1), then JUDGE_EXTENDED, etc.

Usage:
  python scripts/session_ingestor.py                 # ingest all
  python scripts/session_ingestor.py --group JUDGE_LEVEL
  python scripts/session_ingestor.py --dry-run       # show what would be ingested
  ShadowTag-v2_DRY_RUN=1 python scripts/session_ingestor.py

env:
  GEMINI_API_KEY         required for embedding
  VITE_API_URL           ShadowTag-v2 API base (default: http://localhost:8000)
  ShadowTag-v2_DRY_RUN          set to 1 for dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "apps" / "ShadowTag-v2_stack" / "nascent-apollo" / "Docs" / "TELEPORT_MANIFEST.json"
CLAUDE_PROJECTS = Path.home() / ".claude" / "projects" / "-Users-pikeymickey"
API_BASE = os.getenv("VITE_API_URL", "http://localhost:8000")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
EMBED_MODEL = "text-embedding-004"
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200
DRY_RUN = os.getenv("ShadowTag-v2_DRY_RUN", "0") == "1"

# ── Text utilities ─────────────────────────────────────────────────────────────

def chunk_text(text: str) -> list[str]:
    chunks: list[str] = []
    start = 0
    n = len(text)
    while start < n:
        chunks.append(text[start: start + CHUNK_SIZE])
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks

# ── Session discovery ─────────────────────────────────────────────────────────

def find_session_file(session_id: str) -> Path | None:
    """
    Search for session data in ~/.claude/projects/.

    NOTE: Manifest session IDs use the Anthropic cloud format (session_01XXXX).
    Local JSONL files use UUID format keyed by the local sessionId field.
    These two namespaces do NOT overlap — cloud session IDs have no local file.

    For cloud session_01XXXX IDs this will always return None unless the ID
    appears verbatim in conversation content (e.g. the user typed it).
    Use --local-only to ingest the UUID sessions that actually exist on disk.
    """
    # Direct JSONL in projects dir — scan full content
    for f in CLAUDE_PROJECTS.glob("*.jsonl"):
        if session_id in f.read_text(errors="ignore"):
            return f
    # Subdirectory layout
    for d in CLAUDE_PROJECTS.iterdir():
        if d.is_dir():
            for f in d.glob("*.jsonl"):
                if session_id in f.read_text(errors="ignore"):
                    return f
    return None


def all_local_jsonl_files() -> list[Path]:
    """Return all JSONL files present in the Claude projects directory."""
    files: list[Path] = list(CLAUDE_PROJECTS.glob("*.jsonl"))
    for d in CLAUDE_PROJECTS.iterdir():
        if d.is_dir():
            files.extend(d.glob("*.jsonl"))
    return files


def extract_text_from_jsonl(path: Path) -> str:
    """Extract role+content pairs from a Claude Code JSONL conversation file."""
    parts: list[str] = []
    for line in path.read_text(errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg = obj.get("message", obj)
        role = msg.get("role", "")
        content = msg.get("content", "")
        if isinstance(content, str) and content.strip():
            parts.append(f"{role}: {content.strip()}")
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    txt = block.get("text", "").strip()
                    if txt:
                        parts.append(f"{role}: {txt}")
    return "\n---\n".join(parts)

# ── Gemini embedding ───────────────────────────────────────────────────────────

def embed_gemini(text: str) -> list[float]:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not set")
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{EMBED_MODEL}:embedContent?key={GEMINI_API_KEY}"
    )
    body = json.dumps({
        "model": f"models/{EMBED_MODEL}",
        "content": {"parts": [{"text": text}]},
    }).encode()
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    return data["embedding"]["values"]

# ── Insert ─────────────────────────────────────────────────────────────────────

def insert_chunk(artifact_id: str, text: str, tags: dict[str, Any], embed: list[float]) -> bool:
    payload = json.dumps({
        "artifactId": artifact_id,
        "text": text,
        "tags": tags,
        "embed": embed,
    }).encode()
    req = urllib.request.Request(
        f"{API_BASE}/api/v1/ShadowTag-v2/graph/insert",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status in (200, 201)
    except urllib.error.URLError:
        return False

# ── Core ingest ────────────────────────────────────────────────────────────────

def ingest_session(session_id: str, group: str) -> dict[str, Any]:
    session_path = find_session_file(session_id)
    if session_path is None:
        return {"status": "not_found", "session_id": session_id, "chunks": 0}

    text = extract_text_from_jsonl(session_path)
    if not text.strip():
        return {"status": "empty", "session_id": session_id, "chunks": 0}

    chunks = chunk_text(text)
    ingested = 0

    for i, chunk in enumerate(chunks):
        artifact_id = f"claude-session-{session_id}-chunk{i}-{int(time.time())}"
        tags: dict[str, Any] = {
            "source": "claude-code-session",
            "session_id": session_id,
            "group": group,
            "chunk": i,
            "total": len(chunks),
            "ingestedAt": int(time.time()),
            "embedModel": EMBED_MODEL,
        }

        if DRY_RUN:
            print(f"[dry-run] {session_id} chunk {i + 1}/{len(chunks)} ({len(chunk)} chars)")
            ingested += 1
            continue

        try:
            embed = embed_gemini(chunk)
        except Exception as exc:
            print(f"[ingestor] embed failed for {session_id} chunk {i + 1}: {exc}")
            continue

        ok = insert_chunk(artifact_id, chunk, tags, embed)
        status = "OK" if ok else "FAIL"
        print(f"[ingestor] {session_id} chunk {i + 1}/{len(chunks)} → {status}")
        if ok:
            ingested += 1

    return {
        "status": "ingested" if ingested > 0 else "failed",
        "session_id": session_id,
        "chunks": ingested,
        "total_chunks": len(chunks),
        "timestamp": int(time.time()),
    }

# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="ShadowTag-v2 Session Ingestor")
    parser.add_argument("--group", help="Only ingest sessions from this group")
    parser.add_argument("--all", action="store_true", help="Ingest all groups (priority order)")
    parser.add_argument("--local-only", action="store_true",
                        help="Ingest all local UUID JSONL files (bypasses manifest session IDs)")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be ingested")
    args = parser.parse_args()

    global DRY_RUN
    if args.dry_run:
        DRY_RUN = True

    # ── Local-only mode: ingest whatever JSONL files actually exist ────────────
    if args.local_only:
        files = all_local_jsonl_files()
        print(f"[ingestor] --local-only: found {len(files)} local JSONL files")
        for f in files:
            sid = f.stem  # UUID filename without .jsonl extension
            text = extract_text_from_jsonl(f)
            if not text.strip():
                print(f"[ingestor] {sid} → empty, skip")
                continue
            chunks = chunk_text(text)
            print(f"[ingestor] {sid} → {len(chunks)} chunks ({len(text)} chars)")
            if DRY_RUN:
                for i, c in enumerate(chunks):
                    print(f"  [dry-run] chunk {i+1}/{len(chunks)} ({len(c)} chars)")
                continue
            ingested = 0
            for i, chunk in enumerate(chunks):
                artifact_id = f"claude-local-{sid}-chunk{i}-{int(time.time())}"
                tags: dict[str, Any] = {
                    "source": "claude-code-local",
                    "session_id": sid,
                    "group": "LOCAL",
                    "chunk": i,
                    "total": len(chunks),
                    "ingestedAt": int(time.time()),
                    "embedModel": EMBED_MODEL,
                }
                try:
                    embed = embed_gemini(chunk)
                except Exception as exc:
                    print(f"[ingestor] embed failed chunk {i+1}: {exc}")
                    continue
                ok = insert_chunk(artifact_id, chunk, tags, embed)
                if ok:
                    ingested += 1
                    print(f"[ingestor] {sid} chunk {i+1}/{len(chunks)} → OK")
                else:
                    print(f"[ingestor] {sid} chunk {i+1}/{len(chunks)} → FAIL")
            print(f"[ingestor] {sid} → {ingested}/{len(chunks)} chunks ingested")
        return

    # ── Manifest-based mode ────────────────────────────────────────────────────
    if not MANIFEST_PATH.exists():
        print(f"ERROR: manifest not found at {MANIFEST_PATH}", flush=True)
        print("Run: python scripts/session_manifest_builder.py Docs/raw_sessions.txt", flush=True)
        raise SystemExit(1)

    manifest: dict[str, Any] = json.loads(MANIFEST_PATH.read_text())
    groups = manifest.get("groups", {})
    ingest_status: dict[str, Any] = manifest.get("ingest_status", {})

    print("[ingestor] NOTE: manifest session IDs (session_01XXXX) are Anthropic cloud IDs.")
    print("[ingestor] Local ~/.claude/projects/ uses UUID format. Use --local-only for local sessions.")

    # Sort groups by priority
    sorted_groups = sorted(groups.items(), key=lambda x: x[1].get("priority", 99))

    for group_name, group_data in sorted_groups:
        if args.group and group_name != args.group:
            continue
        sessions = group_data.get("sessions", [])
        print(f"\n[ingestor] group={group_name} priority={group_data.get('priority')} sessions={len(sessions)}")

        for sid in sessions:
            # Skip already ingested
            if sid in ingest_status and ingest_status[sid].get("status") == "ingested":
                print(f"[ingestor] skip {sid} (already ingested)")
                continue

            result = ingest_session(sid, group_name)
            ingest_status[sid] = result
            print(f"[ingestor] {sid} → {result['status']} ({result.get('chunks', 0)} chunks)")

            # Persist status after each session (fault-tolerant)
            if not DRY_RUN:
                manifest["ingest_status"] = ingest_status
                MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n")

    total_ingested = sum(1 for v in ingest_status.values() if v.get("status") == "ingested")
    total_not_found = sum(1 for v in ingest_status.values() if v.get("status") == "not_found")
    print(f"\n[ingestor] done. ingested={total_ingested} not_found={total_not_found}")
    if total_not_found > 0:
        print(f"[ingestor] {total_not_found} not_found = cloud IDs with no local JSONL. Run --local-only instead.")


if __name__ == "__main__":
    main()
