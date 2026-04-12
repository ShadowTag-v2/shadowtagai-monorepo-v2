#!/bin/bash
set -e

# ONE-CLICK DEPLOYMENT: STAGE 1 (FOUNDATION)
# Mission: Deploy GKE Standard Cluster with System and Judge pools.

echo "🚀 PNKLN STAGE 1: INITIATING FOUNDATION DEPLOYMENT..."

# 1. Pre-flight Checks
if [ -z "$GCP_PROJECT_ID" ]; then
    echo "❌ ERROR: GCP_PROJECT_ID is not set."
    echo "Usage: export GCP_PROJECT_ID='your-project-id' && ./deploy_stage1.sh"
    exit 1
fi

echo "✅ Project ID: $GCP_PROJECT_ID"
export TF_VAR_project_id=$GCP_PROJECT_ID

# Ensure we are in the script's directory for relative pathing
cd "$(dirname "$0")"

# 2. Enable APIs
echo "🛠 Enabling required APIs..."
gcloud services enable \
    compute.googleapis.com \
    container.googleapis.com \
    iam.googleapis.com \
    --project $GCP_PROJECT_ID

# 3. Terraform Execution
echo "🏗 Applying Terraform Infrastructure..."
cd ../terraform
terraform init
terraform apply -auto-approve

# 4. Validation Gate
echo "🔍 Validating Cluster Status..."
CLUSTER_STATUS=$(gcloud container clusters describe pnkln-cluster --region us-central1 --format="value(status)" 2>/dev/null)

if [ "$CLUSTER_STATUS" == "RUNNING" ]; then
    echo "✅ GATE PASSED: Cluster is RUNNING."
    echo "💰 Estimated Cost: ~$504/month (System + Judge pools)"
    echo "📝 Next Step: Run ./deploy_stage2.sh to deploy Inference Stack."
else
    echo "❌ GATE FAILED: Cluster status is $CLUSTER_STATUS."
    exit 1
fi
