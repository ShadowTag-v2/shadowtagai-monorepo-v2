#!/bin/bash
# Vertex AI Workbench Setup Script

set -e

PROJECT_ID=${GCP_PROJECT_ID:-"your-project-id"}
REGION=${GCP_REGION:-"us-central1"}
INSTANCE_NAME="cor17-workbench"
MACHINE_TYPE="n1-standard-4"
BOOT_DISK_SIZE="100GB"

echo "🚀 Setting up Vertex AI Workbench for Cor.17"

# Set project
gcloud config set project $PROJECT_ID

# Enable Notebooks API
echo "📦 Enabling Notebooks API..."
gcloud services enable notebooks.googleapis.com

# Create Workbench instance
echo "💻 Creating Vertex AI Workbench instance..."
gcloud notebooks instances create $INSTANCE_NAME \
    --location=$REGION-a \
    --machine-type=$MACHINE_TYPE \
    --boot-disk-size=$BOOT_DISK_SIZE \
    --boot-disk-type=PD_SSD \
    --install-gpu-driver \
    --framework=PyTorch \
    --metadata="proxy-mode=service_account"

echo "✅ Vertex AI Workbench instance created!"
echo ""
echo "Access your instance:"
echo "  gcloud notebooks instances describe $INSTANCE_NAME --location=$REGION-a"
echo ""
echo "Upload notebooks:"
echo "  Upload files from ./notebooks/ directory to your Workbench instance"
