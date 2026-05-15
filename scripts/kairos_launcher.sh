#!/bin/bash
# KAIROS Daemon Launcher — launchd wrapper
# Fetches secrets from GCP Secret Manager at runtime instead of hardcoding in plist.
# Called by com.shadowtag.kairos.plist ProgramArguments.

set -euo pipefail

# Runtime env
export GCP_PROJECT="shadowtag-omega-v4"
export DISABLE_TELEMETRY=1
export PYTHONPATH="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/packages:/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

# Fetch GEMINI_API_KEY from GCP Secret Manager (never hardcoded)
export GEMINI_API_KEY="$(gcloud secrets versions access latest --secret=gemini-api-key --project=shadowtag-omega-v4 2>/dev/null || echo "")"

if [ -z "$GEMINI_API_KEY" ]; then
    echo "[KAIROS] WARNING: Failed to fetch GEMINI_API_KEY from Secret Manager. Suggestions will be disabled." >&2
fi

exec /opt/homebrew/bin/python3.14 /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/scripts/kairos_daemon.py "$@"
