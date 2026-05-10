#!/bin/bash
# Setup Hugging Face credentials in Secret Manager
# Based on: GoogleCloudPlatform/accelerated-platforms inference-ref-arch

set -euo pipefail

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== Setting Up Hugging Face Credentials ===${NC}"

# Check required environment variables
if [ -z "${PROJECT_ID:-}" ]; then
    echo -e "${RED}Error: PROJECT_ID not set. Run: source .env.gcp-inference${NC}"
    exit 1
fi

# HF Token configuration
HF_SECRET_NAME="huggingface-hub-token"
HF_TOKEN=${HF_TOKEN:-}

if [ -z "$HF_TOKEN" ]; then
    echo -e "${YELLOW}Hugging Face token not found in environment.${NC}"
    echo -e "${YELLOW}You can get your token from: https://huggingface.co/settings/tokens${NC}"
    echo -e ""
    read -sp "Enter your Hugging Face token: " HF_TOKEN
    echo ""
fi

if [ -z "$HF_TOKEN" ]; then
    echo -e "${RED}Error: No Hugging Face token provided${NC}"
    exit 1
fi

# Validate token format (basic check)
if [[ ! "$HF_TOKEN" =~ ^hf_[A-Za-z0-9]{30,}$ ]]; then
    echo -e "${YELLOW}Warning: Token doesn't match expected format (hf_...)${NC}"
    read -p "Continue anyway? (y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if secret already exists
echo -e "\n${GREEN}Checking if secret exists...${NC}"

if gcloud secrets describe "${HF_SECRET_NAME}" \
    --project="${PROJECT_ID}" &>/dev/null; then
    echo -e "${YELLOW}Secret already exists: ${HF_SECRET_NAME}${NC}"
    read -p "Update existing secret? (y/N): " update_secret

    if [[ "$update_secret" =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}Adding new secret version...${NC}"
        echo -n "$HF_TOKEN" | gcloud secrets versions add "${HF_SECRET_NAME}" \
            --data-file=- \
            --project="${PROJECT_ID}"
        echo -e "${GREEN}Secret updated successfully!${NC}"
    else
        echo -e "${YELLOW}Using existing secret${NC}"
    fi
else
    # Create new secret
    echo -e "${GREEN}Creating new secret: ${HF_SECRET_NAME}${NC}"
    echo -n "$HF_TOKEN" | gcloud secrets create "${HF_SECRET_NAME}" \
        --data-file=- \
        --replication-policy="automatic" \
        --project="${PROJECT_ID}"
    echo -e "${GREEN}Secret created successfully!${NC}"
fi

# Grant access to model downloader service account
echo -e "\n${GREEN}Granting access to model downloader service account...${NC}"

MODEL_DOWNLOAD_GSA="model-downloader@${PROJECT_ID}.iam.gserviceaccount.com"

# Check if service account exists
if ! gcloud iam service-accounts describe "${MODEL_DOWNLOAD_GSA}" \
    --project="${PROJECT_ID}" &>/dev/null; then
    echo -e "${YELLOW}Service account not found: ${MODEL_DOWNLOAD_GSA}${NC}"
    echo -e "${YELLOW}Run ./02-setup-infrastructure.sh first${NC}"
else
    gcloud secrets add-iam-policy-binding "${HF_SECRET_NAME}" \
        --member="serviceAccount:${MODEL_DOWNLOAD_GSA}" \
        --role="roles/secretmanager.secretAccessor" \
        --project="${PROJECT_ID}"

    echo -e "${GREEN}Access granted to ${MODEL_DOWNLOAD_GSA}${NC}"
fi

# Create Kubernetes secret for direct pod access (alternative method)
echo -e "\n${GREEN}Creating Kubernetes secret (alternative access method)...${NC}"

if kubectl get secret huggingface-token -n model-download &>/dev/null; then
    echo -e "${YELLOW}Kubernetes secret already exists${NC}"
    kubectl delete secret huggingface-token -n model-download
fi

kubectl create secret generic huggingface-token \
    -n model-download \
    --from-literal=token="$HF_TOKEN"

echo -e "${GREEN}Kubernetes secret created in model-download namespace${NC}"

# Test secret access
echo -e "\n${GREEN}Testing secret access...${NC}"

LATEST_VERSION=$(gcloud secrets versions list "${HF_SECRET_NAME}" \
    --project="${PROJECT_ID}" \
    --format="value(name)" \
    --limit=1)

if [ -n "$LATEST_VERSION" ]; then
    echo -e "${GREEN}✓ Secret accessible. Latest version: ${LATEST_VERSION}${NC}"
else
    echo -e "${RED}✗ Unable to access secret${NC}"
    exit 1
fi

# Display model access instructions
cat << 'EOF'

=== Hugging Face Model Access Instructions ===

To download models, you need to accept the model licenses:

1. Gemma Models:
   - Visit: https://www.kaggle.com/models/google/gemma
   - Accept terms with your Hugging Face account

2. Llama Models:
   - Visit: https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct
   - Accept terms on the model page

3. Other Models:
   - Check individual model pages for license requirements

EOF

echo -e "${GREEN}Hugging Face setup complete!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Accept model licenses (see instructions above)"
echo -e "  2. Download a model: ./04-download-model.sh"
