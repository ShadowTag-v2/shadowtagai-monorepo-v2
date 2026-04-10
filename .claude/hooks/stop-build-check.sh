#!/bin/bash
# Stop Build Check Hook
# Runs quality checks after Claude finishes a response

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "🔍 Running quality checks..."
echo "=============================="

ERROR_COUNT=0
ERRORS_FILE=$(mktemp)

# 1. Type checking with mypy
echo "📝 Type checking (mypy)..."
if ! mypy src/ 2>&1 | tee -a "$ERRORS_FILE"; then
    MYPY_ERRORS=$(grep -c "error:" "$ERRORS_FILE" || echo "0")
    ERROR_COUNT=$((ERROR_COUNT + MYPY_ERRORS))
fi

# 2. Linting with ruff
echo ""
echo "🧹 Linting (ruff)..."
if ! ruff check . 2>&1 | tee -a "$ERRORS_FILE"; then
    RUFF_ERRORS=$(grep -c "error" "$ERRORS_FILE" || echo "0")
    ERROR_COUNT=$((ERROR_COUNT + RUFF_ERRORS))
fi

# 3. Quick test run (stop on first failure)
echo ""
echo "🧪 Running tests (pytest)..."
if ! pytest tests/ -x --tb=short 2>&1 | tee -a "$ERRORS_FILE"; then
    TEST_ERRORS=$(grep -c "FAILED" "$ERRORS_FILE" || echo "0")
    ERROR_COUNT=$((ERROR_COUNT + TEST_ERRORS))
fi

# Summary
echo ""
echo "=============================="
if [ "$ERROR_COUNT" -eq 0 ]; then
    echo "✅ All checks passed!"
elif [ "$ERROR_COUNT" -lt 5 ]; then
    echo "⚠️  Found $ERROR_COUNT error(s). Please review:"
    head -20 "$ERRORS_FILE"
else
    echo "❌ Found $ERROR_COUNT errors. Consider using:"
    echo "   /agent auto-error-resolver"
    echo ""
    echo "First 10 errors:"
    head -10 "$ERRORS_FILE"
fi

# Cleanup
rm -f "$ERRORS_FILE"

# Return success to not block Claude
exit 0
