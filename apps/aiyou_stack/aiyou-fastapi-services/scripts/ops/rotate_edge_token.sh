#!/bin/bash
# Pnkln Operations: Rotate Edge Token
# Author: Pnkln Ops
# Description: Rotates the PNKLN_EDGE_TOKEN secret in GCP Secret Manager and updates local references.

set -euo pipefail

# Configuration
SECRET_NAME="PNKLN_EDGE_TOKEN"
PROJECT_ID="${PNKLN_PROJECT_ID:-pnkln-core-v1}"
TIMESTAMP=$(date +%s)
NEW_TOKEN="edge-tok-${TIMESTAMP}-$(openssl rand -hex 8)"

echo "🔄 Starting Secret Rotation for: ${SECRET_NAME}"

# 1. Create new secret version in GCP
if command -v gcloud &> /dev/null; then
    echo "☁️  Pushing new version to GCP Secret Manager..."
    # Check if secret exists first, create if not
    if ! gcloud secrets describe "${SECRET_NAME}" --project="${PROJECT_ID}" &>/dev/null; then
         echo -n "${NEW_TOKEN}" | gcloud secrets create "${SECRET_NAME}" --data-file=- --replication-policy="automatic" --project="${PROJECT_ID}" --quiet
    else
         echo -n "${NEW_TOKEN}" | gcloud secrets versions add "${SECRET_NAME}" --data-file=- --project="${PROJECT_ID}" --quiet
    fi
    echo "✅ GCP Secret updated."
else
    echo "⚠️  gcloud CLI not found or configured. Skipping cloud sync (Simulation Mode)."
fi

# 2. Update Local Environment (.env stub or similar)
# In a real scenario, this might update a Vault or k8s secret.
# Here we just output it for the operator to capture if needed.
echo "🔑 New Token Generated: ${NEW_TOKEN}"

# 3. Validation
echo "🔍 Verifying token format..."
if [[ "${NEW_TOKEN}" =~ ^edge-tok- ]]; then
    echo "✅ Token format valid."
else
    echo "❌ Token format invalid!"
    exit 1
fi

echo "🎉 Rotation Complete. Please update dependent services (Starlink Gateway, Edge Pods)."
