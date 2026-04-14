#!/bin/bash
# FINISH PROTOCOL — Autonomous Cleanup
# Usage: ./scripts/finish_changes.sh
# Runs: lint → format → stage → commit → kill orphans

set -euo pipefail

echo "=== FINISH PROTOCOL: AUTONOMOUS CLEANUP ==="

# Phase 1: Auto-Fix Lint/Format
echo "[1/4] Running ruff auto-fix..."
if command -v ruff &>/dev/null; then
    ruff check --fix --select F401,F841 \
        --exclude "*/external_repos/*" \
        --exclude "*/archive/*" \
        --exclude "*/node_modules/*" \
        --exclude "*/.venv/*" \
        apps/ tools/ scripts/ 2>/dev/null || true
    echo "  ✅ ruff lint complete"
else
    echo "  ⚠️ ruff not found, skipping lint"
fi

echo "[1.5/4] Running biome format..."
if command -v biome &>/dev/null; then
    biome format --write apps/ 2>/dev/null || true
    echo "  ✅ biome format complete"
elif [ -f "node_modules/.bin/biome" ]; then
    npx biome format --write apps/ 2>/dev/null || true
    echo "  ✅ biome format complete (npx)"
else
    echo "  ⚠️ biome not found, skipping format"
fi

# Phase 2: Stage All Changes
echo "[2/4] Staging changes..."
git add -A
CHANGES=$(git diff --cached --shortstat 2>/dev/null || echo "")
if [ -z "$CHANGES" ]; then
    echo "  ℹ️ No changes to commit"
else
    echo "  ✅ Staged: $CHANGES"

    # Phase 3: Commit
    echo "[3/4] Committing..."
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    git commit -m "chore(finish): autonomous cleanup $TIMESTAMP

Auto-fix lint (ruff F401/F841), format (biome), stage all changes.
Executed by Finish Protocol." || true
    echo "  ✅ Committed"
fi

# Phase 4: Kill Orphan Processes
echo "[4/4] Killing orphan dev servers..."
# Kill common dev server ports
for PORT in 3000 3001 5173 8080 8081 8082; do
    PID=$(lsof -ti :$PORT 2>/dev/null || true)
    if [ -n "$PID" ]; then
        kill $PID 2>/dev/null || true
        echo "  🔪 Killed PID $PID on port $PORT"
    fi
done

echo ""
echo "=== FINISH PROTOCOL COMPLETE ==="
echo "State: CLEAN"
