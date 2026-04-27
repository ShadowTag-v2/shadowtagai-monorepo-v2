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

# ── Dangerous-pattern security scan ──────────────────────────
# Scans all SKILL.md files for patterns that violate RULE_00,
# secrets doctrine, or could cause destructive side-effects.
UNSAFE_COUNT=0
UNSAFE_FINDINGS=()

# Patterns that indicate dangerous or prohibited operations in skills
DANGEROUS_PATTERNS=(
  "private-key\.pem"
  "agentYoloMode"
  "git reset --hard"
  "git push.*--force"
  "git push.*-f "
  "while true"
  "rm -rf"
  "rm -r "
  "sudo "
  "\beval\b"
  "exec("
  "os\.system("
  "subprocess\.call.*shell=True"
  "sk_live_"
  "sk_test_"
  "AKIA[0-9A-Z]"
  "password\s*=\s*['\"]"
  "secret\s*=\s*['\"]"
  "curl.*\| bash"
  "wget.*\| sh"
  "filter-branch"
  "unlink "
)

scan_skills_for_danger() {
  local dir="$1"
  local label="$2"
  if [[ ! -d "$dir" ]]; then
    return
  fi

  while IFS= read -r -d '' skill_file; do
    local skill_name
    skill_name="$(basename "$(dirname "$skill_file")")"
    for pattern in "${DANGEROUS_PATTERNS[@]}"; do
      local matches
      matches=$(grep -c -E -i "$pattern" "$skill_file" 2>/dev/null || true)
      if [[ "$matches" -gt 0 ]]; then
        UNSAFE_COUNT=$((UNSAFE_COUNT + 1))
        UNSAFE_FINDINGS+=("${label}/${skill_name}|${pattern}|${matches}")
      fi
    done
  done < <(find "$dir" -name "SKILL.md" -not -path "*/_archive_*/*" -not -path "*/_dedup_*/*" -print0 2>/dev/null)
}

scan_skills_for_danger "$WORKSPACE_SKILLS" "workspace"
scan_skills_for_danger "$GLOBAL_SKILLS" "global"

# Write unsafe findings report
REPORT_DIR="${REPO_ROOT}/.reports/skills"
REPORT_FILE="${REPORT_DIR}/unsafe_findings.md"
if [[ "$UNSAFE_COUNT" -gt 0 ]]; then
  mkdir -p "$REPORT_DIR"
  {
    echo "# SkillOps Unsafe Pattern Report"
    echo ""
    echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "Total findings: ${UNSAFE_COUNT}"
    echo ""
    echo "| Skill | Pattern | Hits |"
    echo "|-------|---------|------|"
    for finding in "${UNSAFE_FINDINGS[@]}"; do
      IFS='|' read -r skill pattern hits <<< "$finding"
      echo "| ${skill} | \`${pattern}\` | ${hits} |"
    done
    echo ""
    echo "> These patterns may be legitimate documentation references."
    echo "> Review each finding manually before taking action."
  } > "$REPORT_FILE"
fi

# ── Output ───────────────────────────────────────────────────
if [[ "$JSON_OUTPUT" == "true" ]]; then
  overlap_json="[]"
  if [[ ${#OVERLAPS[@]} -gt 0 ]]; then
    overlap_json=$(printf '"%s",' "${OVERLAPS[@]}")
    overlap_json="[${overlap_json%,}]"
  fi
  unsafe_json="[]"
  if [[ ${#UNSAFE_FINDINGS[@]} -gt 0 ]]; then
    unsafe_json="["
    first=true
    for finding in "${UNSAFE_FINDINGS[@]}"; do
      IFS='|' read -r skill pattern hits <<< "$finding"
      if [[ "$first" == "true" ]]; then
        first=false
      else
        unsafe_json+=","
      fi
      unsafe_json+="{\"skill\":\"${skill}\",\"pattern\":\"${pattern}\",\"hits\":${hits}}"
    done
    unsafe_json+="]"
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
  "unsafe_findings": ${UNSAFE_COUNT},
  "overlapping_skills": ${overlap_json},
  "unsafe_details": ${unsafe_json},
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
  echo "  ─────────────────────────────────────────"
  echo "  🛡 Unsafe patterns: ${UNSAFE_COUNT}"
  echo "═══════════════════════════════════════════"
  if [[ ${#OVERLAPS[@]} -gt 0 ]]; then
    echo ""
    echo "  ⚠ Overlapping skills:"
    for s in "${OVERLAPS[@]}"; do
      echo "    - $s"
    done
  fi
  if [[ "$UNSAFE_COUNT" -gt 0 ]]; then
    echo ""
    echo "  🛡 Unsafe pattern findings:"
    for finding in "${UNSAFE_FINDINGS[@]}"; do
      IFS='|' read -r skill pattern hits <<< "$finding"
      echo "    - ${skill}: ${pattern} (${hits} hits)"
    done
    echo ""
    echo "  Report: .reports/skills/unsafe_findings.md"
  fi
fi
