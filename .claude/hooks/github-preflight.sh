#!/usr/bin/env bash
# .claude/hooks/github-preflight.sh
# Pre-tool-use hook: Injects GitHub state context before file writes.
# Called by PreToolUse hook on Write|Edit|Bash patterns.

set -euo pipefail

# Only run for significant tool calls (skip reads)
TOOL_NAME="${CLAUDE_TOOL_NAME:-}"
if [[ "$TOOL_NAME" == "Read" ]] || [[ "$TOOL_NAME" == "" ]]; then
    exit 0
fi

# Quick GitHub state snapshot (cached for 5 minutes)
CACHE_FILE="/tmp/.claude-github-preflight-cache"
CACHE_TTL=300  # 5 minutes

if [[ -f "$CACHE_FILE" ]]; then
    CACHE_AGE=$(( $(date +%s) - $(stat -f %m "$CACHE_FILE" 2>/dev/null || echo 0) ))
    if [[ $CACHE_AGE -lt $CACHE_TTL ]]; then
        cat "$CACHE_FILE"
        exit 0
    fi
fi

# Build fresh context
{
    echo "--- GitHub Context (auto-injected) ---"

    # Current branch + sync status
    BRANCH=$(git branch --show-current 2>/dev/null || echo "detached")
    AHEAD_BEHIND=$(git rev-list --left-right --count origin/"$BRANCH"...HEAD 2>/dev/null || echo "?	?")
    echo "Branch: $BRANCH | Behind/Ahead: $AHEAD_BEHIND"

    # Uncommitted changes summary
    CHANGES=$(git diff --stat HEAD 2>/dev/null | tail -1)
    if [[ -n "$CHANGES" ]]; then
        echo "Uncommitted: $CHANGES"
    fi

    # Latest CI status (if gh CLI available)
    if command -v gh &>/dev/null; then
        CI_STATUS=$(gh run list --limit 1 --json status,conclusion,name -q '.[0] | "\(.name): \(.status)/\(.conclusion // "pending")"' 2>/dev/null || echo "CI: unavailable")
        echo "CI: $CI_STATUS"

        # Open PRs touching current branch
        PR_COUNT=$(gh pr list --state open --head "$BRANCH" --json number -q 'length' 2>/dev/null || echo "?")
        echo "Open PRs for this branch: $PR_COUNT"
    fi

    echo "--- End GitHub Context ---"
} > "$CACHE_FILE" 2>/dev/null

cat "$CACHE_FILE" 2>/dev/null || true
