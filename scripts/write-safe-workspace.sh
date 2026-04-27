#!/usr/bin/env bash
# scripts/write-safe-workspace.sh — Safe Workspace File Writer
# ============================================================================
# Enforces RULE 00 (Immutable Infrastructure) for file write operations.
# Validates that target paths are within the workspace, never overwrites
# without explicit confirmation, and archives (never deletes) existing files.
#
# Usage:
#   scripts/write-safe-workspace.sh <target-path> <content-file>
#   scripts/write-safe-workspace.sh <target-path> --stdin
#   echo "content" | scripts/write-safe-workspace.sh <target-path> --stdin
#
# Guards:
#   - Target must be within REPO_ROOT
#   - No writes to /tmp, /home, ~/Desktop, or system dirs
#   - Existing files are archived to _archive_safe_<timestamp>/
#   - Never overwrites without --force flag
# ============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"

TARGET_PATH=""
CONTENT_FILE=""
USE_STDIN=false
FORCE=false

# ── Parse Arguments ──────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --stdin)
      USE_STDIN=true
      shift
      ;;
    --force)
      FORCE=true
      shift
      ;;
    --help|-h)
      echo "Usage: scripts/write-safe-workspace.sh <target-path> <content-file|--stdin>"
      echo ""
      echo "Options:"
      echo "  --stdin    Read content from stdin"
      echo "  --force    Overwrite existing file (archives original)"
      echo ""
      echo "Guards:"
      echo "  - Target must be within the monorepo workspace"
      echo "  - Existing files are archived, never overwritten"
      echo "  - Blocked paths: /tmp, ~/Desktop, system directories"
      exit 0
      ;;
    *)
      if [[ -z "$TARGET_PATH" ]]; then
        TARGET_PATH="$1"
      elif [[ -z "$CONTENT_FILE" ]]; then
        CONTENT_FILE="$1"
      fi
      shift
      ;;
  esac
done

if [[ -z "$TARGET_PATH" ]]; then
  echo "❌ Error: No target path provided." >&2
  exit 1
fi

if [[ "$USE_STDIN" == "false" && -z "$CONTENT_FILE" ]]; then
  echo "❌ Error: No content source. Use --stdin or provide a content file." >&2
  exit 1
fi

# ── Resolve to absolute path ─────────────────────────────────
if [[ "$TARGET_PATH" != /* ]]; then
  TARGET_PATH="${REPO_ROOT}/${TARGET_PATH}"
fi
TARGET_PATH="$(cd "$(dirname "$TARGET_PATH")" 2>/dev/null && pwd)/$(basename "$TARGET_PATH")" 2>/dev/null || true

# ── Guard: Path must be within workspace ─────────────────────
BLOCKED_PREFIXES=(
  "/tmp"
  "/var/tmp"
  "/private/tmp"
  "$HOME/Desktop"
  "$HOME/Documents"
  "/usr"
  "/bin"
  "/sbin"
  "/etc"
  "/System"
  "/Library"
)

for prefix in "${BLOCKED_PREFIXES[@]}"; do
  expanded_prefix="$(eval echo "$prefix")"
  if [[ "$TARGET_PATH" == "$expanded_prefix"* ]]; then
    echo "❌ BLOCKED: Target path '${TARGET_PATH}' is outside workspace (matches ${prefix})." >&2
    exit 1
  fi
done

if [[ "$TARGET_PATH" != "${REPO_ROOT}"* ]]; then
  echo "❌ BLOCKED: Target path '${TARGET_PATH}' is outside monorepo root '${REPO_ROOT}'." >&2
  exit 1
fi

# ── Guard: Archive existing file (RULE 00) ───────────────────
if [[ -f "$TARGET_PATH" ]]; then
  if [[ "$FORCE" == "false" ]]; then
    echo "❌ File exists: ${TARGET_PATH}" >&2
    echo "   Use --force to archive and overwrite." >&2
    exit 1
  fi

  ARCHIVE_DIR="${REPO_ROOT}/_archive_safe_${TIMESTAMP}"
  mkdir -p "$ARCHIVE_DIR"
  REL_PATH="${TARGET_PATH#"${REPO_ROOT}/"}"
  ARCHIVE_TARGET="${ARCHIVE_DIR}/${REL_PATH}"
  mkdir -p "$(dirname "$ARCHIVE_TARGET")"
  cp "$TARGET_PATH" "$ARCHIVE_TARGET"
  echo "📦 Archived: ${REL_PATH} → _archive_safe_${TIMESTAMP}/${REL_PATH}" >&2
fi

# ── Create parent directories ────────────────────────────────
mkdir -p "$(dirname "$TARGET_PATH")"

# ── Write content ────────────────────────────────────────────
if [[ "$USE_STDIN" == "true" ]]; then
  cat > "$TARGET_PATH"
else
  if [[ ! -f "$CONTENT_FILE" ]]; then
    echo "❌ Content file not found: ${CONTENT_FILE}" >&2
    exit 1
  fi
  cp "$CONTENT_FILE" "$TARGET_PATH"
fi

REL_PATH="${TARGET_PATH#"${REPO_ROOT}/"}"
echo "✅ Written: ${REL_PATH} ($(wc -c < "$TARGET_PATH" | tr -d ' ') bytes)" >&2
