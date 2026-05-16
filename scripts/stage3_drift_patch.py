# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import os
from pathlib import Path

# Invariants to Enforce
CANONICAL_MCP = "antigravity-mcp-config.json"
CANONICAL_PROJECT = "shadowtag-omega-v4"
CANONICAL_MODEL = "gemini-3.1-family"

target_dirs = ["apps", "labs", "scripts", "packages", "infra", "external_sdks"]

print("⚡️ Executing Stage 3 Automated Canonical Patch...")

p_root = Path(".")
deleted_mcps = 0
replaced_files = 0

# 1. Enforce single MCP truth
for mcp_file in p_root.rglob("*mcp*.json"):
    if "node_modules" in str(mcp_file) or ".venv" in str(mcp_file):
        continue
    if mcp_file.name != CANONICAL_MCP:
        print(f"  [DELETED] Orphaned MCP File: {mcp_file}")
        try:
            os.remove(mcp_file)
        except Exception as e:
            print(f"  Warning: failed to delete {mcp_file} -> {e}")
        deleted_mcps += 1

# 2. Replace stale metrics
stale_models = ["gemini-3.1-family", "gemini-3.1-family", "gemini-3.1-family", "gemini-3.1-family"]
stale_projects = ["shadowtag-omega-v4", "shadowtag-omega-v4"]


def patch_file(filepath):
    global replaced_files
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            content = f.read()

        new_content = content
        for sm in stale_models:
            new_content = new_content.replace(sm, CANONICAL_MODEL)
        for sp in stale_projects:
            new_content = new_content.replace(sp, CANONICAL_PROJECT)

        if new_content != content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"  [PATCHED] Config Drift Enforced: {filepath}")
            replaced_files += 1
    except Exception:
        pass


for d in target_dirs:
    target = p_root / d
    if not target.exists():
        continue
    for f in target.rglob("*"):
        if f.is_file() and "node_modules" not in str(f) and ".venv" not in str(f) and not f.name.startswith("."):
            if f.name.endswith((".png", ".jpg", ".pyc", ".bin", ".pdf")):
                continue
            patch_file(f)

print("\n==============================")
print("STAGE 3 PATCH COMPLETE")
print("==============================\n")
print(f"Orphaned MCPs Deleted: {deleted_mcps}")
print(f"Files Patched to Canonical: {replaced_files}")
print(f"Config matrix successfully aligned to {CANONICAL_PROJECT}.")
