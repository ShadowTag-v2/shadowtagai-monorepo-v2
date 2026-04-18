#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
cd "$ROOT"

echo "[audit] workspace root"
pwd -P

echo "[audit] canonical files"
test -f memory_lock.json || echo "[warn] missing memory_lock.json"
test -f antigravity-mcp-config.json || echo "[warn] missing antigravity-mcp-config.json"
test -f AGENTS.md || echo "[warn] missing AGENTS.md"

echo "[audit] product/lab split"
test -d apps/counselconduit || echo "[warn] missing apps/counselconduit"
test -d labs/uphillsnowball || echo "[warn] missing labs/uphillsnowball"

echo "[audit] stale model / mcp / naming scan"
python3 - <<'PY'
import json
from pathlib import Path

root = Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball")
patterns = {
    "stale_model": ["gemini-2.5", "gemini-3.1-flash-lite-preview"],
    "stale_mcp": ["mcp_config.json", "cline_mcp_settings.json", ".mcp.json"],
    "stale_naming": ["ShadowTag-v2", "ShadowTag", "ShadowTag-v2"],
    "forbidden_service_account_claim": [
        "Service Accounts: 767252945109-compute@developer.gserviceaccount.com is now REFRESHING at the start of every tool call. This is this service account’s only function!"
    ],
}

hits = {k: [] for k in patterns}
skip_suffixes = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".sqlite", ".db", ".pyc", ".pack", ".idx"}
skip_dirs = {".git", "node_modules", ".venv", ".beads", "dist", "build"}

for path in root.rglob("*"):
    if not path.is_file() or path.suffix.lower() in skip_suffixes:
        continue

    # Skip ignored directories
    if any(part in skip_dirs for part in path.parts):
        continue

    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue

    for key, needles in patterns.items():
        for needle in needles:
            if needle in text:
                hits[key].append({"file": str(path), "needle": needle})

print(json.dumps({k: v for k, v in hits.items() if v}, indent=2))
PY
