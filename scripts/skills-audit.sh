#!/usr/bin/env bash
# scripts/skills-audit.sh — SkillOps Fleet Auditor
# Scans workspace + global skill directories, reports overlaps, stale skills, and counts.
# Usage: bash scripts/skills-audit.sh [--check-overlap] [--json]
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE_SKILLS="${REPO_ROOT}/.agents/skills"
GLOBAL_SKILLS="${HOME}/.gemini/antigravity/skills"
CHECK_OVERLAP=false
JSON_OUTPUT=false

for arg in "$@"; do
  case "$arg" in
    --check-overlap) CHECK_OVERLAP=true ;;
    --json) JSON_OUTPUT=true ;;
  esac
done

# ── Count active skills ──────────────────────────────────────
count_skills() {
  local dir="$1"
  local count=0
  if [[ -d "$dir" ]]; then
    while IFS= read -r -d '' skill_dir; do
      if [[ -f "${skill_dir}/SKILL.md" ]]; then
        count=$((count + 1))
      fi
    done < <(find "$dir" -mindepth 1 -maxdepth 1 -type d -not -name "_archive_*" -not -name "_dedup_*" -not -name "__pycache__" -print0 2>/dev/null)
  fi
  echo "$count"
}

# ── Count archived skills ────────────────────────────────────
count_archived() {
  local dir="$1"
  local count=0
  if [[ -d "$dir" ]]; then
    while IFS= read -r -d '' archive_dir; do
      while IFS= read -r -d '' skill_dir; do
        if [[ -f "${skill_dir}/SKILL.md" ]]; then
          count=$((count + 1))
        fi
      done < <(find "$archive_dir" -mindepth 1 -maxdepth 1 -type d -print0 2>/dev/null)
    done < <(find "$dir" -mindepth 1 -maxdepth 1 -type d \( -name "_archive_*" -o -name "_dedup_*" \) -print0 2>/dev/null)
  fi
  echo "$count"
}

WORKSPACE_COUNT=$(count_skills "$WORKSPACE_SKILLS")
GLOBAL_COUNT=$(count_skills "$GLOBAL_SKILLS")
WORKSPACE_ARCHIVED=$(count_archived "$WORKSPACE_SKILLS")
GLOBAL_ARCHIVED=$(count_archived "$GLOBAL_SKILLS")

# ── Overlap detection ────────────────────────────────────────
OVERLAP_COUNT=0
OVERLAPS=()
if [[ "$CHECK_OVERLAP" == "true" ]] && [[ -d "$WORKSPACE_SKILLS" ]] && [[ -d "$GLOBAL_SKILLS" ]]; then
  while IFS= read -r -d '' ws_skill; do
    skill_name="$(basename "$ws_skill")"
    if [[ -d "${GLOBAL_SKILLS}/${skill_name}" ]] && [[ -f "${GLOBAL_SKILLS}/${skill_name}/SKILL.md" ]]; then
      OVERLAP_COUNT=$((OVERLAP_COUNT + 1))
      OVERLAPS+=("$skill_name")
    fi
  done < <(find "$WORKSPACE_SKILLS" -mindepth 1 -maxdepth 1 -type d -not -name "_archive_*" -not -name "_dedup_*" -print0 2>/dev/null)
fi

TOTAL_ACTIVE=$(( WORKSPACE_COUNT + GLOBAL_COUNT - OVERLAP_COUNT ))
TOTAL_ARCHIVED=$(( WORKSPACE_ARCHIVED + GLOBAL_ARCHIVED ))

# ── Output ───────────────────────────────────────────────────
if [[ "$JSON_OUTPUT" == "true" ]]; then
  overlap_json="[]"
  if [[ ${#OVERLAPS[@]} -gt 0 ]]; then
    overlap_json=$(printf '"%s",' "${OVERLAPS[@]}")
    overlap_json="[${overlap_json%,}]"
  fi
  cat <<EOF
{
  "workspace_active": ${WORKSPACE_COUNT},
  "global_active": ${GLOBAL_COUNT},
  "overlap": ${OVERLAP_COUNT},
  "total_active": ${TOTAL_ACTIVE},
  "workspace_archived": ${WORKSPACE_ARCHIVED},
  "global_archived": ${GLOBAL_ARCHIVED},
  "total_archived": ${TOTAL_ARCHIVED},
  "overlapping_skills": ${overlap_json},
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
else
  echo "═══════════════════════════════════════════"
  echo "  SkillOps Fleet Audit Report"
  echo "═══════════════════════════════════════════"
  echo "  Workspace active:  ${WORKSPACE_COUNT}"
  echo "  Global active:     ${GLOBAL_COUNT}"
  echo "  Overlap:           ${OVERLAP_COUNT}"
  echo "  ─────────────────────────────────────────"
  echo "  TOTAL ACTIVE:      ${TOTAL_ACTIVE}"
  echo "  TOTAL ARCHIVED:    ${TOTAL_ARCHIVED}"
  echo "═══════════════════════════════════════════"
  if [[ ${#OVERLAPS[@]} -gt 0 ]]; then
    echo ""
    echo "  ⚠ Overlapping skills:"
    for s in "${OVERLAPS[@]}"; do
      echo "    - $s"
    done
  fi
fi
