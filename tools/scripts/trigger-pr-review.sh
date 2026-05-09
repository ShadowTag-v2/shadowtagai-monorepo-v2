#!/usr/bin/env bash
# trigger-pr-review.sh — Manual trigger for the Jules + GCA PR Review Swarm
# Usage: ./tools/scripts/trigger-pr-review.sh <PR_NUMBER> [--tier 1|2|3] [--auto-fix]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

PR_NUMBER="${1:-}"
TIER="${2:-}"
AUTO_FIX="${3:-}"

if [[ -z "$PR_NUMBER" ]]; then
  echo "❌ Usage: $0 <PR_NUMBER> [--tier 1|2|3] [--auto-fix]"
  exit 1
fi

# Parse optional flags
TIER_FLAG=""
FIX_FLAG=""
for arg in "$@"; do
  case "$arg" in
    --tier)
      shift
      TIER_FLAG="$1"
      ;;
    --auto-fix)
      FIX_FLAG="true"
      ;;
  esac
done

echo "╔══════════════════════════════════════════╗"
echo "║  Jules + GCA PR Review Swarm             ║"
echo "║  PR #${PR_NUMBER}                                  ║"
echo "╚══════════════════════════════════════════╝"

# Step 1: Run AST surgery (auto-fix) if requested
if [[ "$FIX_FLAG" == "true" ]]; then
  echo ""
  echo "[1/4] 🔧 Running AST surgery (auto-fix)..."
  cd "$REPO_ROOT"
  if command -v bun &>/dev/null; then
    bun run scripts/ast_surgery.ts
  else
    echo "⚠️  Bun not found — skipping AST surgery"
  fi
fi

# Step 2: Run the swarm orchestrator
echo ""
echo "[2/4] 🐝 Running swarm orchestrator..."
cd "$REPO_ROOT"
python3 tools/scripts/run_swarm.py \
  --pr "$PR_NUMBER" \
  ${TIER_FLAG:+--tier "$TIER_FLAG"}

# Step 3: Post findings to GitHub
echo ""
echo "[3/4] 📝 Posting findings to GitHub..."
python3 tools/scripts/post_pr_findings.py \
  --pr "$PR_NUMBER" \
  --findings-file "/tmp/swarm_findings_${PR_NUMBER}.json"

# Step 4: Summary
echo ""
echo "[4/4] ✅ Review complete for PR #${PR_NUMBER}"
echo ""
echo "View results: https://github.com/ShadowTag-v2/shadowtagai-monorepo-v2/pull/${PR_NUMBER}"
