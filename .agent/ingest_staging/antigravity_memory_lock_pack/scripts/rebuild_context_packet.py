#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from __future__ import annotations

import argparse
from pathlib import Path

KEY_FILES = [
    "AGENTS.md",
    "docs/MEMORY_LOCK.md",
    "docs/UPDATED_PNKLN_PACK.md",
    "monorepo_manifest.yaml",
    "antigravity-mcp-config.json",
    "docs/AUDIT_REPORT.md",
]


def safe_read(path: Path, limit: int = 12000) -> str:
    if not path.exists():
        return f"[missing] {path}\n"
    text = path.read_text(encoding="utf-8", errors="ignore")
    if len(text) > limit:
        text = text[:limit] + "\n[truncated]\n"
    return text


def build_packet(root: Path) -> str:
    parts = [
        "# Session Packet",
        "",
        "Use this packet when context is thin. It summarizes the current control plane from repo truth surfaces.",
        "",
        "## Mandatory operating order",
        "1. workspace truth",
        "2. MCP truth",
        "3. behavior truth",
        "4. survivorship truth",
        "5. current audit",
        "",
    ]
    for rel in KEY_FILES:
        path = root / rel
        parts.append(f"## Source: `{rel}`")
        parts.append("")
        parts.append("```text")
        parts.append(safe_read(path).rstrip())
        parts.append("```")
        parts.append("")
    return "\n".join(parts)


def build_recovery_packet(root: Path) -> str:
    return (
        "\n".join(
            [
                "# Recovery Packet",
                "",
                "If memory appears dropped:",
                "- stop feature work",
                "- run `scripts/root_guard.sh`",
                "- run `python3 scripts/memory_lock_audit.py --repo-root . --write`",
                "- run `python3 scripts/rebuild_context_packet.py --repo-root . --write`",
                "- read `docs/SESSION_PACKET.md`",
                "- continue only from canonical files and verified sources",
                "",
                "## Canonical files",
                "- AGENTS.md",
                "- docs/MEMORY_LOCK.md",
                "- docs/UPDATED_PNKLN_PACK.md",
                "- monorepo_manifest.yaml",
                "- antigravity-mcp-config.json",
            ]
        )
        + "\n"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", required=True)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    root = Path(args.repo_root).resolve()
    packet = build_packet(root)
    recovery = build_recovery_packet(root)
    if args.write:
        docs = root / "docs"
        docs.mkdir(exist_ok=True)
        (docs / "SESSION_PACKET.md").write_text(packet, encoding="utf-8")
        (docs / "RECOVERY_PACKET.md").write_text(recovery, encoding="utf-8")
    print(packet)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
