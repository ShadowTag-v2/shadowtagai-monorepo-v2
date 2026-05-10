#!/bin/bash
# Deploy Kosmos to GKE

set -e

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-"your-project-id"}
REGION=${GCP_REGION:-"us-central1"}
CLUSTER_NAME=${CLUSTER_NAME:-"kosmos-cluster"}
IMAGE_NAME="gcr.io/${PROJECT_ID}/kosmos-orchestrator"

echo "=== Kosmos GKE Deployment ==="
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Cluster: $CLUSTER_NAME"
echo ""

# Step 1: Build and push Docker image
echo "[1/6] Building Docker image..."
cd "$(dirname "$0")/../.."
docker build -t "${IMAGE_NAME}:latest" -f deployment/Dockerfile .

echo "[2/6] Pushing image to GCR..."
docker push "${IMAGE_NAME}:latest"

# Step 2: Create GKE cluster if it doesn't exist
echo "[3/6] Checking GKE cluster..."
if ! gcloud container clusters describe "$CLUSTER_NAME" \
    --location="$REGION" \
    --project="$PROJECT_ID" &>/dev/null; then

    echo "Creating GKE Autopilot cluster..."
    gcloud container clusters create-auto "$CLUSTER_NAME" \
        --location="$REGION" \
        --project="$PROJECT_ID" \
        --workload-pool="${PROJECT_ID}.svc.id.goog"
else
    echo "Cluster $CLUSTER_NAME already exists"
fi

# Step 3: Configure kubectl
echo "[4/6] Configuring kubectl..."
gcloud container clusters get-credentials "$CLUSTER_NAME" \
    --location="$REGION" \
    --project="$PROJECT_ID"

# Step 4: Set up Workload Identity
echo "[5/6] Setting up Workload Identity..."

# Create GCP service account if it doesn't exist
if ! gcloud iam service-accounts describe "kosmos-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --project="$PROJECT_ID" &>/dev/null; then

    gcloud iam service-accounts create kosmos-sa \
        --display-name="Kosmos Orchestrator Service Account" \
        --project="$PROJECT_ID"
fi

# Grant necessary permissions
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:kosmos-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:kosmos-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/datastore.user"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:kosmos-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:kosmos-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/cloudtrace.agent"

# Bind to Kubernetes service account
gcloud iam service-accounts add-iam-policy-binding \
    "kosmos-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role roles/iam.workloadIdentityUser \
    --member "serviceAccount:${PROJECT_ID}.svc.id.goog[default/kosmos-sa]" \
    --project="$PROJECT_ID"

# Step 5: Create Storage bucket
echo "Creating Cloud Storage bucket..."
gsutil mb -p "$PROJECT_ID" -l "$REGION" \
    "gs://${PROJECT_ID}-kosmos-artifacts" 2>/dev/null || true

# Step 6: Deploy to Kubernetes
echo "[6/6] Deploying to Kubernetes..."

# Replace PROJECT_ID in manifests
cat deployment/kubernetes/deployment.yaml | \
    sed "s/PROJECT_ID/$PROJECT_ID/g" | \
    kubectl apply -f -

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "To check status:"
echo "  kubectl get pods -l app=kosmos"
echo ""
echo "To view logs:"
echo "  kubectl logs -f -l app=kosmos"
echo ""
echo "To get service IP:"
echo "  kubectl get service kosmos-service"
echo ""
echo "Don't forget to create the AgentOps secret:"
echo "  kubectl create secret generic kosmos-secrets \\"
echo "    --from-literal=agentops-api-key=YOUR_KEY"
