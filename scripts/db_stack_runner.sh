#!/bin/bash
# Database Stack Runner - ShadowTagAi
# Discovers and spins up all database tools across the stack

set -e

PROJECT_ID="${GCP_PROJECT_ID:-acquired-jet-478701-b3}"
REGION="${GCP_REGION:-us-central1}"
GCLOUD="/Users/pikeymickey/google-cloud-sdk/bin/gcloud"

echo "///▞ DATABASE STACK RUNNER"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "========================================="
echo ""

# Check if gcloud is available
if [ ! -f "$GCLOUD" ]; then
    GCLOUD="gcloud"
fi

# 1. Cloud SQL Instances
echo "///▞ CLOUD SQL INSTANCES"
SQL_INSTANCES=$($GCLOUD sql instances list --project=$PROJECT_ID --format="table(name,databaseVersion,state,primaryAddress)" 2>/dev/null || echo "NONE")
if [ "$SQL_INSTANCES" = "NONE" ] || [ -z "$SQL_INSTANCES" ]; then
    echo "  Status: No Cloud SQL instances found"
    echo "  Action: Run 'gcloud sql instances create shadowtagai-db --database-version=POSTGRES_15 --tier=db-f1-micro --region=$REGION'"
else
    echo "$SQL_INSTANCES"
fi
echo ""

# 2. BigQuery Datasets
echo "///▞ BIGQUERY DATASETS"
BQ_DATASETS=$($GCLOUD alpha bq datasets list --project=$PROJECT_ID --format="table(datasetId,location)" 2>/dev/null || echo "NONE")
if [ "$BQ_DATASETS" = "NONE" ] || [ -z "$BQ_DATASETS" ]; then
    echo "  Status: No BigQuery datasets found"
    echo "  Action: Run 'bq mk --dataset $PROJECT_ID:shadowtagai_analytics'"
else
    echo "$BQ_DATASETS"
fi
echo ""

# 3. Firestore
echo "///▞ FIRESTORE"
FIRESTORE=$($GCLOUD firestore databases list --project=$PROJECT_ID --format="table(name,type,locationId)" 2>/dev/null || echo "NONE")
if [ "$FIRESTORE" = "NONE" ] || [ -z "$FIRESTORE" ]; then
    echo "  Status: Firestore not configured"
    echo "  Action: Run 'gcloud firestore databases create --location=$REGION'"
else
    echo "$FIRESTORE"
fi
echo ""

# 4. Cloud Storage Buckets (for governance traces)
echo "///▞ CLOUD STORAGE BUCKETS"
BUCKETS=$($GCLOUD storage buckets list --project=$PROJECT_ID --format="table(name,location)" 2>/dev/null | grep -E "shadowtag|governance|audit" || echo "NONE")
if [ "$BUCKETS" = "NONE" ] || [ -z "$BUCKETS" ]; then
    echo "  Status: No ShadowTagAi buckets found"
    echo "  Action: Run 'gcloud storage buckets create gs://shadowtagai-governance-traces --location=$REGION'"
else
    echo "$BUCKETS"
fi
echo ""

# 5. Redis/Memorystore
echo "///▞ MEMORYSTORE (Redis)"
REDIS=$($GCLOUD redis instances list --region=$REGION --project=$PROJECT_ID --format="table(name,tier,memorySizeGb,host,port)" 2>/dev/null || echo "NONE")
if [ "$REDIS" = "NONE" ] || [ -z "$REDIS" ]; then
    echo "  Status: No Redis instances found"
    echo "  Action: Run 'gcloud redis instances create shadowtagai-cache --size=1 --region=$REGION'"
else
    echo "$REDIS"
fi
echo ""

# 6. Local Docker Databases
echo "///▞ LOCAL DOCKER DATABASES"
if command -v docker &> /dev/null; then
    DOCKER_DBS=$(docker ps --filter "name=postgres\|redis\|mongo" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "NONE")
    if [ "$DOCKER_DBS" = "NONE" ] || [ -z "$DOCKER_DBS" ]; then
        echo "  Status: No local database containers running"
        echo "  Action: Use docker-compose.db.yml or run:"
        echo "    docker run -d --name shadowtagai-postgres -e POSTGRES_PASSWORD=dev -p 5432:5432 postgres:15"
        echo "    docker run -d --name shadowtagai-redis -p 6379:6379 redis:7"
    else
        echo "$DOCKER_DBS"
    fi
else
    echo "  Status: Docker not installed"
fi
echo ""

# 7. Connection Strings Summary
echo "///▞ CONNECTION STRINGS"
echo "========================================="

# Cloud SQL connection (if exists)
SQL_INSTANCE_NAME=$($GCLOUD sql instances list --project=$PROJECT_ID --format="value(name)" --limit=1 2>/dev/null || echo "")
if [ -n "$SQL_INSTANCE_NAME" ]; then
    SQL_IP=$($GCLOUD sql instances describe $SQL_INSTANCE_NAME --project=$PROJECT_ID --format="value(ipAddresses[0].ipAddress)" 2>/dev/null || echo "")
    echo "Cloud SQL: postgresql://REDACTED_USER:REDACTED_PASS@$SQL_IP:5432/shadowtagai"
fi

# BigQuery
echo "BigQuery: bq://$PROJECT_ID/shadowtagai_analytics"

# Firestore
echo "Firestore: projects/$PROJECT_ID/databases/(default)"

# Local Dev
echo "Local PostgreSQL: postgresql://REDACTED_USER:REDACTED_PASS@localhost:5432/shadowtagai"
echo "Local Redis: redis://localhost:6379"

echo ""
echo "///▞ STACK RUNNER COMPLETE"
