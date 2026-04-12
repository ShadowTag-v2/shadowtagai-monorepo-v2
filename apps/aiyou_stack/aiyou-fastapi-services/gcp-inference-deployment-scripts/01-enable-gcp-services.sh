#!/bin/bash
# Enable required GCP services for GKE Inference
# Based on: GoogleCloudPlatform/accelerated-platforms inference-ref-arch

set -euo pipefail

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== Enabling GCP Services ===${NC}"

# Check required environment variables
if [ -z "${PROJECT_ID:-}" ]; then
    echo -e "${RED}Error: PROJECT_ID not set. Run: source .env.gcp-inference${NC}"
    exit 1
fi

echo -e "${YELLOW}Project: ${PROJECT_ID}${NC}"

# List of required services
REQUIRED_SERVICES=(
    "compute.googleapis.com"                    # Compute Engine
    "container.googleapis.com"                  # GKE
    "storage.googleapis.com"                    # Cloud Storage
    "storage-api.googleapis.com"                # Cloud Storage API
    "artifactregistry.googleapis.com"           # Artifact Registry
    "cloudbuild.googleapis.com"                 # Cloud Build
    "cloudresourcemanager.googleapis.com"       # Resource Manager
    "iam.googleapis.com"                        # IAM
    "iamcredentials.googleapis.com"             # IAM Credentials
    "secretmanager.googleapis.com"              # Secret Manager
    "monitoring.googleapis.com"                 # Cloud Monitoring
    "logging.googleapis.com"                    # Cloud Logging
    "stackdriver.googleapis.com"                # Stackdriver
    "cloudtrace.googleapis.com"                 # Cloud Trace
    "servicenetworking.googleapis.com"          # Service Networking
    "dns.googleapis.com"                        # Cloud DNS
    "gkeconnect.googleapis.com"                 # GKE Connect
    "gkehub.googleapis.com"                     # GKE Hub
    "anthos.googleapis.com"                     # Anthos
    "mesh.googleapis.com"                       # Service Mesh
    "multiclusterservicediscovery.googleapis.com"  # Multi-cluster Service Discovery
    "multiclusteringress.googleapis.com"        # Multi-cluster Ingress
    "trafficdirector.googleapis.com"            # Traffic Director
    "networkservices.googleapis.com"            # Network Services
    "certificatemanager.googleapis.com"         # Certificate Manager
)

# Enable billing (if not already enabled)
echo -e "\n${YELLOW}Checking billing status...${NC}"
BILLING_ENABLED=$(gcloud beta billing projects describe "${PROJECT_ID}" \
    --format="value(billingEnabled)" 2>/dev/null || echo "false")

if [ "$BILLING_ENABLED" = "false" ]; then
    echo -e "${RED}Warning: Billing is not enabled for this project.${NC}"
    echo -e "${YELLOW}Please enable billing at: https://console.cloud.google.com/billing/${NC}"
    read -p "Press Enter after enabling billing to continue..."
fi

# Enable services
echo -e "\n${GREEN}Enabling required services...${NC}"
echo -e "${YELLOW}This may take several minutes...${NC}\n"

for service in "${REQUIRED_SERVICES[@]}"; do
    echo -e "${YELLOW}Enabling: ${service}${NC}"
    gcloud services enable "$service" \
        --project="${PROJECT_ID}" \
        2>&1 | grep -v "already enabled" || true
done

echo -e "\n${GREEN}Waiting for services to be fully enabled...${NC}"
sleep 10

# Verify all services are enabled
echo -e "\n${GREEN}Verifying services...${NC}"
FAILED_SERVICES=()

for service in "${REQUIRED_SERVICES[@]}"; do
    if gcloud services list --enabled \
        --project="${PROJECT_ID}" \
        --filter="name:${service}" \
        --format="value(name)" | grep -q "${service}"; then
        echo -e "${GREEN}✓ ${service}${NC}"
    else
        echo -e "${RED}✗ ${service}${NC}"
        FAILED_SERVICES+=("$service")
    fi
done

if [ ${#FAILED_SERVICES[@]} -gt 0 ]; then
    echo -e "\n${RED}Failed to enable the following services:${NC}"
    printf '%s\n' "${FAILED_SERVICES[@]}"
    exit 1
fi

echo -e "\n${GREEN}All required services are enabled!${NC}"

# Check GPU quota
echo -e "\n${GREEN}=== Checking GPU Quota ===${NC}"
REGION=${REGION:-us-central1}

echo -e "${YELLOW}Checking quota for common GPUs in region: ${REGION}${NC}"

# List of GPU types to check
GPU_TYPES=(
    "NVIDIA_L4"
    "NVIDIA_TESLA_T4"
    "NVIDIA_H100"
    "NVIDIA_A100"
)

for gpu in "${GPU_TYPES[@]}"; do
    QUOTA=$(gcloud compute project-info describe \
        --project="${PROJECT_ID}" \
        --format="value(quotas.filter(metric:${gpu}).filter(region:${REGION}).limit)" \
        2>/dev/null || echo "0")

    if [ "$QUOTA" != "0" ] && [ -n "$QUOTA" ]; then
        echo -e "${GREEN}✓ ${gpu}: ${QUOTA} GPUs available${NC}"
    else
        echo -e "${YELLOW}! ${gpu}: No quota or quota is 0${NC}"
    fi
done

echo -e "\n${YELLOW}Note: If you need more GPU quota, request it at:${NC}"
echo -e "${YELLOW}https://console.cloud.google.com/iam-admin/quotas?project=${PROJECT_ID}${NC}"

# Create service accounts
echo -e "\n${GREEN}=== Creating Service Accounts ===${NC}"

# GKE node service account
GKE_SA_NAME="gke-inference-sa"
GKE_SA_EMAIL="${GKE_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

if gcloud iam service-accounts describe "${GKE_SA_EMAIL}" \
    --project="${PROJECT_ID}" &>/dev/null; then
    echo -e "${YELLOW}Service account already exists: ${GKE_SA_EMAIL}${NC}"
else
    echo -e "${GREEN}Creating service account: ${GKE_SA_EMAIL}${NC}"
    gcloud iam service-accounts create "${GKE_SA_NAME}" \
        --display-name="GKE Inference Node Service Account" \
        --project="${PROJECT_ID}"
fi

# Grant required roles to service account
echo -e "\n${GREEN}Granting IAM roles to service account...${NC}"

REQUIRED_ROLES=(
    "roles/logging.logWriter"
    "roles/monitoring.metricWriter"
    "roles/monitoring.viewer"
    "roles/stackdriver.resourceMetadata.writer"
    "roles/storage.objectViewer"
    "roles/artifactregistry.reader"
)

for role in "${REQUIRED_ROLES[@]}"; do
    echo -e "${YELLOW}Granting ${role}...${NC}"
    gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
        --member="serviceAccount:${GKE_SA_EMAIL}" \
        --role="${role}" \
        --condition=None \
        2>&1 | grep -v "already exists" || true
done

echo -e "\n${GREEN}GCP services setup complete!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Review GPU quota allocation"
echo -e "  2. Run: ./02-setup-infrastructure.sh"
