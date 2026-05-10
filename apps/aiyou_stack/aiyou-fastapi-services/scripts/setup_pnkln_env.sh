#!/bin/bash
# setup_pnkln_env.sh - PNKLN Environment Setup
#
# Sets up the complete PNKLN (Pipeline) infrastructure:
# - GCP services enablement
# - GCS bucket creation
# - Pub/Sub topics for event messaging
# - Cloud Scheduler jobs for automated workflows
# - BigQuery datasets and tables
# - Policy configuration
#
# Usage: ./setup_pnkln_env.sh [--dry-run]

set -euo pipefail

# Configuration - can be overridden via environment variables
export PNKLN_PROJECT="${PNKLN_PROJECT:-pnkln-proj}"
export PNKLN_REGION="${PNKLN_REGION:-us-central1}"
export PNKLN_BUCKET="${PNKLN_BUCKET:-pnkln-os}"
export PNKLN_DATASET="${PNKLN_DATASET:-pnkln_os}"
export TIME_ZONE="${TIME_ZONE:-America/Los_Angeles}"

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
    echo "🔍 DRY RUN: Commands will be printed but not executed."
fi

log() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] $1"
}

run_cmd() {
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "DRY_RUN: $*"
    else
        log "Executing: $*"
        eval "$*" || { log "ERROR: Command failed: $*"; exit 1; }
    fi
}

# 1. Environment & Project Config
log "🚀 Setting up PNKLN Environment for project: $PNKLN_PROJECT"
if [[ "$DRY_RUN" == "false" ]]; then
    run_cmd "gcloud config set project $PNKLN_PROJECT"
    run_cmd "gcloud config set compute/region $PNKLN_REGION"
fi

# 2. Enable Services
log "🔌 Enabling GCP Services..."
SERVICES=(
    aiplatform.googleapis.com
    bigquery.googleapis.com
    cloudscheduler.googleapis.com
    workflows.googleapis.com
    pubsub.googleapis.com
    run.googleapis.com
    cloudfunctions.googleapis.com
)
run_cmd "gcloud services enable ${SERVICES[*]}"

# 3. Storage
log "🪣 Creating GCS Bucket..."
run_cmd "gsutil mb -l $PNKLN_REGION -p $PNKLN_PROJECT gs://$PNKLN_BUCKET || true"

# 4. Pub/Sub Topics
log "msg Creating Pub/Sub Topics..."
TOPICS=(
    "pnkln.reg_update"
    "pnkln.weak_signal"
    "pnkln.finance_brief"
    "pnkln.family_booster"
)
for topic in "${TOPICS[@]}"; do
    run_cmd "gcloud pubsub topics create $topic || true"
done

# 5. Cloud Scheduler Jobs
log "⏰ Creating Scheduler Jobs..."
# Finance Brief: Daily at 13:00
run_cmd "gcloud scheduler jobs create pubsub pnkln-finance-brief \
    --schedule='0 13 * * *' \
    --topic=pnkln.finance_brief \
    --message-body='{\"run\":\"daily_finance\"}' \
    --time-zone='$TIME_ZONE' || true"

# Weak Signal: Weekdays at 12:15
run_cmd "gcloud scheduler jobs create pubsub pnkln-weak-signal \
    --schedule='15 12 * * 1-5' \
    --topic=pnkln.weak_signal \
    --message-body='{\"scan\":\"sewa\"}' \
    --time-zone='$TIME_ZONE' || true"

# Family Booster: Daily at 06:30
run_cmd "gcloud scheduler jobs create pubsub pnkln-family-boost \
    --schedule='30 6 * * *' \
    --topic=pnkln.family_booster \
    --message-body='{\"boost\":\"am\"}' \
    --time-zone='$TIME_ZONE' || true"

# 6. Dependencies
log "📦 Installing Python Dependencies..."
run_cmd "pip install --quiet google-cloud-aiplatform google-cloud-pubsub google-cloud-bigquery pandas numpy orjson prophet"

# 7. BigQuery Datasets & Tables
log "📊 Setting up BigQuery..."
run_cmd "bq mk --dataset $PNKLN_PROJECT:$PNKLN_DATASET || true"

TASKS=(
    "bq mk --table $PNKLN_PROJECT:$PNKLN_DATASET.finance_daily date:DATE,cash:STRING,ar:STRING,ap:STRING,burn:STRING,runway:STRING,f30:STRING,f90:STRING,flags:STRING || true"
    "bq mk --table $PNKLN_PROJECT:$PNKLN_DATASET.reg_updates ts:TIMESTAMP,jsd:STRING,src:STRING,sum:STRING,impact:STRING,actions:STRING || true"
    "bq mk --table $PNKLN_PROJECT:$PNKLN_DATASET.weak_signals ts:TIMESTAMP,dom:STRING,topic:STRING,prob:FLOAT,imp:FLOAT,ttm:INT64,notes:STRING,acts:STRING || true"
    "bq mk --table $PNKLN_PROJECT:$PNKLN_DATASET.family_msgs ts:TIMESTAMP,to_:STRING,msg:STRING,meta:STRING || true"
)

for task in "${TASKS[@]}"; do
    run_cmd "$task"
done

# 8. Policy Configuration
log "📝 generating Policy Configuration..."
# This part is handled by Python script creation in the main plan, but we can ensure the dir exists
CONFIG_DIR="pnkln_intelligence/config"
run_cmd "mkdir -p $CONFIG_DIR"

log "✅ PNKLN Environment Setup Complete!"
