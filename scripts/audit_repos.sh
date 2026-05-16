#!/usr/bin/env bash
# Audit all dirs under apps/ with their sizes
set -euo pipefail
MONOREPO=/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball

echo "=== Repo Size Audit: apps/ ==="
echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

if [ -d "$MONOREPO/apps" ]; then
    du -sh "$MONOREPO/apps"/*/  2>/dev/null | sort -hr | while IFS=$'\t' read -r size path; do
        dirname=$(basename "$path")
        echo "  $size  $dirname"
    done
    echo ""
    echo "=== Subdirs under apps/aiyou_stack/ ==="
    if [ -d "$MONOREPO/apps/aiyou_stack" ]; then
        du -sh "$MONOREPO/apps/aiyou_stack"/*/  2>/dev/null | sort -hr | while IFS=$'\t' read -r size path; do
            dirname=$(basename "$path")
            echo "  $size  $dirname"
        done
    else
        echo "  (apps/aiyou_stack not found)"
    fi
else
    echo "  (apps/ directory not found)"
fi
