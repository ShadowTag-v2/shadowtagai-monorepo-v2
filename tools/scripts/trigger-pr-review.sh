#!/bin/bash
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
# Jules + GCA Sovereign PR Review — Trigger Script
set -euo pipefail

PR_NUMBER=$1
BRANCH=${2:-"main"}
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo "🚀 [Jules] Deploying Antigravity PR Review Swarm to PR #$PR_NUMBER"

# 1. Ensure GitHub App token exists
if [ ! -f /tmp/gh_app_token.txt ]; then
  echo "  Generating GitHub App token..."
  python3 "$REPO_ROOT/scripts/auth_github_app.py" --export
fi

# 2. Run Jules Orchestrator + GCA Swarm
python3 "$REPO_ROOT/tools/scripts/run_swarm.py" \
  --pr-number "$PR_NUMBER" \
  --branch "$BRANCH" \
  --mode="full-review"

# 3. Run AST Surgery auto-fix
if command -v bun &> /dev/null; then
  echo "  Running AST Surgery..."
  bun run "$REPO_ROOT/scripts/ast_surgery.ts" --auto-fix 2>/dev/null || true
else
  echo "  ⚠️ Bun not available — skipping AST Surgery"
fi

# 4. Post verified findings to GitHub
python3 "$REPO_ROOT/tools/scripts/post_pr_findings.py" --pr "$PR_NUMBER"

echo "✅ [Jules] PR Review Swarm completed for #$PR_NUMBER"
