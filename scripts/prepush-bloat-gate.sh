#!/usr/bin/env bash
# scripts/prepush-bloat-gate.sh — Pre-push hook to reject bloated commits
# Prevents files > 10MB and banned binary extensions from entering the repo.
# Install: ln -sf ../../scripts/prepush-bloat-gate.sh .git/hooks/pre-push
#
# Part of: Wave 0 Governance (migration_manifest.yaml)
# Created: 2026-04-27
# Updated: 2026-04-28 — Single-pass optimization, portable stat, CI --fast mode

set -euo pipefail

readonly MAX_FILE_SIZE_BYTES=$((10 * 1024 * 1024))  # 10 MB
readonly MAX_FILE_SIZE_HUMAN="10 MB"

# Portable file size helper (macOS uses -f%z, Linux uses -c%s)
_filesize() {
  stat -f%z "$1" 2>/dev/null || stat -c%s "$1" 2>/dev/null || echo 0
}

# Binary extensions that must NEVER be committed directly
readonly BANNED_EXTENSIONS=(
  ".exe" ".dll" ".so" ".dylib" ".a" ".lib"
  ".jar" ".war" ".class"
  ".o" ".obj" ".pyc" ".pyo"
  ".gz" ".tar" ".zip" ".rar" ".7z" ".bz2" ".xz"
  ".iso" ".dmg" ".pkg" ".deb" ".rpm"
  ".gguf" ".safetensors" ".model" ".onnx" ".bin"
  ".sqlite" ".db" ".sqlite3"
  ".heapsnapshot"
  ".psd" ".ai" ".sketch" ".fig"
  ".mp4" ".mov" ".avi" ".webm" ".mkv"
  ".wav" ".mp3" ".flac" ".aac"
  ".woff" ".woff2" ".ttf" ".otf" ".eot"
  ".heic" ".heif"
)

# Directories that must NEVER be committed
readonly BANNED_DIRS=(
  "node_modules/"
  "venv/"
  ".venv/"
  "__pycache__/"
  ".mypy_cache/"
  ".gitnexus/"
  "target/"        # Rust/Java build output
  ".next/"         # Next.js build cache
  "dist/"          # Generic build output (allow via explicit override)
  ".scannerwork/"
  ".tmp.driveupload/"
  # NOTE: "archive/" removed — legitimate organizational pattern for docs/reference repos
)

errors=0
warnings=0

CHECK_MODE=false
FAST_MODE=false
for arg in "$@"; do
  case "$arg" in
    --check) CHECK_MODE=true ;;
    --fast)  FAST_MODE=true; CHECK_MODE=true ;;
  esac
done

# Build a regex pattern for banned extensions (for speed)
_build_ext_set() {
  local s=""
  for ext in "${BANNED_EXTENSIONS[@]}"; do
    s="${s}|${ext}"
  done
  echo "${s:1}"  # strip leading |
}
BANNED_EXT_PATTERN=$(_build_ext_set)

# Load allowlist (pre-existing files that predate the bloat gate)
ALLOWLIST=()
ALLOWLIST_FILE="${REPO_ROOT:-.}/.bloat-allowlist"
if [[ -f "$ALLOWLIST_FILE" ]]; then
  while IFS= read -r line; do
    # Skip comments and blank lines
    line="${line%%#*}"
    line="$(echo "$line" | xargs 2>/dev/null || true)"
    [[ -z "$line" ]] && continue
    ALLOWLIST+=("$line")
  done < "$ALLOWLIST_FILE"
fi

_is_allowlisted() {
  local file="$1"
  for pattern in "${ALLOWLIST[@]}"; do
    if [[ "$file" == "$pattern"* ]]; then
      return 0
    fi
  done
  return 1
}

echo "🔒 Pre-push bloat gate running..."

