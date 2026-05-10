# Item 18: canary_deploy.sh — Wire canary_analysis.py into CI deploy
# Usage: bash scripts/canary_deploy.sh <image_tag>
# Requires: CLOUDSDK_PYTHON, gcloud, python3
#!/usr/bin/env bash
set -euo pipefail

TAG="${1:-v3.3.2}"
SERVICE="counselconduit"
REGION="us-central1"
PROJECT="shadowtag-omega-v4"
CANARY_TAG="canary-${TAG//./-}"
IMAGE="us-central1-docker.pkg.dev/${PROJECT}/counselconduit/counselconduit:${TAG}"

echo "=== CounselConduit Canary Deploy ==="
echo "Tag: ${TAG}"
echo "Image: ${IMAGE}"

# Step 1: Deploy canary revision (no traffic)
echo "--- Step 1: Deploying canary revision (0% traffic) ---"
CLOUDSDK_PYTHON=/opt/homebrew/bin/python3 gcloud run deploy "${SERVICE}" \
  --image="${IMAGE}" \
  --region="${REGION}" \
  --project="${PROJECT}" \
  --revision-suffix="${CANARY_TAG}" \
  --no-traffic \
  --quiet

# Step 2: Split 10% traffic to canary
echo "--- Step 2: Routing 10% traffic to canary ---"
STABLE_REV=$(CLOUDSDK_PYTHON=/opt/homebrew/bin/python3 gcloud run revisions list \
  --service="${SERVICE}" --region="${REGION}" --project="${PROJECT}" \
  --filter="status.conditions.type=Active AND status.conditions.status=True" \
  --sort-by="~metadata.creationTimestamp" --limit=2 \
  --format="value(metadata.name)" | head -1)

CLOUDSDK_PYTHON=/opt/homebrew/bin/python3 gcloud run services update-traffic "${SERVICE}" \
  --region="${REGION}" --project="${PROJECT}" \
  --to-revisions="${STABLE_REV}=90,${SERVICE}-${CANARY_TAG}=10" \
  --quiet

echo "--- Step 3: Wait 5 minutes for canary soak ---"
sleep 300

# Step 4: Run canary analysis
echo "--- Step 4: Running canary analysis ---"
python3 scripts/canary_analysis.py 2>&1

# Step 5: If analysis passes, promote to 100%
echo "--- Step 5: Promoting canary to 100% ---"
CLOUDSDK_PYTHON=/opt/homebrew/bin/python3 gcloud run services update-traffic "${SERVICE}" \
  --region="${REGION}" --project="${PROJECT}" \
  --to-latest \
  --quiet

echo "=== Canary deploy complete: ${TAG} is now at 100% ==="
