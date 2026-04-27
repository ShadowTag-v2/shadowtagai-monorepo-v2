#!/usr/bin/env bash
# classify-upload-payload.sh — Two-Lane Upload Classifier
# Reads upload_policy.yaml and classifies staged/specified files
# into git_source vs artifact_archive lanes.
#
# Usage:
#   scripts/classify-upload-payload.sh                    # classify staged files
#   scripts/classify-upload-payload.sh --all               # classify all tracked files
#   scripts/classify-upload-payload.sh --path path/to/file # classify specific file
#   scripts/classify-upload-payload.sh --json              # output JSON
#
# Exit codes:
#   0 = all files classified, no violations
#   1 = violations found (forbidden files staged)
#   2 = configuration error
#
# Referenced by: upload_policy.yaml, push-with-app-gates.sh, invariant #103

set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")/.." rev-parse --show-toplevel)"
POLICY_FILE="${REPO_ROOT}/upload_policy.yaml"
OUTPUT_JSON="${1:-false}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# --- Parse arguments ---
MODE="staged"
TARGET_PATH=""
JSON_OUTPUT=false
for arg in "$@"; do
  case "$arg" in
    --all) MODE="all" ;;
    --json) JSON_OUTPUT=true ;;
    --path)
      MODE="path"
      shift
      TARGET_PATH="${1:-}"
      ;;
  esac
done

# --- Verify policy file exists ---
if [[ ! -f "$POLICY_FILE" ]]; then
  echo -e "${RED}ERROR: upload_policy.yaml not found at ${POLICY_FILE}${NC}" >&2
  exit 2
fi

