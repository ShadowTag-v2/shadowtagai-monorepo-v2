#!/usr/bin/env bash
# Weekly compliance copy scanner
# Scans production source for banned compliance phrases
# Schedule: cron/launchd weekly (item #21)
set -euo pipefail

MONOREPO_ROOT="${MONOREPO_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"

BANNED_PHRASES=(
  "SOC 2 Type II certified"
  "SOC 2 Type II ready"
  "HIPAA compliant"
  "HIPAA certified"
  "HIPAA-adjacent"
  "fully compliant"
  "certified infrastructure"
  "SOC 2 reports"
)

SCAN_DIRS=(
  "$MONOREPO_ROOT/apps/kovelai/site"
  "$MONOREPO_ROOT/apps/kovelai/components"
  "$MONOREPO_ROOT/apps/kovelai/app"
  "$MONOREPO_ROOT/apps/kovelai/public-v1-archive"
  "$MONOREPO_ROOT/apps/counselconduit"
)

VIOLATIONS=0

for phrase in "${BANNED_PHRASES[@]}"; do
  for dir in "${SCAN_DIRS[@]}"; do
    if [ -d "$dir" ]; then
      HITS=$(grep -rn "$phrase" "$dir" --include="*.html" --include="*.tsx" --include="*.ts" --include="*.mdx" --include="*.md" --exclude-dir=node_modules --exclude-dir=.next --exclude-dir=dist 2>/dev/null || true)
      if [ -n "$HITS" ]; then
        echo "❌ VIOLATION: '$phrase' found:"
        echo "$HITS"
        VIOLATIONS=$((VIOLATIONS + 1))
      fi
    fi
  done
done

if [ "$VIOLATIONS" -eq 0 ]; then
  echo "✅ Compliance copy scan PASSED — 0 banned phrases found ($(date -u +%Y-%m-%dT%H:%M:%SZ))"
else
  echo "❌ Compliance copy scan FAILED — $VIOLATIONS violations found ($(date -u +%Y-%m-%dT%H:%M:%SZ))"
  exit 1
fi
