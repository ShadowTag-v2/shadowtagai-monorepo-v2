#!/bin/bash
TARGET="shadowtag-omega-v2"
echo "🌐 [Phase 4] Identity Pivot: Targeting $TARGET..."

# 1. Update Cloud Build
echo "   -> Patching Cloud Build Configs..."
find infra/cloudbuild -name "*.yaml" -type f -exec sed -i '' "s/shadowtag-v2/$TARGET/g" {} +

# 2. Update Terraform
echo "   -> Patching Terraform State & Vars..."
# Replace generic or old project IDs in .tf files
find infra/terraform -name "*.tf" -type f -exec sed -i '' "s/shadowtag-v2/$TARGET/g" {} +

# Create/Overwrite the Backend Config for the new project
cat > infra/terraform/backend.tf <<EOF
terraform {
  backend "gcs" {
    bucket  = "${TARGET}-tfstate"
    prefix  = "terraform/state"
  }
}
provider "google" {
  project = "${TARGET}"
  region  = "us-central1"
}
EOF

# 3. Authenticate
echo "   -> Setting GCloud Context..."
gcloud config set project "$TARGET"

echo "✅ [Phase 4] Identity Established."
