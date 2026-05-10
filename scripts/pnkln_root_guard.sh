#!/usr/bin/env bash
# ============================================================================
# Canonical Root Guard v8.5 — Monorepo Entrypoint
# ============================================================================
set -euo pipefail

# --- CONFIGURATION ---
EXPECTED_ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
ACTUAL_ROOT="$(pwd -P)"

# --- HELPERS ---
usage() {
    echo "Usage: $0 [check|validate <path>]"
    echo "  check: Verify current directory is canonical root and has truth files."
    echo "  validate <path>: Ensure <path> is inside root and NOT in a denied zone."
}

# --- PRIMARY LOGIC ---

# 1. Root verification
check_root() {
    if [[ "$ACTUAL_ROOT" != "$EXPECTED_ROOT" ]]; then
        echo "❌ [root-guard] ERROR: Not in canonical workspace root."
        echo "   Expected: $EXPECTED_ROOT"
        echo "   Actual:   $ACTUAL_ROOT"
        exit 1
    fi

    for f in monorepo_manifest.yaml AGENTS.md antigravity-mcp-config.json; do
        if [[ ! -f "$ACTUAL_ROOT/$f" ]]; then
            echo "❌ [root-guard] ERROR: Missing truth file: $f"
            exit 1
        fi
    done

    echo "✅ [root-guard] OK: Canonical root verified."
}

# 2. Path validation (from guard_path.sh)
validate_path() {
    local target="$1"

    if ! command -v realpath >/dev/null 2>&1; then
        echo "❌ ERROR: realpath is required." >&2
        exit 1
    fi

    local target_real
    target_real="$(realpath -m "${target}")"
    local root_real="$(realpath "${EXPECTED_ROOT}")"

    # Enforce root boundary
    case "${target_real}" in
        "${root_real}"|"${root_real}"/*)
            ;;
        *)
            echo "❌ ERROR: Path is outside canonical root: ${target_real}" >&2
            exit 1
            ;;
    esac

    # Denied zones audit
    case "${target_real}" in
        "${root_real}"/archive/recovery/*|\
        "${root_real}"/tools/legacy/*|\
        */_PRE_OMEGA_BACKUP_*/*|\
        */repos/*-legacy/*)
            echo "❌ ERROR: Path is in a denied/archived zone: ${target_real}" >&2
            exit 1
            ;;
        *)
            ;;
    esac

    echo "${target_real}"
}

# --- ROUTER ---
case "${1:-check}" in
    check)
        check_root
        ;;
    validate)
        if [[ -z "${2:-}" ]]; then usage; exit 2; fi
        validate_path "$2"
        ;;
    -h|--help)
        usage
        ;;
    *)
        usage
        exit 2
        ;;
esac
