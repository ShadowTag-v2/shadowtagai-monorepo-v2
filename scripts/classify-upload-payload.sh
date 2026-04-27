#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════
# scripts/classify-upload-payload.sh — Two-Lane Upload Classifier
# Invariant #111: Determines git lane vs artifact lane.
# ═══════════════════════════════════════════════════════════
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MAX_FILE_SIZE_MB=10
MAX_FILE_SIZE_BYTES=$((MAX_FILE_SIZE_MB * 1024 * 1024))
ERRORS=0

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "▸ Classifying staged files for upload lane..."

git -C "$REPO_ROOT" diff --cached --name-only --diff-filter=ACMR | while IFS= read -r file; do
  FULL_PATH="$REPO_ROOT/$file"
  [ -f "$FULL_PATH" ] || continue

  FILE_SIZE=$(stat -f%z "$FULL_PATH" 2>/dev/null || stat -c%s "$FULL_PATH" 2>/dev/null || echo 0)
  if [ "$FILE_SIZE" -gt "$MAX_FILE_SIZE_BYTES" ]; then
    SIZE_MB=$((FILE_SIZE / 1024 / 1024))
    printf "  ${RED}ARTIFACT LANE${NC}: %s (%dMB > %dMB limit)\n" "$file" "$SIZE_MB" "$MAX_FILE_SIZE_MB"
    ERRORS=$((ERRORS + 1))
  fi

  case "$file" in
    *.onnx|*.bin|*.weights|*.pt|*.h5|*.hdf5|*.sqlite|*.sqlite3|*.db)
      printf "  ${RED}ARTIFACT LANE${NC}: %s (binary/data file)\n" "$file"
      ERRORS=$((ERRORS + 1))
      ;;
    *.mp4|*.mp3|*.wav|*.heapsnapshot|*.cpuprofile)
      printf "  ${RED}ARTIFACT LANE${NC}: %s (media/profile file)\n" "$file"
      ERRORS=$((ERRORS + 1))
      ;;
    *.zip|*.tar.gz|*.tgz|*.tar|*.7z|*.rar)
      printf "  ${RED}ARTIFACT LANE${NC}: %s (archive file)\n" "$file"
      ERRORS=$((ERRORS + 1))
      ;;
    *)
      printf "  ${GREEN}GIT LANE${NC}: %s\n" "$file"
      ;;
  esac
done

if [ "$ERRORS" -gt 0 ]; then
  printf "\n${RED}BLOCKED${NC}: %d files belong in the artifact lane.\n" "$ERRORS"
  exit 1
fi

printf "\n${GREEN}All staged files classified for git lane.${NC}\n"
