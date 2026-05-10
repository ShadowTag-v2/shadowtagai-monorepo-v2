#!/usr/bin/env bash
set -euo pipefail
echo "🔍 Pre-push Bloat Gate (TACSOP 5)"
# Check for files >95MB tracked
large_files=$(git ls-files -z | xargs -0 du -h 2>/dev/null | awk '$1 ~ /[0-9]+M/ && $1+0 > 95' || true)
if [ -n "$large_files" ]; then
  echo "❌ BLOCKED: Tracked files over 95MB detected:"
  echo "$large_files"
  exit 1
fi
echo "✅ No oversized tracked files."
# Add more: LFS check, secret scan already in workflow
exit 0
