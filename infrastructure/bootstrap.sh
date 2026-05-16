#!/bin/bash
set -euo pipefail

# ==============================================================================
# Terraform Bootstrap Script
# ==============================================================================
# This script creates the GCS bucket for Terraform state storage
# Run this ONCE before running terraform init
# ==============================================================================

PROJECT_ID="${PROJECT_ID:-pnkln-core-stack}"
REGION="${REGION:-us-central1}"
BUCKET_NAME="pnkln-terraform-state"

echo "Creating Terraform state bucket..."
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Bucket: gs://${BUCKET_NAME}"

# Create bucket if it doesn't exist
if gsutil ls -b "gs://${BUCKET_NAME}" 2>/dev/null; then
  echo "Bucket already exists: gs://${BUCKET_NAME}"
else
  echo "Creating bucket..."
  gsutil mb -p "${PROJECT_ID}" -c STANDARD -l "${REGION}" "gs://${BUCKET_NAME}"

  # Enable versioning
  gsutil versioning set on "gs://${BUCKET_NAME}"

  # Enable uniform bucket-level access
  gsutil uniformbucketlevelaccess set on "gs://${BUCKET_NAME}"

  echo "✓ Bucket created successfully"
fi

echo ""
echo "Bootstrap complete. You can now run:"
echo "  cd infrastructure"
echo "  terraform init"
echo "  terraform plan"
echo "  terraform apply"
