#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
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

print("Starting Master Rule Pack overlay...")
for ex_dir in extract_dirs:
    src_dir = os.path.join(SOURCE_BASE, ex_dir)
    if not os.path.exists(src_dir):
        continue

    print(f"Applying payload from {ex_dir}...")
    for item in os.listdir(src_dir):
        # Skip __MACOSX and other junk
        if item.startswith(".") and item != ".github" and item != ".agent":
            continue

        s = os.path.join(src_dir, item)
        d = os.path.join(TARGET_BASE, item)

        if os.path.isdir(s):
            print(f"  Mergiug directory: {item}/")
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            print(f"  Copying file: {item}")
            shutil.copy2(s, d)

# Special cases: move trailing isolated JSONs into correct config dirs if applicable,
# but for now just leave them in the archive unless specified.
print("Successfully overlaid the control plane architectures and Superpowers/Antigravity Agent Skills.")
