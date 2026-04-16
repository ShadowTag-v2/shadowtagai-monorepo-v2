#!/usr/bin/env bash
# iam_mappings.sh
# Manually map GCP IAM service accounts (Stub for Phase 2 Deployment)

PROJECT_ID="shadowtag-omega-v4"
REGION="us-central1"
SERVICE_ACCOUNT="kovelai-runner@${PROJECT_ID}.iam.gserviceaccount.com"

echo "Provisioning IAM mappings for $SERVICE_ACCOUNT..."

# 1. Ensure Service Account Exists
# gcloud iam service-accounts create kovelai-runner \
#    --description="KovelAI Cloud Run execution identity" \
#    --display-name="KovelAI Runner" \
#    --project="${PROJECT_ID}"

# 2. Bind Secrets Access (Secret Manager)
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor"

# 3. Bind Cloud Logging (Write)
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/logging.logWriter"

# 4. Bind Cloud Trace (APM)
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/cloudtrace.agent"

echo "IAM mapping complete."