if $CHECK_MODE; then
  # ── Check Mode: Single-pass scan of tracked files ──
  # Used by release-readiness-gate.sh and CI (no stdin, no git pre-push protocol)
  if $FAST_MODE; then
    echo "   Mode: Fast working tree scan (--fast, no size checks)"
  else
    echo "   Mode: Working tree scan (--check)"
  fi

  while IFS= read -r file; do
    # Skip allowlisted pre-existing files
    _is_allowlisted "$file" && continue

    # Check 1: Banned directories
    dir_blocked=false
    for banned_dir in "${BANNED_DIRS[@]}"; do
      if [[ "$file" == *"$banned_dir"* ]]; then
        echo "❌ BLOCKED: $file (banned directory: $banned_dir)"
        errors=$((errors + 1))
        dir_blocked=true
        break
      fi
    done
    # Skip further checks if directory is already banned
    $dir_blocked && continue

    # Check 2: Banned extensions
    ext=".${file##*.}"
    ext_lower=$(echo "$ext" | tr '[:upper:]' '[:lower:]')
    for banned in "${BANNED_EXTENSIONS[@]}"; do
      if [[ "$ext_lower" == "$banned" ]]; then
        echo "❌ BLOCKED: $file (banned extension: $banned)"
        errors=$((errors + 1))
        break
      fi
    done

    # Check 3: File size (skip in --fast mode)
    if ! $FAST_MODE && [[ -f "$file" ]]; then
      size=$(_filesize "$file")
      if (( size > MAX_FILE_SIZE_BYTES )); then
        human_size=$(numfmt --to=iec "$size" 2>/dev/null || echo "${size} bytes")
        echo "❌ BLOCKED: $file ($human_size > $MAX_FILE_SIZE_HUMAN)"
        errors=$((errors + 1))
      fi
    fi
  done < <(git ls-files 2>/dev/null)

else
  # ── Hook Mode: Parse git pre-push protocol from stdin ──
  # Format: <local_ref> <local_sha> <remote_ref> <remote_sha>
  DIFF_RANGE=""
  while read -r local_ref local_sha remote_ref remote_sha; do
    if [[ "$remote_sha" == "0000000000000000000000000000000000000000" ]]; then
      DIFF_RANGE="origin/main..${local_sha}"
    elif [[ "$local_sha" == "0000000000000000000000000000000000000000" ]]; then
      continue
    else
      DIFF_RANGE="${remote_sha}..${local_sha}"
    fi
  done

  if [[ -z "$DIFF_RANGE" ]]; then
    echo "✅ Nothing to push — bloat gate skipped."
    exit 0
  fi

  echo "   Scanning range: $DIFF_RANGE"

  # Single-pass check of all files in the diff range
  while IFS= read -r file; do
    # Check 1: Banned directories
    dir_blocked=false
    for banned_dir in "${BANNED_DIRS[@]}"; do
      if [[ "$file" == *"$banned_dir"* ]]; then
        echo "❌ BLOCKED: $file (banned directory: $banned_dir)"
        errors=$((errors + 1))
        dir_blocked=true
        break
      fi
    done
    $dir_blocked && continue

    # Check 2: Banned extensions
    ext=".${file##*.}"
    ext_lower=$(echo "$ext" | tr '[:upper:]' '[:lower:]')
    for banned in "${BANNED_EXTENSIONS[@]}"; do
      if [[ "$ext_lower" == "$banned" ]]; then
        echo "❌ BLOCKED: $file (banned extension: $banned)"
        errors=$((errors + 1))
        break
      fi
    done

    # Check 3: File size
    if [[ -f "$file" ]]; then
      size=$(_filesize "$file")
      if (( size > MAX_FILE_SIZE_BYTES )); then
        human_size=$(numfmt --to=iec "$size" 2>/dev/null || echo "${size} bytes")
        echo "❌ BLOCKED: $file ($human_size > $MAX_FILE_SIZE_HUMAN)"
        errors=$((errors + 1))
      fi
    fi
  done < <(git diff --name-only "$DIFF_RANGE" 2>/dev/null)

  # Check 4: Total commit size (warn at 50MB)
  total_size=0
  while IFS= read -r -d $'\0' file; do
    if [[ -f "$file" ]]; then
      size=$(_filesize "$file")
      ((total_size += size)) || true
    fi
  done < <(git diff --name-only -z "$DIFF_RANGE" 2>/dev/null)

  if (( total_size > 50 * 1024 * 1024 )); then
    human_total=$(numfmt --to=iec "$total_size" 2>/dev/null || echo "${total_size} bytes")
    echo "⚠️  WARNING: Total commit size is $human_total (> 50 MB)"
    warnings=$((warnings + 1))
  fi
fi

if (( errors > 0 )); then
  echo ""
  echo "🚫 Push REJECTED: $errors bloat violation(s) detected."
  echo "   Fix the violations above, then try again."
  echo "   To bypass (EMERGENCY ONLY): git push --no-verify"
  exit 1
fi

if (( warnings > 0 )); then
  echo "⚠️  $warnings warning(s) — push proceeding."
fi

echo "✅ Bloat gate passed."
exit 0
