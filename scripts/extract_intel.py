# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os
import shutil
from pathlib import Path

TARGET_DIR = os.path.abspath("apps/ShadowTag-v2_ecosystem/recovered_intel")

# The list of highly specific intellectual property directories
# EXCLUSIONS: /Users/pikeymickey and /Users/Deleted Users/pikeymickey have been filtered out
# to prevent catastrophic exponential cloning of the entire macOS SSD.
INTEL_PATHS = [
    "/Users/pikeymickey/.gemini/antigravity/playground/molten-universe/ast-grep",
    "/Users/pikeymickey/.gemini/antigravity/playground/molten-universe/.vscode",
    "/Users/pikeymickey/.gemini/antigravity/playground/molten-universe/ast-grep-mcp",
    "/Users/pikeymickey/.gemini/antigravity/playground/molten-universe/ast-grep-vscode",
    "/Users/pikeymickey/.gemini/antigravity/playground/molten-universe/ast-grep.github.io",
    "/Users/pikeymickey/.gemini/antigravity/playground/molten-universe/grep-ast",
    "/Users/pikeymickey/.gemini/antigravity/playground/molten-universe/heavy_lift",
    "/Users/pikeymickey/.gemini/antigravity/playground/cosmic-crab/.agent",
    "/Users/pikeymickey/.gemini/antigravity/playground/cosmic-crab/.antigravity",
    "/Users/pikeymickey/.gemini/antigravity/playground/cosmic-crab",
    "/Users/pikeymickey/.gemini/antigravity-demo-archive/antigravity-demo-2026-3-7-25",
    "/Users/pikeymickey/.gemini/antigravity-backup-recovered/playground",
    "/Users/pikeymickey/antigravity-knowledge",
    "/Users/pikeymickey/Library/Application Support/Claude",
    "/Users/pikeymickey/.antigravity/nascent-apollo",
    "/Users/pikeymickey/.gemini/antigravity-demo-archive/antigravity-demo-2026-3-7-25/brain",
    "/Users/pikeymickey/.gemini/history",
    "/Users/pikeymickey/.gemini/antigravity-demo-archive/antigravity-demo-2026-3-7-25/code_tracker/active/ShadowTag-v2_bea43616e508f85cade1de6fdee33ec72b5e65b1",
]


def sanitize_name(path_str):
    # Convert absolute paths to folder names
    return path_str.replace("/", "_").replace(" ", "_")[1:]


success_count = 0
for path in INTEL_PATHS:
    p = Path(path)
    if not p.exists():
        continue

    # Destination mapping
    safe_name = sanitize_name(path)
    dest_path = os.path.join(TARGET_DIR, safe_name)

    if os.path.exists(dest_path):
        continue

    try:
        if p.is_dir():
            shutil.copytree(path, dest_path, dirs_exist_ok=True, ignore_dangling_symlinks=True)
        else:
            shutil.copy2(path, dest_path)
        success_count += 1
    except Exception:
        pass
