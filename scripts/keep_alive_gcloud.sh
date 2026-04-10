#!/usr/bin/env bash
# Sovereign State Protocol — Interactive Auth Keep-Alive
# Refreshes gcloud token every 50 minutes (before 60-min expiry)
# Requires: browser click "Allow" each cycle
set -euo pipefail

INTERVAL=3000  # 50 minutes in seconds

echo "=== GCLOUD AUTH KEEP-ALIVE (Interactive) ==="
echo "Will refresh every $((INTERVAL/60)) minutes. Close with Ctrl+C."
echo ""

while true; do
  echo "[$(date '+%H:%M:%S')] Refreshing gcloud auth..."
  gcloud auth application-default login --no-launch-browser 2>/dev/null \
    || gcloud auth application-default login
  echo "[$(date '+%H:%M:%S')] Token refreshed. Next refresh in $((INTERVAL/60)) min."
  sleep "$INTERVAL"
done
