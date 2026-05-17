# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import json
from pathlib import Path

from service.app.adapters.authority_state import AuthorityState
from service.app.adapters.memory_atoms import search_atoms
from service.app.adapters.monorepo_truth import load_monorepo_truth
from service.app.config import load_settings
from service.app.utils.db import pg_conn

s = load_settings()
authority = AuthorityState(s.authority_state_path).read()
monorepo_truth = load_monorepo_truth(
  s.monorepo_manifest_path,
  s.monorepo_merge_status_path,
  s.monorepo_control_plane_path,
)

with pg_conn(s.postgres_dsn) as conn:
  cur = conn.cursor()
  cur.execute(
    "SELECT bead_id, title, status, summary FROM beads_tasks WHERE repo_id = %s ORDER BY updated_at DESC LIMIT 12",
    (s.repo_id,),
  )
  tasks = [
    {"id": r[0], "title": r[1], "status": r[2], "summary": r[3] or ""}
    for r in cur.fetchall()
  ]
  cur.execute(
    "SELECT summary FROM ltm_thread_summaries WHERE is_active = true ORDER BY created_at DESC LIMIT 5"
  )
  summaries = [r[0] for r in cur.fetchall()]
  cur.execute(
    "SELECT rel_path, drift_kind, expected, observed, severity, suggested_fix FROM drift_reports WHERE repo_id = %s ORDER BY created_at DESC LIMIT 12",
    (s.repo_id,),
  )
  drifts = [
    {
      "rel_path": r[0],
      "drift_kind": r[1],
      "expected": r[2],
      "observed": r[3],
      "severity": r[4],
      "suggested_fix": r[5],
    }
    for r in cur.fetchall()
  ]

atoms = search_atoms(
  s.postgres_dsn,
  s.repo_id,
  "formatter ane fallback startup memory authority current standards settings monorepo canonical roots",
  limit=24,
)

packet = {
  "repo_id": s.repo_id,
  "authority": authority,
  "monorepo_truth": monorepo_truth,
  "atoms": atoms,
  "active_tasks": tasks,
  "recent_summaries": summaries,
  "drift_reports": drifts,
}
out = Path("./data/memory/launch-packet.json")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
print({"exported": str(out)})
