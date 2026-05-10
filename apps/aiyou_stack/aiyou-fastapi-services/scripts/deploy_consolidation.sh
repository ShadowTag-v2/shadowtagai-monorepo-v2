#!/bin/bash
# ==============================================================================
# 🚀 MASSIVE CONSOLIDATION DEPLOYER
# ==============================================================================
# 1. Deploys Infra (Terraform)
# 2. Submits Dataflow Job
# ==============================================================================

set -e

PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
TOPIC="projects/$PROJECT_ID/locations/$REGION/clusters/omega-kafka-cluster/topics/shadowtag-events-v1"
TABLE="$PROJECT_ID:velocity_lake.events_v1"
# Note: Bootstrap servers endpoint needs to be retrieved dynamically after TF apply
# For now, we assume a placeholder or require manual input.
BOOTSTRAP_SERVERS="bootstrap.omega-kafka-cluster.$REGION.managedkafka.$PROJECT_ID.cloud.goog:9092"

echo ">>> 🏗️  Applying Infrastructure..."
cd infra/terraform
terraform init
terraform apply -auto-approve
cd ../..

echo ">>> 🌊 Submitting Dataflow Job..."
# Ensure API is enabled
gcloud services enable dataflow.googleapis.com managedkafka.googleapis.com

python3 src/pipeline/consolidation_beam.py \
  --project $PROJECT_ID \
  --region $REGION \
  --runner DataflowRunner \
  --temp_location gs://$PROJECT_ID-dataflow-temp/ \
  --input_topic $TOPIC \
  --bootstrap_servers $BOOTSTRAP_SERVERS \
  --output_table $TABLE

echo ">>> ✅ Consolidation Pipeline Deployed."
