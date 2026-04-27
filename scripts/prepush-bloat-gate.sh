#!/usr/bin/env bash
# scripts/prepush-bloat-gate.sh — Pre-push hook to reject bloated commits
# Prevents files > 10MB and banned binary extensions from entering the repo.
# Install: ln -sf ../../scripts/prepush-bloat-gate.sh .git/hooks/pre-push
#
# Part of: Wave 0 Governance (migration_manifest.yaml)
# Created: 2026-04-27

set -euo pipefail

readonly MAX_FILE_SIZE_BYTES=$((10 * 1024 * 1024))  # 10 MB
readonly MAX_FILE_SIZE_HUMAN="10 MB"

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
  "archive/"
)

errors=0
warnings=0

echo "🔒 Pre-push bloat gate running..."

# Parse the refspec range from stdin (git pre-push protocol)
# Format: <local_ref> <local_sha> <remote_ref> <remote_sha>
DIFF_RANGE=""
while read -r local_ref local_sha remote_ref remote_sha; do
  if [[ "$remote_sha" == "0000000000000000000000000000000000000000" ]]; then
    # New branch — check all commits against default branch
    DIFF_RANGE="origin/main..${local_sha}"
  elif [[ "$local_sha" == "0000000000000000000000000000000000000000" ]]; then
    # Deleting branch — nothing to check
    continue
  else
    # Regular push — check only the commits being pushed
    DIFF_RANGE="${remote_sha}..${local_sha}"
  fi
done

if [[ -z "$DIFF_RANGE" ]]; then
  echo "✅ Nothing to push — bloat gate skipped."
  exit 0
fi

echo "   Scanning range: $DIFF_RANGE"

# Check 1: Large files in the commits being pushed
while IFS= read -r -d $'\0' file; do
  if [[ -f "$file" ]]; then
    size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo 0)
    if (( size > MAX_FILE_SIZE_BYTES )); then
      human_size=$(numfmt --to=iec "$size" 2>/dev/null || echo "${size} bytes")
      echo "❌ BLOCKED: $file ($human_size > $MAX_FILE_SIZE_HUMAN)"
      ((errors++))
    fi
  fi
done < <(git diff --name-only -z "$DIFF_RANGE" 2>/dev/null)

# Check 2: Banned extensions
while IFS= read -r file; do
  ext=".${file##*.}"
  ext_lower=$(echo "$ext" | tr '[:upper:]' '[:lower:]')
  for banned in "${BANNED_EXTENSIONS[@]}"; do
    if [[ "$ext_lower" == "$banned" ]]; then
      echo "❌ BLOCKED: $file (banned extension: $banned)"
      ((errors++))
      break
    fi
  done
done < <(git diff --name-only "$DIFF_RANGE" 2>/dev/null)

# Check 3: Banned directories
while IFS= read -r file; do
  for banned_dir in "${BANNED_DIRS[@]}"; do
    if [[ "$file" == *"$banned_dir"* ]]; then
      echo "❌ BLOCKED: $file (banned directory: $banned_dir)"
      ((errors++))
      break
    fi
  done
done < <(git diff --name-only "$DIFF_RANGE" 2>/dev/null)

# Check 4: Total commit size (warn at 50MB)
total_size=0
while IFS= read -r -d $'\0' file; do
  if [[ -f "$file" ]]; then
    size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo 0)
    ((total_size += size)) || true
  fi
done < <(git diff --name-only -z "$DIFF_RANGE" 2>/dev/null)

if (( total_size > 50 * 1024 * 1024 )); then
  human_total=$(numfmt --to=iec "$total_size" 2>/dev/null || echo "${total_size} bytes")
  echo "⚠️  WARNING: Total commit size is $human_total (> 50 MB)"
  ((warnings++))
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
