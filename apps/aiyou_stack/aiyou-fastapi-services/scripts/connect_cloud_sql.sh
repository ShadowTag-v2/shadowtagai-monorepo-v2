#!/bin/bash
set -e

# Cloud SQL Connection Helper
# Usage: ./scripts/connect_cloud_sql.sh [INSTANCE_NAME] [LOCAL_PORT]

PROJECT_ID="acquired-jet-478701-b3"
REGION="us-central1"
DEFAULT_INSTANCE="ShadowTag-v2-mysql-primary" # Update this to your actual instance name
INSTANCE_NAME="${1:-$DEFAULT_INSTANCE}"
LOCAL_PORT="${2:-3306}"

echo "============================================================"
echo "Cloud SQL Connection Helper"
echo "Project: $PROJECT_ID"
echo "Instance: $INSTANCE_NAME"
echo "============================================================"

# Check for gcloud
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI is not installed."
    exit 1
fi

# Check for cloud-sql-proxy
if command -v cloud-sql-proxy &> /dev/null; then
    echo "✅ Found cloud-sql-proxy. Starting proxy on port $LOCAL_PORT..."
    echo "Connection string: $PROJECT_ID:$REGION:$INSTANCE_NAME"
    echo "Run this command in a separate terminal to connect:"
    echo "  mysql -u [USER] -p --host 127.0.0.1 --port $LOCAL_PORT"

    cloud-sql-proxy "$PROJECT_ID:$REGION:$INSTANCE_NAME" --port "$LOCAL_PORT"
else
    echo "⚠️ 'cloud-sql-proxy' not found. Falling back to 'gcloud sql connect'."
    echo "This method whitelists your IP temporarily."

    echo "Connecting to $INSTANCE_NAME..."
    gcloud sql connect "$INSTANCE_NAME" --user=root --quiet
fi
