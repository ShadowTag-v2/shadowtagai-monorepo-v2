#!/bin/bash
set -euo pipefail

# CONFIG
PROJECT_ID="shadowtag-omega-v2"
REGION="us-central1"
CLUSTER_ID="agent-cluster"
CONFIG_ID="agent-config"
WORKSTATION_ID="brave-agent-workstation"

echo ">>> 🏗️ PROVISIONING WORKSTATION INFRASTRUCTURE ($PROJECT_ID)..."

# 1. Enable API
gcloud services enable workstations.googleapis.com --project="$PROJECT_ID" || \
  { echo "Failed to enable workstations API"; exit 1; }

# 2. Create Cluster (if not exists)
if ! gcloud beta workstations clusters describe "$CLUSTER_ID" --region="$REGION" --project="$PROJECT_ID" >/dev/null 2>&1; then
    echo "Creating Cluster: $CLUSTER_ID..."
    gcloud beta workstations clusters create "$CLUSTER_ID" \
      --region="$REGION" \
      --project="$PROJECT_ID" || { echo "Failed to create cluster"; exit 1; }
else
    echo "Cluster $CLUSTER_ID exists."
fi

# 3. Create Config (if not exists)
if ! gcloud beta workstations configs describe "$CONFIG_ID" --cluster="$CLUSTER_ID" --region="$REGION" --project="$PROJECT_ID" >/dev/null 2>&1; then
    echo "Creating Config: $CONFIG_ID..."
    gcloud beta workstations configs create "$CONFIG_ID" \
      --cluster="$CLUSTER_ID" \
      --region="$REGION" \
      --project="$PROJECT_ID" \
      --machine-type="e2-standard-4" \
      --idle-timeout=120m || { echo "Failed to create config"; exit 1; }
else
    echo "Config $CONFIG_ID exists."
fi

# 4. Create Workstation (if not exists)
if ! gcloud beta workstations describe "$WORKSTATION_ID" --cluster="$CLUSTER_ID" --config="$CONFIG_ID" --region="$REGION" --project="$PROJECT_ID" >/dev/null 2>&1; then
    echo "Creating Workstation: $WORKSTATION_ID..."
    gcloud beta workstations create "$WORKSTATION_ID" \
      --cluster="$CLUSTER_ID" \
      --config="$CONFIG_ID" \
      --region="$REGION" \
      --project="$PROJECT_ID" || { echo "Failed to create workstation"; exit 1; }
else
    echo "Workstation $WORKSTATION_ID exists."
fi

echo ">>> ✅ INFRASTRUCTURE READY."
echo "You can now run 'deploy_agent.sh' to deploy the code."
