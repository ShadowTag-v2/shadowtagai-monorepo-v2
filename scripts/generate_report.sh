#!/usr/bin/env bash
# Generate markdown summary of all repos in apps/ShadowTag-v2_stack/
set -euo pipefail
MONOREPO=/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball
STACK_DIR="$MONOREPO/apps/ShadowTag-v2_stack"
OUTPUT="$MONOREPO/docs/ShadowTag-v2_stack_report.md"

echo "# ShadowTag-v2 Stack Report" > "$OUTPUT"
echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$OUTPUT"
echo "" >> "$OUTPUT"

if [ ! -d "$STACK_DIR" ]; then
    echo "ERROR: $STACK_DIR not found" | tee -a "$OUTPUT"
    exit 1
fi

echo "## Repos in apps/ShadowTag-v2_stack/" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo "| Repo | Size | Files | Has package.json | Has Dockerfile |" >> "$OUTPUT"
echo "|------|------|-------|-----------------|----------------|" >> "$OUTPUT"

for dir in "$STACK_DIR"/*/; do
    if [ -d "$dir" ]; then
        name=$(basename "$dir")
        size=$(du -sh "$dir" 2>/dev/null | cut -f1)
        filecount=$(find "$dir" -type f 2>/dev/null | wc -l | tr -d ' ')
        has_pkg="No"
        has_docker="No"
        [ -f "$dir/package.json" ] && has_pkg="Yes"
        [ -f "$dir/Dockerfile" ] && has_docker="Yes"
        echo "| $name | $size | $filecount | $has_pkg | $has_docker |" >> "$OUTPUT"
    fi
done

echo "" >> "$OUTPUT"
echo "## Summary" >> "$OUTPUT"
total=$(ls -d "$STACK_DIR"/*/ 2>/dev/null | wc -l | tr -d ' ')
echo "- Total repos: $total" >> "$OUTPUT"
echo "- Stack directory: $STACK_DIR" >> "$OUTPUT"

echo "Report written to: $OUTPUT"
cat "$OUTPUT"
