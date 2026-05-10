#!/bin/bash
# create_workstation.sh
# PROVISIONS THE ANTIGRAVITY COCKPIT (Cloud Workstation)

PROJECT_ID="shadowtag-omega-v2"
REGION="us-central1"
CLUSTER_ID="antigravity-cluster"
CONFIG_ID="god-mode-config"
WORKSTATION_ID="shadowtag-cockpit"
SERVICE_ACCOUNT_EMAIL="hands-sa@${PROJECT_ID}.iam.gserviceaccount.com" # From shadowtag_omega_v2_deploy.sh
WORKER_IMAGE="mcr.microsoft.com/playwright:v1.41.0-jammy" # From shadowtag_omega_v2_deploy.sh

echo ">>> 🏗️  PROVISIONING COCKPIT INFRASTRUCTURE..."

# 1. Enable APIs
echo "Enabling Workstations API..."
gcloud services enable workstations.googleapis.com --project=$PROJECT_ID

# 2. Create Cluster (The Dock)
echo "Creating Workstation Cluster: $CLUSTER_ID..."
if ! gcloud workstations clusters describe $CLUSTER_ID --region=$REGION --project=$PROJECT_ID &>/dev/null; then
    gcloud workstations clusters create $CLUSTER_ID \
        --region=$REGION \
        --project=$PROJECT_ID \
        --network="default" \
        --subnetwork="default" \
        --async
    echo "Cluster $CLUSTER_ID creation initiated."
else
    echo "Cluster $CLUSTER_ID already exists."
fi

# 3. Create Config (The Blueprint)
echo "Creating Workstation Config: $CONFIG_ID..."
if ! gcloud workstations configs describe $CONFIG_ID --region=$REGION --cluster=$CLUSTER_ID --project=$PROJECT_ID &>/dev/null; then
    gcloud workstations configs create $CONFIG_ID \
        --region=$REGION \
        --cluster=$CLUSTER_ID \
        --project=$PROJECT_ID \
        --machine-type="e2-standard-8" \
        --idle-timeout=120m \
        --container-custom-image="$WORKER_IMAGE" \
        --service-account="$SERVICE_ACCOUNT_EMAIL" \
        --async
    echo "Config $CONFIG_ID creation initiated."
else
    echo "Config $CONFIG_ID already exists."
fi

# 4. Create Workstation (The Ship)
echo "Creating Workstation: $WORKSTATION_ID..."
if ! gcloud workstations describe $WORKSTATION_ID --region=$REGION --cluster=$CLUSTER_ID --config=$CONFIG_ID --project=$PROJECT_ID &>/dev/null; then
    gcloud workstations create $WORKSTATION_ID \
        --region=$REGION \
        --cluster=$CLUSTER_ID \
        --config=$CONFIG_ID \
        --project=$PROJECT_ID \
        --async
    echo "Workstation $WORKSTATION_ID creation initiated."
else
    echo "Workstation $WORKSTATION_ID already exists."
fi

echo ">>> ✅ COCKPIT PROVISIONED (or creation initiated)."
echo "Waiting for workstation $WORKSTATION_ID to be ready..."

# Wait for the workstation to be in a READY state
gcloud workstations describe $WORKSTATION_ID \
    --region=$REGION \
    --cluster=$CLUSTER_ID \
    --config=$CONFIG_ID \
    --project=$PROJECT_ID \
    --format="value(state)" \
    --filter="state=ACTIVE" \
    --timeout=600s # Wait up to 10 minutes for it to become active

echo "Workstation $WORKSTATION_ID is now ACTIVE."
echo "Run: gcloud workstations start $WORKSTATION_ID --region=$REGION --project=$PROJECT_ID"
echo "Then connect: gcloud workstations ssh $WORKSTATION_ID --region=$REGION --project=$PROJECT_ID"
