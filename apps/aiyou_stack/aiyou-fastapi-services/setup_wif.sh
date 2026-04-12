#!/bin/bash
set -e

# Configuration
PROJECT_ID="shadowtag-omega-v2"
POOL_ID="antigravity-pool-v2"
PROVIDER_ID="antigravity-provider"
SERVICE_ACCOUNT_EMAIL="gemini-antigravity-sa@${PROJECT_ID}.iam.gserviceaccount.com"
WIF_CONFIG_FILE="wif-config.json"
REPO="ShadowTag-v2/ShadowTag-v2-fastapi-services" # Adjust if needed, but using subject mapping mostly

echo "Checking WIF Configuration..."

# 1. Verify Pool
if gcloud iam workload-identity-pools describe "${POOL_ID}" --project="${PROJECT_ID}" --location="global" > /dev/null 2>&1; then
    echo "✅ Pool '${POOL_ID}' exists."
else
    echo "❌ Pool '${POOL_ID}' not found. Please create it manually or check the ID."
    exit 1
fi

# 2. Verify Provider
if gcloud iam workload-identity-pools providers describe "${PROVIDER_ID}" \
    --project="${PROJECT_ID}" --location="global" \
    --workload-identity-pool="${POOL_ID}" > /dev/null 2>&1; then
    echo "✅ Provider '${PROVIDER_ID}' exists."
else
    echo "❌ Provider '${PROVIDER_ID}' not found."
    exit 1
fi

# 3. IAM Policy Binding (Allow GitHub Actions to impersonate the SA)
echo "Binding Service Account..."
# Construct the member string for the GitHub repo (or specific subject)
# Using generic subject mapping from the provider setup: google.subject=assertion.sub
# Member format: principalSet://iam.googleapis.com/projects/NUMBER/locations/global/workloadIdentityPools/POOL_ID/attribute.repository/REPO
# OR principal://iam.googleapis.com/projects/NUMBER/locations/global/workloadIdentityPools/POOL_ID/subject/SUBJECT

PROJECT_NUMBER=$(gcloud projects describe "${PROJECT_ID}" --format="value(projectNumber)")
MEMBER="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/*"

# We bind to the *entire* pool for simplicity in this dev environment, or specific attributes.
# Let's bind to the specific attribute.repository if possible, or just the subject.
# Currently mapping is: google.subject=assertion.sub
# So we can bind to specific subjects, or use attribute.repository if mapped.
# Checking provider I saw: attribute.repository: assertion.repository IS mapped.
# So we can use attribute.repository.

# CAUTION: Replace OWNER/REPO with actual if validating specific repo.
# For now, let's authorize the specific repo if known, or the whole pool if flexible.
# Let's authorize the pool to be safe/broad for now, or check correct repo.
# User repo seems to be: ShadowTag-v2/ShadowTag-v2-fastapi-services (from context)

gcloud iam service-accounts add-iam-policy-binding "${SERVICE_ACCOUNT_EMAIL}" \
    --project="${PROJECT_ID}" \
    --role="roles/iam.workloadIdentityUser" \
    --member="${MEMBER}" \
    --no-user-output-enabled

echo "✅ IAM Binding added/verified."

# 4. Generate Config
# 4. Success Message
echo "✅ WIF Infrastructure Setup Complete."
echo " - Pool: ${POOL_ID}"
echo " - Provider: ${PROVIDER_ID}"
echo " - Service Account: ${SERVICE_ACCOUNT_EMAIL}"
echo " - Binding: roles/iam.workloadIdentityUser assigned."
echo ""
echo "To use in GitHub Actions:"
echo "  uses: google-github-actions/auth@v2"
echo "  with:"
echo "    workload_identity_provider: projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/providers/${PROVIDER_ID}"
echo "    service_account: ${SERVICE_ACCOUNT_EMAIL}"
