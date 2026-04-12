#!/bin/bash
set -e

# Project Configuration
export PROJECT_ID=$(gcloud config get project)
export REGION="us-central1"
export ZONE="us-central1-a"

echo "Using Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Zone: $ZONE"

# 1. Enable Required APIs
echo "Enabling APIs..."
gcloud services enable container.googleapis.com \
    compute.googleapis.com \
    bigquery.googleapis.com \
    notebooks.googleapis.com \
    cloudresourcemanager.googleapis.com

# 2. Create GKE Cluster with gVisor
echo "Creating GKE Cluster (mcp-dev-cluster)..."
# Check if cluster exists first
if ! gcloud container clusters describe mcp-dev-cluster --zone=$ZONE > /dev/null 2>&1; then
    gcloud container clusters create mcp-dev-cluster \
      --zone=$ZONE \
      --machine-type=n1-standard-4 \
      --num-nodes=3 \
      --enable-sandbox \
      --enable-autoscaling \
      --min-nodes=3 \
      --max-nodes=10 \
      --addons=Istio,CloudRun,HorizontalPodAutoscaling \
      --workload-pool=$PROJECT_ID.svc.id.goog \
      --enable-stackdriver-kubernetes
else
    echo "Cluster mcp-dev-cluster already exists."
fi

# 3. Create BigQuery Dataset
echo "Creating BigQuery Dataset..."
if ! bq ls --dataset_id $PROJECT_ID:mcp_audit_logs > /dev/null 2>&1; then
    bq mk \
      --dataset \
      --location=US \
      --description="MCP code execution audit logs" \
      $PROJECT_ID:mcp_audit_logs

    # Create Table
    bq mk \
      --table \
      $PROJECT_ID:mcp_audit_logs.code_executions \
      timestamp:TIMESTAMP,user_id:STRING,session_id:STRING,code_hash:STRING,code_length:INTEGER,execution_time_ms:FLOAT,success:BOOLEAN,error:STRING,security_violations:STRING,resource_usage:STRING,sandbox_id:STRING
else
    echo "Dataset mcp_audit_logs already exists."
fi

# 4. Service Account Setup
echo "Setting up Service Account..."
SA_NAME="mcp-server"
SA_EMAIL="$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"

if ! gcloud iam service-accounts describe $SA_EMAIL > /dev/null 2>&1; then
    gcloud iam service-accounts create $SA_NAME \
      --display-name="MCP Code Execution Server" \
      --description="Service account for MCP server with BigQuery write access"
fi

# Grant BigQuery data editor role
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/bigquery.dataEditor"

# Workload Identity Binding
gcloud iam service-accounts add-iam-policy-binding \
  $SA_EMAIL \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:$PROJECT_ID.svc.id.goog[mcp-system/mcp-server-sa]"

echo "Infrastructure setup complete!"
