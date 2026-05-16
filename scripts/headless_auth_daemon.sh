#!/usr/bin/env bash
# Sovereign State Protocol — Headless Auth Daemon (Zero Prompts)
# Requires: keys/service-account.json (SA: headless-runner@shadowtag-omega-v4.iam.gserviceaccount.com)
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
SA_KEY="${REPO_ROOT}/keys/service-account.json"
PROJECT="${GCLOUD_PROJECT:-shadowtag-omega-v4}"
INTERVAL=3300  # 55 minutes

if [[ ! -f "$SA_KEY" ]]; then
  echo "ERROR: Service account key not found at $SA_KEY"
  echo "Place headless-runner@${PROJECT}.iam.gserviceaccount.com key there."
  exit 1
fi

echo "=== HEADLESS AUTH DAEMON ==="
echo "SA Key: $SA_KEY"
echo "Project: $PROJECT"
echo "Refresh interval: $((INTERVAL/60)) min"
echo ""

# Initial auth
gcloud auth activate-service-account --key-file="$SA_KEY" --project="$PROJECT"
gcloud config set project "$PROJECT"
echo "[$(date '+%H:%M:%S')] Initial auth complete."

while true; do
  sleep "$INTERVAL"
  echo "[$(date '+%H:%M:%S')] Re-authenticating..."
  gcloud auth activate-service-account --key-file="$SA_KEY" --project="$PROJECT"
  # Refresh application-default token too
  gcloud auth application-default activate-service-account \
    --key-file="$SA_KEY" 2>/dev/null || true
  echo "[$(date '+%H:%M:%S')] Done. Next refresh in $((INTERVAL/60)) min."
done
