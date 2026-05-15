#!/bin/bash
# scripts/god_mode_launch.sh
# ShadowTag Omega v2 - "God Mode" Launch Protocol (Native Edition)
# Automates: Infrastructure and Native Refinery Deployments (Workflows + Vertex)

set -e

PROJECT_ID="shadowtag-omega-v3"
REGION="us-central1"

echo "💎 [GOD MODE] Initiating Native Launch Sequence for $PROJECT_ID..."
echo "✨ Stack: Google Cloud Workflows + Vertex AI (Zero External Keys)"

# 1. Authorization & Quota Setup
echo "🔑 [1/4] Configuring Authorization Context..."
gcloud config set project $PROJECT_ID
gcloud auth application-default set-quota-project $PROJECT_ID

export GOOGLE_BILLING_PROJECT=$PROJECT_ID
export GOOGLE_USER_PROJECT_OVERRIDE=true

# 2. Infrastructure (Terraform)
echo "🏗️ [2/4] Applying Infrastructure (Terraform)..."
cd infra/terraform
terraform init
terraform apply -auto-approve
cd ../..

# 3. Deploy Workflows (Orchestration)
echo "⚡ [3/4] Deploying Cloud Workflows..."
gcloud services enable workflows.googleapis.com workflowexecutions.googleapis.com --project $PROJECT_ID

gcloud workflows deploy shadowtag-orchestrator \
    --source=experiments/google-workflows/workflow.yaml \
    --location=$REGION \
    --project=$PROJECT_ID

echo "   ✅ Workflow Deployed: shadowtag-orchestrator"

# 4. Deploy Refineries
echo "🚀 [4/4] Deploying Refineries via Cloud Build..."

# Ruby MCP (Kept as Specialist)
echo "   -> Submitting Ruby MCP Build..."
gcloud builds submit experiments/ruby-firestore-mcp \
    --config experiments/ruby-firestore-mcp/cloudbuild.yaml \
    --project $PROJECT_ID --async

# Vertex Vision (Native AI)
echo "   -> Submitting Vertex Vision Build..."
gcloud builds submit experiments/vertex-vision \
    --config experiments/vertex-vision/cloudbuild.yaml \
    --project $PROJECT_ID --async

echo "✅ [GOD MODE] Launch Sequence Complete."
echo "   Monitor Builds: https://console.cloud.google.com/cloud-build/builds?project=$PROJECT_ID"
echo "   View Workflows: https://console.cloud.google.com/workflows?project=$PROJECT_ID"
