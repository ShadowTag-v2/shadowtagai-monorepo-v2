#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os
import shutil
import tarfile
import zipfile

DOWNLOADS = "/Users/pikeymickey/Downloads"
DEST = "archive/downloads_ingest"

targets = [
    f"{DOWNLOADS}/pnkln_master_rules_pack_v2.zip",
    f"{DOWNLOADS}/merged_master_rules_pack.zip",
    f"{DOWNLOADS}/antigravity_rebuilt_bundle_2026_03_18.zip",
    f"{DOWNLOADS}/antigravity_v11_merged_control_plane_final_bundle.tar.gz",
    f"{DOWNLOADS}/ane_cortex_stack_v9_bundle.tar.gz",
    f"{DOWNLOADS}/ane_cortex_stack_v10_bundle.tar.gz",
    f"{DOWNLOADS}/operator_invariants_atoms(1).json",
    f"{DOWNLOADS}/operator_invariants(1).json",
]

os.makedirs(DEST, exist_ok=True)

for path in targets:
    if os.path.exists(path):
        name = os.path.basename(path)
        out_path = os.path.join(DEST, name)
        shutil.copy2(path, out_path)

        # Extract into a subfolder named after the archive
        sub_dest = os.path.join(DEST, name.replace(".zip", "").replace(".tar.gz", ""))
        os.makedirs(sub_dest, exist_ok=True)

        try:
            if name.endswith(".zip"):
                with zipfile.ZipFile(out_path, "r") as z:
                    z.extractall(sub_dest)
            elif name.endswith(".tar.gz"):
                with tarfile.open(out_path, "r:gz") as t:
                    t.extractall(sub_dest)
        except Exception:
            pass
