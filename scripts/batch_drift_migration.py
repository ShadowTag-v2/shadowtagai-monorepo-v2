#!/usr/bin/env python3
"""Batch drift migration — move non-canonical top-level directories to archive/.

This script moves tracked files from non-canonical top-level directories
into archive/ to satisfy the repo doctor layout check. It uses `git mv`
to preserve history.

Run: python3 scripts/batch_drift_migration.py [--dry-run] [--execute]
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Canonical layout — these directories are allowed at the top level
CANONICAL = {
  "apps",
  "libs",
  "labs",
  "packages",
  "scripts",
  "tools",
  "docs",
  "infra",
  "vault",
  "archive",
  # Extended canonical (added based on actual usage)
  "tests",
  "services",
  "core",
  "knowledge",
  "keys",
}

# Directories that should be moved into archive/ with a descriptive prefix
MIGRATION_MAP = {
  # Claude Code audit artifacts
  "_audit_claude_code": "archive/claude_code_audit_2026",
  "src": "archive/claude_code_src_extract",
  "scratch": "archive/scratch_2026",
  # Already-archived directories with non-canonical names
  "_archive_redundant_2026-04-25": "archive/redundant_2026-04-25",
  "_archive_redundant_2026-04-30": "archive/redundant_2026-04-30",
  "_archive_redundant_2026-05-02": "archive/redundant_2026-05-02",
  "_archive_redundant_venvs_2026-05-04": "archive/redundant_venvs_2026-05-04",
  "_archive": "archive/stale_middleware",
  # Legacy workspaces
  "control": "archive/control_legacy",
  # Third-party code
  "third_party": "archive/third_party",
  # Product sites and reports
  "product-pitch-site": "archive/product_pitch_site",
  "playwright-report": "archive/playwright_report",
  "test-results": "archive/test_results",
  # Infrastructure (keep separate from infra/)
  "infrastructure": "archive/infrastructure_legacy",
  "terraform": "archive/terraform_legacy",
  # Code modules that should be in packages/ or libs/
  "antigravity-core": "archive/antigravity_core",
  "Claude_Code_6": "archive/claude_code_6",
  "judge6": "archive/judge6",
  "pnkln": "archive/pnkln_legacy",
  # Misc
  "tool_contracts": "archive/tool_contracts",
  "dataconnect": "archive/dataconnect",
  "governance": "archive/governance",
  "external_payloads": "archive/external_payloads",
  "skills": "archive/skills_legacy",
  # Broken directory name (created by accidental --force flag)
  "--force": "archive/force_views",
  # Quoted archive (broken directory name)
  '"archive': "archive/old_artifacts_phase0",
  # ── Remaining small directories (1-4 files each) ──
  "public": "archive/public_legacy",
  "_archive_redundant_2026-04-29": "archive/redundant_2026-04-29",
  "_archive_legacy_beads_2026-04-28": "archive/legacy_beads_2026-04-28",
  "config": "archive/config_legacy",
  "configs": "archive/configs_legacy",
  "extensions": "archive/extensions",
  "shared": "archive/shared_legacy",
  "target": "archive/target_build",
  "eslint-plugin-cor-rules": "archive/eslint_plugin_cor_rules",
  "evals": "archive/evals",
  "external_repos": "archive/external_repos",
  "ops": "archive/ops_legacy",
  "reference_architectures": "archive/reference_architectures",
  "reports": "archive/reports_legacy",
  "src-tauri": "archive/src_tauri",
  "staging": "archive/staging",
  "artifacts": "archive/artifacts_legacy",
  "authz": "archive/authz",
  "benchmarks": "archive/benchmarks",
  "build": "archive/build_output",
  "cmd": "archive/cmd_legacy",
  "contracts": "archive/contracts",
  "design": "archive/design",
  "infrastructure-pulumi": "archive/infrastructure_pulumi",
  "otel": "archive/otel",
  "templates": "archive/templates",
  "temporal": "archive/temporal",
}


def get_drift_dirs() -> dict[str, int]:
  """Get all non-canonical top-level directories with file counts."""
  r = subprocess.run(
    ["git", "ls-files"],
    capture_output=True,
    text=True,
    cwd=REPO_ROOT,
  )
  from collections import Counter

  counts: Counter[str] = Counter()
  for line in r.stdout.strip().splitlines():
    if "/" in line:
      top = line.split("/")[0]
      if not top.startswith(".") and top not in CANONICAL:
        counts[top] += 1
  return dict(counts.most_common())


def migrate(dry_run: bool = True) -> None:
  """Execute the migration."""
  drift = get_drift_dirs()

  if not drift:
    print("✅ No drift directories found — layout is canonical!")
    return

  print(f"Found {sum(drift.values())} drift files across {len(drift)} directories\n")

  moved = 0
  skipped = 0
  for dirname, count in drift.items():
    src = REPO_ROOT / dirname
    if dirname in MIGRATION_MAP:
      dest = REPO_ROOT / MIGRATION_MAP[dirname]
      action = f"→ {MIGRATION_MAP[dirname]}"
    else:
      print(f"  ⚠️  {dirname:40s} ({count:5d} files) — NO MAPPING, skipping")
      skipped += count
      continue

    if dry_run:
      print(f"  📦 {dirname:40s} ({count:5d} files) {action}")
      moved += count
    else:
      dest.parent.mkdir(parents=True, exist_ok=True)
      if dest.exists():
        # Merge into existing directory
        print(f"  🔀 {dirname:40s} ({count:5d} files) {action} (merging)")
        # Use git mv for each file individually to handle merge
        r = subprocess.run(
          ["git", "ls-files", dirname],
          capture_output=True,
          text=True,
          cwd=REPO_ROOT,
        )
        for fpath in r.stdout.strip().splitlines():
          rel = fpath[len(dirname) :]
          target = dest / rel.lstrip("/")
          target.parent.mkdir(parents=True, exist_ok=True)
          subprocess.run(
            ["git", "mv", "-f", fpath, str(target)],
            cwd=REPO_ROOT,
            capture_output=True,
          )
      else:
        print(f"  📦 {dirname:40s} ({count:5d} files) {action}")
        subprocess.run(
          ["git", "mv", str(src), str(dest)],
          cwd=REPO_ROOT,
          check=True,
        )
      moved += count

  print(
    f"\n{'DRY RUN — ' if dry_run else ''}Summary: {moved} files moved, {skipped} files skipped"
  )
  if dry_run:
    print("\nRe-run with --execute to apply changes")


if __name__ == "__main__":
  execute = "--execute" in sys.argv
  migrate(dry_run=not execute)
