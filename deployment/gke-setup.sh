#!/bin/bash
# GKE Cluster Setup Script for Cor.17 AI Architecture

set -e

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-"your-project-id"}
CLUSTER_NAME="cor17-cluster"
REGION=${GCP_REGION:-"us-central1"}
ZONE="${REGION}-a"
MACHINE_TYPE="n1-standard-4"
NUM_NODES=3

echo "🚀 Setting up GKE cluster for Cor.17 AI Architecture"

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "📦 Enabling required GCP APIs..."
gcloud services enable \
    container.googleapis.com \
    compute.googleapis.com \
    aiplatform.googleapis.com \
    storage-api.googleapis.com \
    dlp.googleapis.com

# Create GKE cluster
echo "🏗️ Creating GKE cluster: $CLUSTER_NAME"
gcloud container clusters create $CLUSTER_NAME \
    --region $REGION \
    --machine-type $MACHINE_TYPE \
    --num-nodes $NUM_NODES \
    --enable-autoscaling \
    --min-nodes 3 \
    --max-nodes 20 \
    --enable-autorepair \
    --enable-autoupgrade \
    --enable-ip-alias \
    --network "default" \
    --subnetwork "default" \
    --enable-stackdriver-kubernetes \
    --addons HorizontalPodAutoscaling,HttpLoadBalancing,GcePersistentDiskCsiDriver \
    --workload-pool=$PROJECT_ID.svc.id.goog

# Get cluster credentials
echo "🔑 Getting cluster credentials..."
gcloud container clusters get-credentials $CLUSTER_NAME --region $REGION

# Create service account for Workload Identity
echo "👤 Creating service account..."
gcloud iam service-accounts create cor17-gke \
    --display-name "Cor.17 GKE Service Account"

# Grant necessary permissions
echo "🔐 Granting IAM permissions..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member "serviceAccount:cor17-gke@$PROJECT_ID.iam.gserviceaccount.com" \
    --role "roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member "serviceAccount:cor17-gke@$PROJECT_ID.iam.gserviceaccount.com" \
    --role "roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member "serviceAccount:cor17-gke@$PROJECT_ID.iam.gserviceaccount.com" \
    --role "roles/dlp.user"

# Create GCS buckets
echo "🪣 Creating GCS buckets..."
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://aiyou-data-bucket || echo "Data bucket already exists"
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://aiyou-models-bucket || echo "Model bucket already exists"

# Apply Kubernetes configurations
echo "☸️ Applying Kubernetes configurations..."
kubectl apply -f deployment/kubernetes/namespace.yaml
kubectl apply -f deployment/kubernetes/configmap.yaml
kubectl apply -f deployment/kubernetes/secret.yaml
kubectl apply -f deployment/kubernetes/service-account.yaml
kubectl apply -f deployment/kubernetes/pvc.yaml
kubectl apply -f deployment/kubernetes/redis.yaml

# Bind Workload Identity
echo "🔗 Setting up Workload Identity..."
gcloud iam service-accounts add-iam-policy-binding \
    cor17-gke@$PROJECT_ID.iam.gserviceaccount.com \
    --role roles/iam.workloadIdentityUser \
    --member "serviceAccount:$PROJECT_ID.svc.id.goog[cor17/cor17-sa]"

echo "✅ GKE cluster setup complete!"
echo ""
echo "Next steps:"
echo "1. Build and push Docker image: ./deployment/build-and-push.sh"
echo "2. Deploy application: kubectl apply -f deployment/kubernetes/deployment.yaml"
echo "3. Apply HPA: kubectl apply -f deployment/kubernetes/hpa.yaml"
echo "4. Configure Ingress: kubectl apply -f deployment/kubernetes/ingress.yaml"
echo ""
echo "Get cluster info:"
echo "  kubectl cluster-info"
echo "  kubectl get nodes"
echo "  kubectl get pods -n cor17"
