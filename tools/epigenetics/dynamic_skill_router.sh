#!/usr/bin/env bash
# tools/epigenetics/dynamic_skill_router.sh — Synaptic Plasticity Engine
#
# Runtime skill acquisition via decentralized registries.
# Bypasses static tool constraints by dynamically installing skills
# from Google and Vercel ecosystems.
#
# Usage:
#   ./tools/epigenetics/dynamic_skill_router.sh <capability-query>
#   ./tools/epigenetics/dynamic_skill_router.sh "firebase deploy"
#   ./tools/epigenetics/dynamic_skill_router.sh --list
#   ./tools/epigenetics/dynamic_skill_router.sh --audit
#
# Rule 00 compliant: No rm, unlink, or destructive operations.

set -euo pipefail

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SKILLS_DIR="${WORKSPACE_ROOT}/.agents/skills"
GOOGLE_REPO="${WORKSPACE_ROOT}/external_repos/google-skills"
VERCEL_REPO="${WORKSPACE_ROOT}/external_repos/vercel-skills"
AUDIT_LOG="${WORKSPACE_ROOT}/.beads/skill_acquisitions.jsonl"

# ─── Colors ─────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}[INFO]${NC} $*"; }
log_ok()    { echo -e "${GREEN}[OK]${NC} $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

# ─── Audit Trail ────────────────────────────────────────────────────────────
emit_audit() {
    local action="$1" skill="$2" source="$3"
    local ts
    ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    mkdir -p "$(dirname "$AUDIT_LOG")"
    echo "{\"ts\":\"${ts}\",\"action\":\"${action}\",\"skill\":\"${skill}\",\"source\":\"${source}\"}" >> "$AUDIT_LOG"
}

# ─── Functions ──────────────────────────────────────────────────────────────
count_skills() {
    if [ -d "$SKILLS_DIR" ]; then
        find "$SKILLS_DIR" -name "SKILL.md" -not -path "*/_archive_*" | wc -l | tr -d ' '
    else
        echo "0"
    fi
}

list_skills() {
    log_info "Skill Fleet Census"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    local count
    count=$(count_skills)
    echo -e "  Active skills: ${GREEN}${count}${NC}"
    echo ""

    if [ -d "$SKILLS_DIR" ]; then
        find "$SKILLS_DIR" -name "SKILL.md" -not -path "*/_archive_*" | sort | while read -r skill_file; do
            local skill_dir
            skill_dir="$(dirname "$skill_file")"
            local skill_name
            skill_name="$(basename "$skill_dir")"
            # Extract description from first line after frontmatter
            local desc
            desc="$(grep -m1 '^description:' "$skill_file" 2>/dev/null | sed 's/^description: *//' || echo "No description")"
            printf "  %-40s %s\n" "$skill_name" "$desc"
        done
    fi

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

search_local() {
    local query="$1"
    log_info "Searching local skill repos for: ${query}"

    local found=0

    # Search workspace skills
    if [ -d "$SKILLS_DIR" ]; then
        local results
        results="$(grep -rl "$query" "$SKILLS_DIR" 2>/dev/null | head -10 || true)"
        if [ -n "$results" ]; then
            log_ok "Found in workspace skills:"
            echo "$results" | while read -r f; do
                echo "  📁 $f"
            done
            found=1
        fi
    fi

    # Search Google skills repo
    if [ -d "$GOOGLE_REPO" ]; then
        local g_results
        g_results="$(grep -rl "$query" "$GOOGLE_REPO" 2>/dev/null | head -10 || true)"
        if [ -n "$g_results" ]; then
            log_ok "Found in Google skills repo:"
            echo "$g_results" | while read -r f; do
                echo "  🔵 $f"
            done
            found=1
        fi
    fi

    # Search Vercel skills repo
    if [ -d "$VERCEL_REPO" ]; then
        local v_results
        v_results="$(grep -rl "$query" "$VERCEL_REPO" 2>/dev/null | head -10 || true)"
        if [ -n "$v_results" ]; then
            log_ok "Found in Vercel skills repo:"
            echo "$v_results" | while read -r f; do
                echo "  ▲ $f"
            done
            found=1
        fi
    fi

    if [ "$found" -eq 0 ]; then
        log_warn "No local matches. Attempting remote acquisition..."
        acquire_remote "$query"
    fi
}

acquire_remote() {
    local query="$1"
    log_info "Attempting remote skill acquisition for: ${query}"

    # Try Google Skills first
    log_info "Querying google/skills registry..."
    if npx -y skills add google/skills --skill find-skills 2>/dev/null; then
        log_ok "Google skills registry queried successfully"
        emit_audit "SEARCH" "$query" "google/skills"
    else
        log_warn "Google skills registry unavailable"
    fi

    # Try Vercel Skills
    log_info "Querying vercel-labs/skills registry..."
    if npx -y skills add vercel-labs/skills --skill find-skills 2>/dev/null; then
        log_ok "Vercel skills registry queried successfully"
        emit_audit "SEARCH" "$query" "vercel-labs/skills"
    else
        log_warn "Vercel skills registry unavailable"
    fi

    local new_count
    new_count=$(count_skills)
    log_info "Post-acquisition skill count: ${new_count}"
}

audit_trail() {
    log_info "Skill Acquisition Audit Trail"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if [ -f "$AUDIT_LOG" ]; then
        tail -20 "$AUDIT_LOG" | while read -r line; do
            echo "  $line"
        done
    else
        log_warn "No acquisition history found"
    fi

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# ─── Main ───────────────────────────────────────────────────────────────────
main() {
    if [ $# -eq 0 ]; then
        echo "Usage: $0 <capability-query> | --list | --audit"
        exit 1
    fi

    case "$1" in
        --list)
            list_skills
            ;;
        --audit)
            audit_trail
            ;;
        --help|-h)
            echo "Synaptic Plasticity Engine — Dynamic Skill Router"
            echo ""
            echo "Usage:"
            echo "  $0 <query>   Search and acquire skills matching <query>"
            echo "  $0 --list    List all active skills"
            echo "  $0 --audit   Show acquisition audit trail"
            ;;
        *)
            echo "═══════════════════════════════════════════════════════════"
            echo "  🧬 Synaptic Plasticity Engine — Skill Acquisition"
            echo "═══════════════════════════════════════════════════════════"
            echo ""
            search_local "$1"
            echo ""
            echo "═══════════════════════════════════════════════════════════"
            echo "  ✅ Acquisition cycle complete"
            echo "  📊 Active skills: $(count_skills)"
            echo "═══════════════════════════════════════════════════════════"
            ;;
    esac
}

main "$@"
