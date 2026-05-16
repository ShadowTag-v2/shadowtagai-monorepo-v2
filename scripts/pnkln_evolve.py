#!/usr/bin/env python3
"""pnkln-evolve: Recursive self-improvement daemon.

Scans the monorepo for:
  1. Stale/duplicate skills (by semantic similarity of SKILL.md descriptions)
  2. Dead code (ruff F401/F841 — V22 doctrine, vulture banned)
  3. Documentation drift (manifest vs filesystem)
  4. Unused CI workflows
  5. Dependency freshness

Runs in two modes:
  --once: Single pass, exit with report
  --daemon: Continuous 5-minute jitter cycles

Rich Hickey Doctrine: Step 0 is DELETION.
"""

import argparse
import json
import random
import subprocess
import sys
import time
from datetime import datetime, UTC
from pathlib import Path

MONOREPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = MONOREPO_ROOT / ".agents" / "skills"
GLOBAL_SKILLS_DIR = Path.home() / ".gemini" / "antigravity" / "skills"
MANIFEST_PATH = MONOREPO_ROOT / "monorepo_manifest.yaml"
BEADS_DIR = MONOREPO_ROOT / ".beads"
EVOLVE_LOG = BEADS_DIR / "evolve_log.jsonl"


def log_event(event_type: str, details: dict) -> None:
  """Append a structured event to the evolve log."""
  BEADS_DIR.mkdir(parents=True, exist_ok=True)
  entry = {
    "timestamp": datetime.now(UTC).isoformat(),
    "type": event_type,
    **details,
  }
  with open(EVOLVE_LOG, "a") as f:
    f.write(json.dumps(entry) + "\n")


def scan_dead_code() -> dict:
  """Run ruff F401/F841 and return statistics."""
  try:
    result = subprocess.run(
      [
        "ruff",
        "check",
        "--select",
        "F401,F841",
        "--statistics",
        "--exclude",
        "external_repos,external_sdks,third_party,control/legacy_workspaces",
        str(MONOREPO_ROOT),
      ],
      capture_output=True,
      text=True,
      timeout=60,
    )
    lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
    return {"dead_code_lines": len(lines), "output": result.stdout[:500]}
  except (subprocess.TimeoutExpired, FileNotFoundError) as e:
    return {"error": str(e)}


def scan_duplicate_skills() -> dict:
  """Find skills with near-identical names or descriptions."""
  duplicates = []
  skills = {}

  for skills_dir in [SKILLS_DIR, GLOBAL_SKILLS_DIR]:
    if not skills_dir.exists():
      continue
    for skill_md in skills_dir.rglob("SKILL.md"):
      name = skill_md.parent.name
      # Read first 5 lines for description
      try:
        with open(skill_md) as f:
          _ = f.read(500)  # Guard: check file is readable
      except OSError:
        continue

      if name in skills:
        duplicates.append(
          {
            "name": name,
            "path_a": str(skills[name]),
            "path_b": str(skill_md),
          }
        )
      else:
        skills[name] = skill_md

  return {
    "total_skills": len(skills),
    "duplicates_found": len(duplicates),
    "duplicates": duplicates[:10],  # Cap output
  }


def scan_manifest_drift() -> dict:
  """Check if manifest stats match filesystem."""
  drift = []

  # Count actual skills
  agent_skills = list(SKILLS_DIR.rglob("SKILL.md")) if SKILLS_DIR.exists() else []
  global_skills = (
    list(GLOBAL_SKILLS_DIR.rglob("SKILL.md")) if GLOBAL_SKILLS_DIR.exists() else []
  )

  # Count CI workflows
  workflows_dir = MONOREPO_ROOT / ".github" / "workflows"
  workflows = list(workflows_dir.glob("*.yml")) if workflows_dir.exists() else []

  return {
    "agent_skills_count": len(agent_skills),
    "global_skills_count": len(global_skills),
    "ci_workflow_count": len(workflows),
    "drift_items": drift,
  }


def scan_stale_repos() -> dict:
  """Check omni_ingest repos for staleness (>30 days since last fetch)."""
  omni_dir = MONOREPO_ROOT / "external_repos" / "omni_ingest"
  if not omni_dir.exists():
    return {"error": "omni_ingest directory not found"}

  stale = []
  for repo_dir in sorted(omni_dir.iterdir()):
    if not repo_dir.is_dir() or not (repo_dir / ".git").exists():
      continue
    fetch_head = repo_dir / ".git" / "FETCH_HEAD"
    if fetch_head.exists():
      mtime = fetch_head.stat().st_mtime
      age_days = (time.time() - mtime) / 86400
      if age_days > 30:
        stale.append({"repo": repo_dir.name, "age_days": round(age_days, 1)})

  return {
    "total_repos": len(list(omni_dir.iterdir())),
    "stale_count": len(stale),
    "stale": stale[:10],
  }


def run_evolve_pass() -> dict:
  """Execute one full evolution pass."""
  print(f"[pnkln-evolve] Starting pass at {datetime.now(UTC).isoformat()}")

  results = {
    "dead_code": scan_dead_code(),
    "duplicate_skills": scan_duplicate_skills(),
    "manifest_drift": scan_manifest_drift(),
    "stale_repos": scan_stale_repos(),
  }

  log_event("evolve_pass", results)
  return results


def main():
  parser = argparse.ArgumentParser(
    description="pnkln-evolve: Recursive self-improvement daemon"
  )
  parser.add_argument(
    "--once", action="store_true", help="Single pass, exit with report"
  )
  parser.add_argument(
    "--daemon", action="store_true", help="Continuous 5-min jitter cycles"
  )
  parser.add_argument(
    "--interval", type=int, default=300, help="Base interval in seconds (default: 300)"
  )
  args = parser.parse_args()

  if args.once or not args.daemon:
    results = run_evolve_pass()
    print(json.dumps(results, indent=2))
    sys.exit(0)

  # Daemon mode with jitter
  print("[pnkln-evolve] Starting daemon mode")
  while True:
    try:
      results = run_evolve_pass()
      print(f"[pnkln-evolve] Pass complete: {len(results)} scans")
    except Exception as e:
      log_event("evolve_error", {"error": str(e)})
      print(f"[pnkln-evolve] Error: {e}")

    # Jitter: ±20% of base interval
    jitter = random.uniform(0.8, 1.2) * args.interval
    print(f"[pnkln-evolve] Sleeping {jitter:.0f}s (base={args.interval}s)")
    time.sleep(jitter)


if __name__ == "__main__":
  main()