# --- Collect files to classify ---
declare -a FILES=()
case "$MODE" in
  staged)
    while IFS= read -r f; do
      [[ -n "$f" ]] && FILES+=("$f")
    done < <(git -C "$REPO_ROOT" diff --cached --name-only --diff-filter=ACMR 2>/dev/null)
    if [[ ${#FILES[@]} -eq 0 ]]; then
      # Fallback: check unstaged modified + untracked
      while IFS= read -r f; do
        [[ -n "$f" ]] && FILES+=("$f")
      done < <(git -C "$REPO_ROOT" diff --name-only --diff-filter=ACMR 2>/dev/null)
    fi
    ;;
  all)
    while IFS= read -r f; do
      [[ -n "$f" ]] && FILES+=("$f")
    done < <(git -C "$REPO_ROOT" ls-files 2>/dev/null)
    ;;
  path)
    if [[ -n "$TARGET_PATH" ]]; then
      FILES+=("$TARGET_PATH")
    fi
    ;;
esac

if [[ ${#FILES[@]} -eq 0 ]]; then
  if $JSON_OUTPUT; then
    echo '{"status":"empty","files":[],"violations":[],"summary":{"total":0,"git_source":0,"artifact_archive":0,"forbidden":0}}'
  else
    echo -e "${GREEN}No files to classify.${NC}"
  fi
  exit 0
fi

# --- Forbidden path patterns (from upload_policy.yaml) ---
FORBIDDEN_PATHS=(
  "archive/"
  "external_repos/"
  "external_sdks/"
  "reference_architectures/raw/"
  "third_party/raw/"
  "venv/"
  ".venv/"
  ".venv-"
  "node_modules/"
  ".gitnexus/"
  ".mypy_cache/"
  ".ruff_cache/"
  ".pytest_cache/"
  "dist/"
  "build/"
  "out/"
  ".next/"
  ".turbo/"
  "__pycache__/"
)

# Forbidden extensions
FORBIDDEN_EXTS=(
  ".zip" ".tar" ".tar.gz" ".tgz" ".7z" ".dmg" ".iso"
  ".mp4" ".mov" ".onnx" ".pt" ".gguf" ".bin" ".weights"
  ".safetensors" ".pkl" ".heapsnapshot"
)

# Secret file patterns
SECRET_PATTERNS=(
  ".env" "*.pem" "*.key" "client_secret" "service-account"
)

# --- Size thresholds (MiB) ---
WARN_SIZE_MIB=50
BLOCK_SIZE_MIB=95
WARN_SIZE_BYTES=$((WARN_SIZE_MIB * 1024 * 1024))
BLOCK_SIZE_BYTES=$((BLOCK_SIZE_MIB * 1024 * 1024))

# --- Classification ---
declare -a GIT_SOURCE=()
declare -a ARTIFACT_ARCHIVE=()
declare -a FORBIDDEN=()
declare -a SIZE_WARNINGS=()
declare -a SIZE_BLOCKS=()

classify_file() {
  local file="$1"

  # Check forbidden paths
  for pattern in "${FORBIDDEN_PATHS[@]}"; do
    if [[ "$file" == "$pattern"* || "$file" == *"/$pattern"* ]]; then
      FORBIDDEN+=("$file:forbidden_path:$pattern")
      return
    fi
  done

  # Check forbidden extensions
  local ext=""
  case "$file" in
    *.tar.gz) ext=".tar.gz" ;;
    *.*) ext=".${file##*.}" ;;
  esac
  for fext in "${FORBIDDEN_EXTS[@]}"; do
    if [[ "$ext" == "$fext" ]]; then
      FORBIDDEN+=("$file:forbidden_extension:$fext")
      return
    fi
  done

  # Check secret patterns
  local basename
  basename="$(basename "$file")"
  for spat in "${SECRET_PATTERNS[@]}"; do
    case "$basename" in
      ${spat}*|*${spat}*)
        FORBIDDEN+=("$file:secret_pattern:$spat")
        return
        ;;
    esac
  done

  # Check file size if file exists on disk
  local full_path="${REPO_ROOT}/${file}"
  if [[ -f "$full_path" ]]; then
    local size
    size=$(stat -f%z "$full_path" 2>/dev/null || stat --printf="%s" "$full_path" 2>/dev/null || echo 0)
    if [[ "$size" -ge "$BLOCK_SIZE_BYTES" ]]; then
      SIZE_BLOCKS+=("$file:${size}")
      ARTIFACT_ARCHIVE+=("$file:size_exceeds_block")
      return
    elif [[ "$size" -ge "$WARN_SIZE_BYTES" ]]; then
      SIZE_WARNINGS+=("$file:${size}")
    fi
  fi

  # Passed all checks — classify as git_source
  GIT_SOURCE+=("$file")
}

for f in "${FILES[@]}"; do
  classify_file "$f"
done

# --- Output ---
TOTAL=${#FILES[@]}
GIT_COUNT=${#GIT_SOURCE[@]}
ARTIFACT_COUNT=${#ARTIFACT_ARCHIVE[@]}
FORBIDDEN_COUNT=${#FORBIDDEN[@]}
WARN_COUNT=${#SIZE_WARNINGS[@]}
BLOCK_COUNT=${#SIZE_BLOCKS[@]}

if $JSON_OUTPUT; then
  # Build JSON arrays
  git_json="["
  for i in "${!GIT_SOURCE[@]}"; do
    [[ $i -gt 0 ]] && git_json+=","
    git_json+="\"${GIT_SOURCE[$i]}\""
  done
  git_json+="]"

  forbidden_json="["
  for i in "${!FORBIDDEN[@]}"; do
    [[ $i -gt 0 ]] && forbidden_json+=","
    forbidden_json+="\"${FORBIDDEN[$i]}\""
  done
  forbidden_json+="]"

  warn_json="["
  for i in "${!SIZE_WARNINGS[@]}"; do
    [[ $i -gt 0 ]] && warn_json+=","
    warn_json+="\"${SIZE_WARNINGS[$i]}\""
  done
  warn_json+="]"

  cat <<EOF
{
  "status": "$([ $FORBIDDEN_COUNT -eq 0 ] && echo 'clean' || echo 'violations_found')",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "files_classified": $TOTAL,
  "git_source": $git_json,
  "artifact_archive": [],
  "forbidden": $forbidden_json,
  "size_warnings": $warn_json,
  "summary": {
    "total": $TOTAL,
    "git_source": $GIT_COUNT,
    "artifact_archive": $ARTIFACT_COUNT,
    "forbidden": $FORBIDDEN_COUNT,
    "size_warnings": $WARN_COUNT,
    "size_blocks": $BLOCK_COUNT
  }
}
EOF
else
  echo -e "${CYAN}═══ Upload Payload Classification ═══${NC}"
  echo -e "  Total files: ${TOTAL}"
  echo -e "  ${GREEN}Git Source:${NC} ${GIT_COUNT}"
  echo -e "  ${YELLOW}Artifact Archive:${NC} ${ARTIFACT_COUNT}"
  echo -e "  ${RED}Forbidden:${NC} ${FORBIDDEN_COUNT}"
  echo ""

  if [[ $FORBIDDEN_COUNT -gt 0 ]]; then
    echo -e "${RED}⛔ FORBIDDEN FILES DETECTED:${NC}"
    for v in "${FORBIDDEN[@]}"; do
      echo -e "  ${RED}✗${NC} $v"
    done
    echo ""
  fi

  if [[ $WARN_COUNT -gt 0 ]]; then
    echo -e "${YELLOW}⚠ SIZE WARNINGS (>${WARN_SIZE_MIB}MiB):${NC}"
    for w in "${SIZE_WARNINGS[@]}"; do
      local fpath="${w%%:*}"
      local fsize="${w##*:}"
      echo -e "  ${YELLOW}!${NC} ${fpath} ($(( fsize / 1024 / 1024 ))MiB)"
    done
    echo ""
  fi

  if [[ $BLOCK_COUNT -gt 0 ]]; then
    echo -e "${RED}🚫 SIZE BLOCKS (>${BLOCK_SIZE_MIB}MiB):${NC}"
    for b in "${SIZE_BLOCKS[@]}"; do
      echo -e "  ${RED}✗${NC} $b"
    done
    echo ""
  fi
fi

# Exit with violation status
if [[ $FORBIDDEN_COUNT -gt 0 || $BLOCK_COUNT -gt 0 ]]; then
  exit 1
fi
exit 0
