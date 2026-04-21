#!/usr/bin/env python3
import os
import shutil

SOURCE_BASE = "archive/downloads_ingest"
TARGET_BASE = "."

extract_dirs = [
    "pnkln_master_rules_pack_v2",
    "merged_master_rules_pack",
    "antigravity_rebuilt_bundle_2026_03_18",
    "antigravity_v11_merged_control_plane_final_bundle",
    "ane_cortex_stack_v9_bundle",
    "ane_cortex_stack_v10_bundle",
]

for ex_dir in extract_dirs:
    src_dir = os.path.join(SOURCE_BASE, ex_dir)
    if not os.path.exists(src_dir):
        continue

    for item in os.listdir(src_dir):
        # Skip __MACOSX and other junk
        if item.startswith(".") and item not in {".github", ".agent"}:
            continue

        s = os.path.join(src_dir, item)
        d = os.path.join(TARGET_BASE, item)

        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

# Special cases: move trailing isolated JSONs into correct config dirs if applicable,
# but for now just leave them in the archive unless specified.
