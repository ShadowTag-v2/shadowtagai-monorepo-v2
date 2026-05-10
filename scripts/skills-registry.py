#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""scripts/skills-registry.py — SkillOps Registry Manager.

Maintains the canonical skill fleet registry. Provides refresh, overlap check,
upstream install, and count synchronization.

Usage:
    python3 scripts/skills-registry.py                  # Print fleet summary
    python3 scripts/skills-registry.py --refresh        # Update registry + evidence
    python3 scripts/skills-registry.py --check-upstream  # Check for upstream updates
    python3 scripts/skills-registry.py --install-missing # Install missing upstream skills
    python3 scripts/skills-registry.py --json           # JSON output
"""

from __future__ import annotations

import argparse
import datetime
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_SKILLS = REPO_ROOT / ".agents" / "skills"
GLOBAL_SKILLS = Path.home() / ".gemini" / "antigravity" / "skills"
EVIDENCE_FILE = REPO_ROOT / ".agent" / "evidence" / "index.ndjson"
HEARTBEAT_FILE = REPO_ROOT / ".beads" / "kairos_heartbeat.json"


def scan_skills(directory: Path) -> list[dict]:
  """Scan a directory for active skills (has SKILL.md, not archived)."""
  skills = []
  if not directory.is_dir():
    return skills
  for child in sorted(directory.iterdir()):
    if not child.is_dir():
      continue
    if child.name.startswith(("_archive_", "_dedup_", "__pycache__", ".")):
      continue
    skill_md = child / "SKILL.md"
    if skill_md.is_file():
      # Extract name and description from frontmatter
      name = child.name
      description = ""
      try:
        content = skill_md.read_text(encoding="utf-8")
        in_frontmatter = False
        for line in content.splitlines():
          if line.strip() == "---":
            in_frontmatter = not in_frontmatter
            continue
          if in_frontmatter and line.startswith("description:"):
            description = line.split(":", 1)[1].strip()
            break
      except OSError:
        pass
      skills.append(
        {
          "id": name,
          "path": str(
            child.relative_to(REPO_ROOT)
            if str(child).startswith(str(REPO_ROOT))
            else child
          ),
          "description": description,
          "size_bytes": skill_md.stat().st_size,
        }
      )
  return skills


def scan_archived(directory: Path) -> int:
  """Count archived skills in _archive_* and _dedup_* directories."""
  count = 0
  if not directory.is_dir():
    return count
  for child in directory.iterdir():
    if child.is_dir() and (
      child.name.startswith("_archive_") or child.name.startswith("_dedup_")
    ):
      for sub in child.iterdir():
        if sub.is_dir() and (sub / "SKILL.md").is_file():
          count += 1
  return count


def find_overlaps(workspace: list[dict], global_skills: list[dict]) -> list[str]:
  """Find skills that exist in both workspace and global directories."""
  ws_ids = {s["id"] for s in workspace}
  gl_ids = {s["id"] for s in global_skills}
  return sorted(ws_ids & gl_ids)


def append_evidence(event: str, details: dict) -> None:
  """Append an evidence entry to the NDJSON log."""
  EVIDENCE_FILE.parent.mkdir(parents=True, exist_ok=True)
  entry = {
    "event": event,
    "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    **details,
  }
  with open(EVIDENCE_FILE, "a", encoding="utf-8") as f:
    f.write(json.dumps(entry, separators=(",", ":")) + "\n")


def update_heartbeat(total_active: int) -> None:
  """Update the heartbeat with current skill count."""
  if HEARTBEAT_FILE.is_file():
    try:
      data = json.loads(HEARTBEAT_FILE.read_text(encoding="utf-8"))
      data["skill_fleet_active"] = total_active
      data["last_skillops_refresh"] = datetime.datetime.now(datetime.UTC).isoformat()
      HEARTBEAT_FILE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    except json.JSONDecodeError, OSError:
      pass


def main() -> None:
  parser = argparse.ArgumentParser(description="SkillOps Registry Manager")
  parser.add_argument(
    "--refresh", action="store_true", help="Update registry + evidence"
  )
  parser.add_argument(
    "--check-upstream", action="store_true", help="Check for upstream updates"
  )
  parser.add_argument(
    "--install-missing", action="store_true", help="Install missing upstream skills"
  )
  parser.add_argument("--json", action="store_true", help="JSON output")
  args = parser.parse_args()

  ws_skills = scan_skills(WORKSPACE_SKILLS)
  gl_skills = scan_skills(GLOBAL_SKILLS)
  overlaps = find_overlaps(ws_skills, gl_skills)
  ws_archived = scan_archived(WORKSPACE_SKILLS)
  gl_archived = scan_archived(GLOBAL_SKILLS)

  total_active = len(ws_skills) + len(gl_skills) - len(overlaps)
  total_archived = ws_archived + gl_archived

  report = {
    "workspace_active": len(ws_skills),
    "global_active": len(gl_skills),
    "overlap": len(overlaps),
    "total_active": total_active,
    "total_archived": total_archived,
    "overlapping_skills": overlaps,
    "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
  }

  if args.refresh:
    append_evidence(
      "skills.registry.refresh",
      {
        "total_active": total_active,
        "total_archived": total_archived,
        "overlaps": len(overlaps),
      },
    )
    update_heartbeat(total_active)

  if args.check_upstream:
    manifest_path = REPO_ROOT / "external_repos" / "upstream_manifest.yaml"
    if manifest_path.is_file():
      print(f"Upstream manifest found: {manifest_path}")
      print("(Upstream diff check requires network access — use npx skills add)")
    else:
      print("No upstream manifest found at external_repos/upstream_manifest.yaml")

  if args.install_missing:
    print("Install-missing requires npx skills CLI. Run manually:")
    print("  npx skills add google/skills")
    print("  npx skills add vercel-labs/skills")

  if args.json:
    print(json.dumps(report, indent=2))
  else:
    print("═══════════════════════════════════════════")
    print("  SkillOps Registry Report")
    print("═══════════════════════════════════════════")
    print(f"  Workspace active:  {len(ws_skills)}")
    print(f"  Global active:     {len(gl_skills)}")
    print(f"  Overlap:           {len(overlaps)}")
    print("  ─────────────────────────────────────────")
    print(f"  TOTAL ACTIVE:      {total_active}")
    print(f"  TOTAL ARCHIVED:    {total_archived}")
    print("═══════════════════════════════════════════")
    if overlaps:
      print("\n  ⚠ Overlapping skills:")
      for s in overlaps:
        print(f"    - {s}")


if __name__ == "__main__":
  main()
