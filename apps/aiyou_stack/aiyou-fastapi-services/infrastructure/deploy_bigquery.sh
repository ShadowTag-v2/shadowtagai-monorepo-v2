#!/bin/bash
# Pnkln Tower-Edge Pilot - BigQuery Deployment Script
# Usage: ./deploy_bigquery.sh

set -e

# Configuration
PROJECT_ID=$(gcloud config get-value project)
DATASET="pnkln_intelligence"
SCHEMA_FILE="infrastructure/bigquery_tower.sql"

echo "///▞ BILLING :: Tower-Edge Pilot BigQuery Deployment"
echo "Project: $PROJECT_ID"
echo "Dataset: $DATASET"
echo "Schema:  $SCHEMA_FILE"

# 1. Check Authentication
echo "///▞ AUTH :: Verifying credentials..."
if ! gcloud auth print-access-token >/dev/null 2>&1; then
    echo "Error: Not authenticated. Please run 'gcloud auth login' first."
    exit 1
fi

# 2. Create Dataset (if not exists)
echo "///▞ DATASET :: Checking/Creating $DATASET..."
if bq ls --dataset "$PROJECT_ID:$DATASET" >/dev/null 2>&1; then
    echo "Dataset $DATASET already exists."
else
    bq mk --dataset --description "Pnkln Tower-Edge Telemetry" --location=US "$PROJECT_ID:$DATASET"
    echo "Dataset $DATASET created."
fi

# 3. Apply Schema (create table)
echo "///▞ SCHEMA :: Applying $SCHEMA_FILE..."
bq query --use_legacy_sql=false --project_id="$PROJECT_ID" < "$SCHEMA_FILE"

echo "///▞ SUCCESS :: Deployment complete. Telemetry ready."
