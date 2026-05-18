#!/usr/bin/env bash
# trigger-pr-review.sh — Sovereign PR Review Orchestrator
# Replaces Anthropic Code Review ($15-25/PR) with local M1 Max verification.
#
# Usage:
#   ./tools/scripts/trigger-pr-review.sh <PR_NUMBER> [BRANCH]
#
# Architecture:
#   Tier 1: pytest fast path (<1ms) — pure logic verification
#   Tier 2: Colab T4 via Google Drive IPC — heavy compute
#   Tier 3: M1 Max ANE bare-metal — hardware constraint verification
#
# Auth: GitHub App PEM (App ID: 3018200)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PR_NUMBER="${1:?Usage: trigger-pr-review.sh <PR_NUMBER> [BRANCH]}"
BRANCH="${2:-}"

PEM_PATH="${SHADOWTAG_PEM:-/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem}"
APP_ID="3018200"
REPO="ShadowTag-v2/shadowtagai-monorepo-v2"

echo "╔══════════════════════════════════════════════════╗"
echo "║  🚀 Antigravity Sovereign PR Review Swarm        ║"
echo "║  PR #${PR_NUMBER} | Repo: ${REPO}               ║"
echo "╚══════════════════════════════════════════════════╝"

# ── Step 1: Resolve branch if not provided ──
if [ -z "$BRANCH" ]; then
  BRANCH=$(cd "$REPO_ROOT" && git log --format='%D' -1 2>/dev/null | grep -oE 'origin/[^ ,]+' | head -1 | sed 's|origin/||')
  echo "Auto-detected branch: $BRANCH"
fi

# ── Step 2: Fetch PR diff ──
echo ""
echo "📥 Fetching PR #${PR_NUMBER} diff..."
DIFF_FILE=$(mktemp /tmp/pr-${PR_NUMBER}-diff.XXXXXX)

cd "$REPO_ROOT"
python3 -c "
import jwt, time, json, urllib.request, sys

with open('${PEM_PATH}', 'rb') as f:
    key = f.read()

now = int(time.time())
tok = jwt.encode({'iat': now-60, 'exp': now+600, 'iss': '${APP_ID}'}, key, algorithm='RS256')

req = urllib.request.Request('https://api.github.com/app/installations',
    headers={'Authorization': f'Bearer {tok}', 'Accept': 'application/vnd.github+json'})
install_id = json.loads(urllib.request.urlopen(req).read())[0]['id']

req2 = urllib.request.Request(f'https://api.github.com/app/installations/{install_id}/access_tokens',
    method='POST', headers={'Authorization': f'Bearer {tok}', 'Accept': 'application/vnd.github+json'})
access_token = json.loads(urllib.request.urlopen(req2).read())['token']

req3 = urllib.request.Request(f'https://api.github.com/repos/${REPO}/pulls/${PR_NUMBER}',
    headers={'Authorization': f'token {access_token}', 'Accept': 'application/vnd.github.v3.diff'})
diff = urllib.request.urlopen(req3).read().decode()
with open('${DIFF_FILE}', 'w') as f:
    f.write(diff)
print(f'Diff saved: {len(diff)} bytes, {diff.count(chr(10))} lines')
"

# ── Step 3: Run the Swarm ──
echo ""
echo "🐝 Deploying verification swarm..."
python3 "${REPO_ROOT}/tools/scripts/run_swarm.py" \
  --pr "${PR_NUMBER}" \
  --diff "${DIFF_FILE}" \
  --repo-root "${REPO_ROOT}" \
  --repo "${REPO}" \
  --pem "${PEM_PATH}" \
  --app-id "${APP_ID}"

# ── Step 4: Cleanup ──
rm -f "${DIFF_FILE}"
echo ""
echo "✅ PR #${PR_NUMBER} review complete."
