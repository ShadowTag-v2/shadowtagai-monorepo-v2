#!/bin/bash
# V23 Task 9: Archive deprecated legacy test suites
# Moves Python/Node.js test files to _archived_legacy/
# Preserves the active Bun test suite and Python speculation engine tests

set -e

ARCHIVE_DIR="tests/_archived_legacy"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "⚡ [V23] Archiving deprecated test suites..."
mkdir -p "$ARCHIVE_DIR"

# Archive only explicitly deprecated test files
# DO NOT archive active test suites:
#   - tests/semantic_routing.test.ts (V23 Bun active)
#   - tests/gemini_bridge.spec.ts (V23 Bun active)
#   - tests/test_semantic_classify.py (V22 Python active)
#   - tests/test_speculation_engine_modules.py (V22 Python active)
#   - tests/test_exit_plan_mode_integration.py (V22 Python active)

DEPRECATED_PATTERNS=(
  "tests/*.test.js"      # Legacy Node.js tests
  "tests/*.spec.js"      # Legacy Node.js specs
)

ARCHIVED_COUNT=0
for pattern in "${DEPRECATED_PATTERNS[@]}"; do
  for file in $pattern; do
    if [ -f "$file" ]; then
      mv "$file" "$ARCHIVE_DIR/"
      ARCHIVED_COUNT=$((ARCHIVED_COUNT + 1))
      echo "  → Archived: $file"
    fi
  done
done

echo "✅ Archived $ARCHIVED_COUNT deprecated test files to $ARCHIVE_DIR/"
echo "   Active test suites preserved (Bun + Python speculation engine)."
