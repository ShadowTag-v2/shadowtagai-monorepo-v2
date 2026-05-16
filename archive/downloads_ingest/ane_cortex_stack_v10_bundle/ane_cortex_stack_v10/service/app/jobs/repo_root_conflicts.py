# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations
from pathlib import Path
from ..config import load_settings
from ..adapters.monorepo_truth import load_monorepo_truth
from ..utils.db import pg_conn

def detect_repo_root_conflicts():
    s = load_settings()
    truth = load_monorepo_truth(
        s.monorepo_manifest_path,
        s.monorepo_merge_status_path,
        s.monorepo_control_plane_path,
    )
    canonical = set(truth.get("canonical_repo_roots", []))
    observed = set()

    for p in [Path("./apps/aiyou_stack"), Path("./apps")]:
        if p.exists():
            for child in p.rglob("*"):
                if child.is_dir():
                    rel = str(child).replace("\\", "/")
                    if rel.startswith("apps/aiyou_stack/"):
                        observed.add(rel)

    conflicts = []
    for root in observed:
        if root.startswith("apps/aiyou_stack/") and root not in canonical:
            conflicts.append({
                "observed_root": root,
                "canonical_root": ",".join(sorted(canonical)),
                "source_type": "filesystem_scan",
                "source_ref": root,
            })

    with pg_conn(s.postgres_dsn) as conn:
        cur = conn.cursor()
        for c in conflicts:
            cur.execute(
                "INSERT INTO repo_root_conflicts (repo_id, observed_root, canonical_root, source_type, source_ref) VALUES (%s, %s, %s, %s, %s)",
                (s.repo_id, c["observed_root"], c["canonical_root"], c["source_type"], c["source_ref"]),
            )
    return {"count": len(conflicts), "conflicts": conflicts}
