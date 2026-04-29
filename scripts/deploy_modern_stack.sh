#!/bin/bash
# ▙▖▙▖▞▞▙ ANTIGRAVITY DEPLOYMENT SCRIPT [v2025.2]
# DOCTRINE: FM 3-0 (Unified Land Operations)
# MISSION: Deploy "Gucci" Tech Stack on GKE Autopilot
# AUTHOR: ANTIGRAVITY

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}▙▖▙▖▞▞▙ ANTIGRAVITY: INITIATING DEPLOYMENT SEQUENCE${NC}"

# 0. AUTHENTICATION CHECK (The "Gatekeeper")
echo -e "${BLUE}[*] Verifying Administrative Access...${NC}"
if ! gcloud auth print-access-token &>/dev/null; then
    echo -e "${RED}[!] Authentication Required.${NC}"
    echo -e "${BLUE}[*] Initiating GCloud Login Sequence...${NC}"
    echo -e "${BLUE}[*] A browser window will open. Please sign in as ADMIN.${NC}"
    gcloud auth login
else
    echo -e "${GREEN}[+] Authenticated.${NC}"
fi

# 1. Configuration
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
CLUSTER_NAME="Claude_Code_6-sovereign-cloud"
NETWORK="default"

echo -e "${GREEN}[+] Target Project: ${PROJECT_ID}${NC}"

# 2. Enable APIs
echo -e "${BLUE}[*] Enabling Essential APIs...${NC}"
gcloud services enable \
    container.googleapis.com \
    aiplatform.googleapis.com \
    cloudbuild.googleapis.com \
    secretmanager.googleapis.com \
    artifactregistry.googleapis.com \
    --quiet

# 3. Deploy GKE Autopilot
echo -e "${BLUE}[*] Deploying GKE Autopilot Cluster...${NC}"
if ! gcloud container clusters describe ${CLUSTER_NAME} --region ${REGION} &>/dev/null; then
    gcloud container clusters create-auto ${CLUSTER_NAME} \
        --region ${REGION} \
        --release-channel "regular" \
        --network ${NETWORK} \
        --subnetwork ${NETWORK} \
        --enable-image-streaming \
        --quiet
    echo -e "${GREEN}[+] Cluster Deployed Successfully${NC}"
else
    echo -e "${GREEN}[+] Cluster already exists${NC}"
fi

# 4. Configure Credentials
echo -e "${BLUE}[*] Configuring kubectl credentials...${NC}"
gcloud container clusters get-credentials ${CLUSTER_NAME} --region ${REGION}

# 5. Install "Gucci" Python Stack
echo -e "${BLUE}[*] Installing Modern AI Stack...${NC}"
pip3 install --upgrade pip
pip3 install -r requirements.txt

# 6. Create Kubernetes Manifests
echo -e "${BLUE}[*] Generating Spot-Optimized Manifests...${NC}"
mkdir -p k8s/deployments

cat <<EOF > k8s/deployments/Claude_Code_6-core.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: Claude_Code_6-core
  labels:
    app: Claude_Code_6
    doctrine: targeting
spec:
  replicas: 2
  selector:
    matchLabels:
      app: Claude_Code_6
  template:
    metadata:
      labels:
        app: Claude_Code_6
    spec:
      nodeSelector:
        cloud.google.com/gke-spot: "true"
      terminationGracePeriodSeconds: 25
      containers:
      - name: Claude_Code_6-engine
        image: us-docker.pkg.dev/cloudrun/container/hello
        resources:
          requests:
            cpu: "500m"
            memory: "1Gi"
            ephemeral-storage: "1Gi"
        env:
        - name: DOCTRINE
          value: "PRECISION_PERSISTENCE_PROFIT"
EOF

# 7. Apply Manifests
echo -e "${BLUE}[*] Applying Initial Configuration...${NC}"
kubectl apply -f k8s/deployments/Claude_Code_6-core.yaml

echo -e "${BLUE}▙▖▙▖▞▞▙ DEPLOYMENT COMPLETE${NC}"
echo -e "${GREEN}Status: OPERATIONAL${NC}"
