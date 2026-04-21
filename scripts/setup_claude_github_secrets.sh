#!/usr/bin/env bash
# scripts/setup_claude_github_secrets.sh
# Sets GitHub Actions secrets for Claude Code Action workflows.
# REQUIRES: gh CLI authenticated with admin access (not App token).
# Run: gh auth login --web  → then run this script.

set -euo pipefail

REPO="ShadowTag-v2/Monorepo-Uphillsnowball"
PROJECT_NUMBER="767252945109"

echo "🔧 Setting Claude Code Action GitHub Secrets..."
echo "================================================"
echo ""
echo "IMPORTANT: You must be authenticated via 'gh auth login --web'"
echo "           (GitHub App tokens lack admin:secrets scope)"
echo ""

# 1. GCP Workload Identity Provider
WIF_PROVIDER="projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github-pool/providers/github-provider"
echo "Setting GCP_WORKLOAD_IDENTITY_PROVIDER..."
echo "$WIF_PROVIDER" | gh secret set GCP_WORKLOAD_IDENTITY_PROVIDER --repo "$REPO"

# 2. GCP Service Account
SA_EMAIL="claude-code-action@shadowtag-omega-v4.iam.gserviceaccount.com"
echo "Setting GCP_SERVICE_ACCOUNT..."
echo "$SA_EMAIL" | gh secret set GCP_SERVICE_ACCOUNT --repo "$REPO"

# 3. GitHub App PEM (from canonical location)
PEM_PATH="${SHADOWTAG_PEM:-/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem}"
if [[ -f "$PEM_PATH" ]]; then
    echo "Setting SHADOWTAG_APP_PEM from $PEM_PATH..."
    gh secret set SHADOWTAG_APP_PEM --repo "$REPO" < "$PEM_PATH"
else
    echo "⚠  PEM not found at $PEM_PATH — set manually:"
    echo "   gh secret set SHADOWTAG_APP_PEM --repo $REPO < /path/to/your.pem"
fi

# 4. GitHub App ID (variable, not secret)
echo "Setting SHADOWTAG_APP_ID variable..."
gh variable set SHADOWTAG_APP_ID --repo "$REPO" --body "3018200"

# 5. Gemini API Key (for existing GCA workflows)
if [[ -n "${GEMINI_API_KEY:-}" ]]; then
    echo "Setting GEMINI_API_KEY..."
    echo "$GEMINI_API_KEY" | gh secret set GEMINI_API_KEY --repo "$REPO"
else
    echo "⚠  GEMINI_API_KEY not in env — skip or set manually"
fi

echo ""
echo "✅ Done! Verify with:"
echo "   gh secret list --repo $REPO"
echo "   gh variable list --repo $REPO"
