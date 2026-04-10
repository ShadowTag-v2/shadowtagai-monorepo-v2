#!/bin/bash
set -e

# 1. Create the Config Bucket & Kill Switch File
echo "Creating Config Bucket..."
gcloud storage buckets create gs://shadowtag-omega-v2-safety-config --project=shadowtag-omega-v2 --location=us-central1 || echo "Bucket might already exist, continuing..."

echo "Creating initial Kill Switch JSON..."
echo '{
  "entities": ["Ashley St. Clair", "Elon Musk"],
  "phrases": ["bikini made of floss", "jailbreak"]
}' > kill_switch.json

echo "Uploading Kill Switch to GCS..."
gcloud storage cp kill_switch.json gs://shadowtag-omega-v2-safety-config/kill_switch.json

# 2. Build & Deploy
echo "Building Container..."
# Navigate to app dir for build context
cd app
gcloud builds submit --tag gcr.io/shadowtag-omega-v2/guardrail:latest .
cd ..

echo "Initializing Terraform..."
cd infra
terraform init

echo "Applying Infrastructure..."
# Note: You need to replace YOUR_ACTUAL_HIVE_KEY_HERE with the real key or pass it via env
# For this script we assume it might be passed as an arg or env var, strictly specifically asking user to check
echo "Applying Terraform. Please ensure you have set the 'hive_api_key' variable or pass it to this script."
# terraform apply -var="hive_api_key=$HIVE_API_KEY"
echo "Run 'terraform apply' manually in the infra directory with your Hive API Key."
