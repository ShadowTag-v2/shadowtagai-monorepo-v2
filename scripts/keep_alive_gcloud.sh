#!/bin/bash
# GCLOUD AUTH KEEP-ALIVE DAEMON
# Usage: ./scripts/keep_alive_gcloud.sh
# Purpose: Prevents 60-minute token expiration mid-flight
# Runs in a separate terminal alongside development

set -euo pipefail

REFRESH_INTERVAL=2400  # 40 minutes (before 60-min expiry)
PROJECT="shadowtag-omega-v4"

echo "=== GCLOUD AUTH KEEP-ALIVE DAEMON ==="
echo "Project: $PROJECT"
echo "Refresh interval: ${REFRESH_INTERVAL}s (40 min)"
echo "Press Ctrl+C to stop"
echo ""

# Verify initial auth
echo "[INIT] Checking current auth..."
ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null || echo "NONE")
if [ "$ACCOUNT" = "NONE" ]; then
    echo "❌ No active GCloud account. Run: gcloud auth login"
    exit 1
fi
echo "  ✅ Active account: $ACCOUNT"
echo "  ✅ Project: $(gcloud config get-value project 2>/dev/null)"

# Ensure correct project
gcloud config set project "$PROJECT" 2>/dev/null

CYCLE=0
while true; do
    CYCLE=$((CYCLE + 1))
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$TIMESTAMP] Cycle $CYCLE: Refreshing application-default credentials..."

    # Refresh ADC token
    gcloud auth application-default print-access-token > /dev/null 2>&1 || {
        echo "  ⚠️ ADC refresh failed. Attempting re-login..."
        gcloud auth application-default login --no-launch-browser 2>/dev/null || true
    }

    # Verify project is still set
    CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
    if [ "$CURRENT_PROJECT" != "$PROJECT" ]; then
        echo "  ⚠️ Project drifted to $CURRENT_PROJECT. Resetting to $PROJECT..."
        gcloud config set project "$PROJECT" 2>/dev/null
    fi

    echo "  ✅ Credentials refreshed. Next refresh in ${REFRESH_INTERVAL}s."

    sleep $REFRESH_INTERVAL
done
