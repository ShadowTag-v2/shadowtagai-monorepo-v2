#!/bin/bash
#
# GKE Cluster Setup Script for PNKLN Core Stack Phase 1
# Sets up complete infrastructure for Ingestion + Orchestrator
#
# Usage: ./scripts/setup_gke_cluster.sh [PROJECT_ID]
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${1:-${GCP_PROJECT_ID}}"
CLUSTER_NAME="pnkln-ingestion"
REGION="us-central1"
NODE_COUNT=3
MACHINE_TYPE="n1-standard-2"

echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  PNKLN CORE STACK™ - GKE CLUSTER SETUP                 ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}\n"

# Validate project ID
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: PROJECT_ID not set${NC}"
    echo "Usage: $0 [PROJECT_ID]"
    echo "Or set GCP_PROJECT_ID environment variable"
    exit 1
fi

echo -e "${GREEN}▸ Project ID:${NC} $PROJECT_ID"
echo -e "${GREEN}▸ Cluster:${NC} $CLUSTER_NAME"
echo -e "${GREEN}▸ Region:${NC} $REGION\n"

# Step 1: Set project
echo -e "${CYAN}[1/8] Setting GCP project...${NC}"
gcloud config set project "$PROJECT_ID"
echo -e "${GREEN}✓ Project set${NC}\n"

# Step 2: Enable required APIs
echo -e "${CYAN}[2/8] Enabling required GCP APIs...${NC}"
gcloud services enable container.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage.googleapis.com
echo -e "${GREEN}✓ APIs enabled${NC}\n"

# Step 3: Create GKE cluster
echo -e "${CYAN}[3/8] Creating GKE cluster (this may take 5-10 minutes)...${NC}"

if gcloud container clusters describe "$CLUSTER_NAME" --region="$REGION" &>/dev/null; then
    echo -e "${YELLOW}⚠ Cluster $CLUSTER_NAME already exists, skipping creation${NC}\n"
else
    gcloud container clusters create "$CLUSTER_NAME" \
        --region="$REGION" \
        --num-nodes="$NODE_COUNT" \
        --machine-type="$MACHINE_TYPE" \
        --enable-autoscaling \
        --min-nodes=1 \
        --max-nodes=5 \
        --enable-autorepair \
        --enable-autoupgrade \
        --disk-size=50 \
        --disk-type=pd-standard \
        --no-enable-basic-auth \
        --no-issue-client-certificate \
        --enable-ip-alias \
        --metadata disable-legacy-endpoints=true \
        --scopes=gke-default,storage-rw,cloud-platform

    echo -e "${GREEN}✓ Cluster created${NC}\n"
fi

# Step 4: Get cluster credentials
echo -e "${CYAN}[4/8] Getting cluster credentials...${NC}"
gcloud container clusters get-credentials "$CLUSTER_NAME" --region="$REGION"
echo -e "${GREEN}✓ Credentials configured${NC}\n"

# Step 5: Create namespaces
echo -e "${CYAN}[5/8] Creating Kubernetes namespaces...${NC}"
kubectl create namespace ingestion --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace orchestrator --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace storage --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
echo -e "${GREEN}✓ Namespaces created${NC}\n"

# Step 6: Create service accounts
echo -e "${CYAN}[6/8] Creating IAM service accounts...${NC}"

# Ingestion crawler service account
if gcloud iam service-accounts describe "ingestion-crawler@${PROJECT_ID}.iam.gserviceaccount.com" &>/dev/null; then
    echo -e "${YELLOW}⚠ ingestion-crawler service account exists${NC}"
else
    gcloud iam service-accounts create ingestion-crawler \
        --display-name="Ingestion Layer Crawler" \
        --description="Service account for PNKLN ingestion crawlers"

    # Grant storage admin role
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:ingestion-crawler@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/storage.admin"
fi

# Orchestrator service account
if gcloud iam service-accounts describe "orchestrator-sa@${PROJECT_ID}.iam.gserviceaccount.com" &>/dev/null; then
    echo -e "${YELLOW}⚠ orchestrator-sa service account exists${NC}"
else
    gcloud iam service-accounts create orchestrator-sa \
        --display-name="CodeAct Orchestrator" \
        --description="Service account for PNKLN orchestrator"

    # Grant AI Platform user role
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:orchestrator-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/aiplatform.user"
fi

echo -e "${GREEN}✓ Service accounts created${NC}\n"

# Step 7: Create GCS bucket for training
echo -e "${CYAN}[7/8] Creating GCS bucket for training data...${NC}"
BUCKET_NAME="${PROJECT_ID}-training"

if gsutil ls "gs://${BUCKET_NAME}" &>/dev/null; then
    echo -e "${YELLOW}⚠ Bucket gs://${BUCKET_NAME} already exists${NC}"
else
    gsutil mb -l "$REGION" "gs://${BUCKET_NAME}"
    echo -e "${GREEN}✓ Bucket created: gs://${BUCKET_NAME}${NC}"
fi

echo

# Step 8: Verify setup
echo -e "${CYAN}[8/8] Verifying installation...${NC}"

echo -e "\n${GREEN}Cluster Info:${NC}"
kubectl cluster-info

echo -e "\n${GREEN}Nodes:${NC}"
kubectl get nodes

echo -e "\n${GREEN}Namespaces:${NC}"
kubectl get namespaces | grep -E "ingestion|orchestrator|storage|monitoring"

echo -e "\n${GREEN}Service Accounts:${NC}"
gcloud iam service-accounts list --filter="email:ingestion-crawler@* OR email:orchestrator-sa@*"

echo -e "\n${GREEN}GCS Buckets:${NC}"
gsutil ls | grep "$BUCKET_NAME"

echo -e "\n${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✓ GKE CLUSTER SETUP COMPLETE                           ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}\n"

echo -e "${CYAN}Next steps:${NC}"
echo "1. Deploy PostgreSQL: kubectl apply -f k8s/storage/postgresql.yaml"
echo "2. Configure secrets: ./scripts/configure_secrets.sh"
echo "3. Deploy ingestion layer: kubectl apply -f k8s/ingestion/"
echo "4. Run training pipeline: python training/vertex_ai_pipeline.py"
echo ""
echo -e "${YELLOW}Note: Make sure to configure API keys before deploying services${NC}"
