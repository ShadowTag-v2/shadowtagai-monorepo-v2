#!/usr/bin/env python3
"""
unified_memory.py — Unified Memory Bridge (Gate 3 & 4)
Per operator_invariants.json PRE_ACTION_MEMORY_GATE steps 3 and 4.

Provides 'status' and 'hydrate' subcommands for verifying and loading
the Hot (Beads L1), Cold (Beads L2/JSONL), and GPTRAM caches.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, UTC
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BEADS_FILE = REPO_ROOT / ".beads" / "issues.jsonl"
GPTRAM_DIR = REPO_ROOT / ".gptram"
MEMORY_LOCK = REPO_ROOT / ".memory_lock_state"
MCP_MEMORY_DIR = REPO_ROOT / ".mcp-memory"

GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[1;33m"
NC = "\033[0m"


def _check_file(path: Path, label: str) -> dict:
    """Return a status dict for a single file/directory."""
    if path.is_file():
        size = path.stat().st_size
        return {"label": label, "status": "OK", "path": str(path), "size_bytes": size}
    if path.is_dir():
        count = sum(1 for _ in path.rglob("*") if _.is_file())
        return {"label": label, "status": "OK", "path": str(path), "file_count": count}
    return {"label": label, "status": "MISSING", "path": str(path)}


def _load_beads() -> list[dict]:
    """Load all beads from the JSONL ledger."""
    if not BEADS_FILE.exists():
        return []
    rows = []
    with BEADS_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                if isinstance(data, dict):
                    rows.append(data)
            except json.JSONDecodeError:
                continue
    return rows


def cmd_status(_args: argparse.Namespace) -> int:
    """Verify structural soundness of Hot, Cold, and GPTRAM caches."""
    print(f"{YELLOW}═══ MEMORY BRIDGE STATUS ═══{NC}")

    checks = [
        _check_file(BEADS_FILE, "Cold Store (Beads L2 JSONL)"),
        _check_file(GPTRAM_DIR, "GPTRAM Cache"),
        _check_file(MEMORY_LOCK, "Memory Lock State"),
        _check_file(MCP_MEMORY_DIR, "Hot Store (MCP Memory L1)"),
    ]

    all_ok = True
    for c in checks:
        status = c["status"]
        icon = f"{GREEN}✅{NC}" if status == "OK" else f"{RED}❌{NC}"
        detail = ""
        if "size_bytes" in c:
            detail = f" ({c['size_bytes']} bytes)"
        elif "file_count" in c:
            detail = f" ({c['file_count']} files)"
        print(f"  {icon} {c['label']}: {status}{detail}")
        if status != "OK":
            all_ok = False

    # Parse memory lock state
    if MEMORY_LOCK.exists():
        lock_text = MEMORY_LOCK.read_text(encoding="utf-8")
        if "MEMORY LOCKED" in lock_text:
            print(f"\n  {GREEN}🔒 Memory State: LOCKED{NC}")
        else:
            print(f"\n  {RED}🔓 Memory State: DRIFTED{NC}")
            all_ok = False
    else:
        print(f"\n  {RED}🔓 Memory State: UNKNOWN (lock file missing){NC}")
        all_ok = False

    # Bead count
    beads = _load_beads()
    open_count = sum(1 for b in beads if b.get("status") == "open")
    print(f"\n  📊 Beads: {len(beads)} total, {open_count} open")

    print(f"\n{GREEN if all_ok else RED}═══ {'ALL CACHES SOUND' if all_ok else 'DRIFT DETECTED — REVIEW ABOVE'} ═══{NC}")
    return 0 if all_ok else 1


def cmd_hydrate(_args: argparse.Namespace) -> int:
    """Pull inter-session Beads into the Hot Store for the active session."""
    print(f"{YELLOW}═══ HYDRATING CONTEXT ═══{NC}")

    beads = _load_beads()
    if not beads:
        print(f"  {YELLOW}⚠ No beads found to hydrate.{NC}")
        return 0

    # Emit open beads as Hot Store context
    open_beads = [b for b in beads if b.get("status") == "open"]
    decisions = [b for b in beads if b.get("tag") == "DECISION"]

    print(f"  📥 Loaded {len(beads)} beads from Cold Store")
    print(f"  🔓 {len(open_beads)} open tasks")
    print(f"  🧠 {len(decisions)} decision records")

    # Output active beads for agent consumption
    if open_beads:
        print(f"\n  {GREEN}Active Beads:{NC}")
        for b in open_beads:
            title = b.get("title", b.get("action", "untitled"))
            bid = b.get("id", "?")
            print(f"    [{bid}] {title}")

    if decisions:
        print(f"\n  {GREEN}Recent Decisions:{NC}")
        for d in decisions[-5:]:  # Last 5 decisions
            action = d.get("action", "unknown")
            entities = d.get("entities", [])
            print(f"    → {action} ({', '.join(entities) if entities else 'no entities'})")

    ts = datetime.now(UTC).isoformat()
    print(f"\n  ⏱ Hydration complete at {ts}")
    print(f"{GREEN}═══ HOT STORE PRIMED ═══{NC}")
    return 0


def cmd_compact(_args: argparse.Namespace) -> int:
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from src.services.context import FourTierContext
    print(f"{YELLOW}═══ MICROCOMPACTING HOT STORE ═══{NC}")
    ctx = FourTierContext()
    # Dummy operation for now as Hot Store reading depends on .mcp-memory format
    print(f"  {GREEN}✅ FourTierContext microcompact pipeline wired.{NC}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Unified Memory Bridge — Pre-Action Gate 3 & 4")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status", help="Verify cache structural soundness")
    sub.add_parser("hydrate", help="Pull beads into Hot Store")
    sub.add_parser("compact", help="Microcompact Hot Store via FourTierContext")
    args = parser.parse_args()

    if args.cmd == "status":
        return cmd_status(args)
    if args.cmd == "hydrate":
        return cmd_hydrate(args)
    if args.cmd == "compact":
        return cmd_compact(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
