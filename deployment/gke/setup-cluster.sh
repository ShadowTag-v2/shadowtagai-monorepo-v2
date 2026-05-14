#!/bin/bash
# Setup GKE cluster for Plan Mode Service

set -e

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-your-project-id}"
CLUSTER_NAME="${GKE_CLUSTER:-plan-mode-cluster}"
REGION="${GKE_REGION:-us-central1}"
ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}"

echo "Setting up GKE cluster for Plan Mode Service"
echo "Project: $PROJECT_ID"
echo "Cluster: $CLUSTER_NAME"
echo "Region: $REGION"

# Set project
gcloud config set project "$PROJECT_ID"

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable container.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Create GKE cluster
echo "Creating GKE cluster..."
if ! gcloud container clusters describe "$CLUSTER_NAME" --region="$REGION" &>/dev/null; then
  gcloud container clusters create "$CLUSTER_NAME" \
    --region="$REGION" \
    --num-nodes=2 \
    --machine-type=n1-standard-2 \
    --enable-autoscaling \
    --min-nodes=2 \
    --max-nodes=10 \
    --enable-stackdriver-kubernetes \
    --enable-ip-alias \
    --workload-pool="$PROJECT_ID.svc.id.goog" \
    --addons=HorizontalPodAutoscaling,HttpLoadBalancing,GcePersistentDiskCsiDriver
  echo "Cluster created successfully"
else
  echo "Cluster already exists"
fi

# Get cluster credentials
echo "Getting cluster credentials..."
gcloud container clusters get-credentials "$CLUSTER_NAME" --region="$REGION"

# Create namespace
echo "Creating namespace..."
kubectl create namespace default --dry-run=client -o yaml | kubectl apply -f -

# Create service account for workload identity
echo "Creating service account..."
SA_NAME="plan-mode-service"
SA_EMAIL="$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"

if ! gcloud iam service-accounts describe "$SA_EMAIL" &>/dev/null; then
  gcloud iam service-accounts create "$SA_NAME" \
    --display-name="Plan Mode Service Account"
fi

# Bind workload identity
echo "Binding workload identity..."
kubectl create serviceaccount plan-mode-sa --namespace=default --dry-run=client -o yaml | kubectl apply -f -

gcloud iam service-accounts add-iam-policy-binding "$SA_EMAIL" \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:$PROJECT_ID.svc.id.goog[default/plan-mode-sa]"

kubectl annotate serviceaccount plan-mode-sa \
  --namespace=default \
  iam.gke.io/gcp-service-account="$SA_EMAIL" \
  --overwrite

# Create Anthropic API key secret
if [ -n "$ANTHROPIC_API_KEY" ]; then
  echo "Creating Anthropic API key secret..."
  kubectl create secret generic anthropic-api-key \
    --from-literal=api-key="$ANTHROPIC_API_KEY" \
    --namespace=default \
    --dry-run=client -o yaml | kubectl apply -f -
  echo "Secret created successfully"
else
  echo "WARNING: ANTHROPIC_API_KEY not set. You'll need to create the secret manually:"
  echo "kubectl create secret generic anthropic-api-key --from-literal=api-key=YOUR_KEY"
fi

# Apply ConfigMap
echo "Applying ConfigMap..."
envsubst < deployment/gke/configmap.yaml | kubectl apply -f -

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Build and push Docker image:"
echo "   docker build -t gcr.io/$PROJECT_ID/plan-mode-service:latest -f deployment/gke/Dockerfile ."
echo "   docker push gcr.io/$PROJECT_ID/plan-mode-service:latest"
echo ""
echo "2. Deploy the service:"
echo "   envsubst < deployment/gke/deployment.yaml | kubectl apply -f -"
echo ""
echo "3. Check deployment status:"
echo "   kubectl get deployments"
echo "   kubectl get pods"
echo "   kubectl get services"
