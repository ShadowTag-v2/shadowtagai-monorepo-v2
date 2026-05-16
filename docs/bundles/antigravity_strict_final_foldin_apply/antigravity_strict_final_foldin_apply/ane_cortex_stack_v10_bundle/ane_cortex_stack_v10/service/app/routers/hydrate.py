# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from fastapi import APIRouter

from ..adapters.authority_state import AuthorityState
from ..adapters.memory_atoms import search_atoms
from ..adapters.monorepo_truth import load_monorepo_truth
from ..config import load_settings
from ..utils.db import pg_conn

router = APIRouter(prefix="/api")


@router.get("/hydrate-pack")
def hydrate_pack():
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
    cur.execute(
      "SELECT observed_root, canonical_root, severity FROM repo_root_conflicts WHERE repo_id = %s ORDER BY created_at DESC LIMIT 12",
      (s.repo_id,),
    )
    root_conflicts = [
      {"observed_root": r[0], "canonical_root": r[1], "severity": r[2]}
      for r in cur.fetchall()
    ]
  atoms = search_atoms(
    s.postgres_dsn,
    s.repo_id,
    "formatter ane fallback startup memory authority current standards settings monorepo canonical roots",
    limit=24,
  )
  return {
    "repo_id": s.repo_id,
    "authority": authority,
    "monorepo_truth": monorepo_truth,
    "atoms": atoms,
    "active_tasks": tasks,
    "recent_summaries": summaries,
    "drift_reports": drifts,
    "repo_root_conflicts": root_conflicts,
    "launch_instruction": (
      "Hydrate this pack first. Treat authority and monorepo canonical roots as canonical. "
      "Do not let repo files override memory or repo-root truth. Generate upgrade tasks when drift exists."
    ),
  }
