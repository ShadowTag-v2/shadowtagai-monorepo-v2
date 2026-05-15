#!/bin/bash
#
# Kubernetes Secrets Configuration Script
# Creates all required secrets for PNKLN Core Stack
#
# Usage: ./scripts/configure_secrets.sh
#
# Required environment variables:
#   - DB_USER, DB_PASSWORD (PostgreSQL)
#   - YOUTUBE_API_KEY (YouTube Data API v3)
#   - TWITTER_BEARER_TOKEN (Twitter API v2)
#   - ANTHROPIC_API_KEY (Claude)
#   - OPENAI_API_KEY (GPT-4)
#   - GOOGLE_API_KEY (Gemini)
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  PNKLN CORE STACK™ - SECRETS CONFIGURATION             ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}\n"

# Function to check if variable is set
check_var() {
    local var_name=$1
    local required=$2

    if [ -z "${!var_name}" ]; then
        if [ "$required" = "true" ]; then
            echo -e "${RED}✗ Error: $var_name not set${NC}"
            return 1
        else
            echo -e "${YELLOW}⚠ Warning: $var_name not set (optional)${NC}"
            return 0
        fi
    else
        echo -e "${GREEN}✓ $var_name is set${NC}"
        return 0
    fi
}

# Validate required variables
echo -e "${CYAN}Validating environment variables...${NC}\n"

all_set=true

# Database credentials (required)
check_var "DB_USER" "true" || all_set=false
check_var "DB_PASSWORD" "true" || all_set=false

# API keys for ingestion (at least one required)
check_var "YOUTUBE_API_KEY" "false"
check_var "TWITTER_BEARER_TOKEN" "false"

# LLM API keys (at least one required for orchestrator)
check_var "ANTHROPIC_API_KEY" "false"
check_var "OPENAI_API_KEY" "false"
check_var "GOOGLE_API_KEY" "false"

if [ "$all_set" = false ]; then
    echo -e "\n${RED}Error: Required environment variables missing${NC}"
    echo -e "${YELLOW}Please set the following before running this script:${NC}"
    echo "  export DB_USER=your_db_user"
    echo "  export DB_PASSWORD=your_db_password"
    echo "  export YOUTUBE_API_KEY=your_youtube_key  # Optional but recommended"
    echo "  export TWITTER_BEARER_TOKEN=your_twitter_token  # Optional"
    echo "  export ANTHROPIC_API_KEY=your_claude_key  # At least one LLM API key required"
    echo "  export OPENAI_API_KEY=your_openai_key"
    echo "  export GOOGLE_API_KEY=your_gemini_key"
    exit 1
fi

echo -e "\n${GREEN}✓ All required variables set${NC}\n"

# Create PostgreSQL secret (storage namespace)
echo -e "${CYAN}[1/3] Creating PostgreSQL secret...${NC}"

kubectl create secret generic postgres-secret \
    --from-literal=username="$DB_USER" \
    --from-literal=password="$DB_PASSWORD" \
    --namespace=storage \
    --dry-run=client -o yaml | kubectl apply -f -

echo -e "${GREEN}✓ PostgreSQL secret created in namespace: storage${NC}\n"

# Create crawler secrets (ingestion namespace)
echo -e "${CYAN}[2/3] Creating crawler API secrets...${NC}"

# Build kubectl command dynamically based on available keys
CRAWLER_SECRET_CMD="kubectl create secret generic crawler-secrets --namespace=ingestion"

if [ -n "$YOUTUBE_API_KEY" ]; then
    CRAWLER_SECRET_CMD="$CRAWLER_SECRET_CMD --from-literal=youtube_api_key=$YOUTUBE_API_KEY"
fi

if [ -n "$TWITTER_BEARER_TOKEN" ]; then
    CRAWLER_SECRET_CMD="$CRAWLER_SECRET_CMD --from-literal=twitter_bearer_token=$TWITTER_BEARER_TOKEN"
fi

# Execute with dry-run and apply
CRAWLER_SECRET_CMD="$CRAWLER_SECRET_CMD --dry-run=client -o yaml"
eval "$CRAWLER_SECRET_CMD" | kubectl apply -f -

echo -e "${GREEN}✓ Crawler secrets created in namespace: ingestion${NC}\n"

# Create LLM secrets (orchestrator namespace)
echo -e "${CYAN}[3/3] Creating LLM API secrets...${NC}"

LLM_SECRET_CMD="kubectl create secret generic llm-secrets --namespace=orchestrator"

if [ -n "$ANTHROPIC_API_KEY" ]; then
    LLM_SECRET_CMD="$LLM_SECRET_CMD --from-literal=anthropic_key=$ANTHROPIC_API_KEY"
fi

if [ -n "$OPENAI_API_KEY" ]; then
    LLM_SECRET_CMD="$LLM_SECRET_CMD --from-literal=openai_key=$OPENAI_API_KEY"
fi

if [ -n "$GOOGLE_API_KEY" ]; then
    LLM_SECRET_CMD="$LLM_SECRET_CMD --from-literal=google_key=$GOOGLE_API_KEY"
fi

LLM_SECRET_CMD="$LLM_SECRET_CMD --dry-run=client -o yaml"
eval "$LLM_SECRET_CMD" | kubectl apply -f -

echo -e "${GREEN}✓ LLM secrets created in namespace: orchestrator${NC}\n"

# Verify secrets
echo -e "${CYAN}Verifying secrets...${NC}\n"

echo -e "${GREEN}Storage namespace:${NC}"
kubectl get secrets -n storage

echo -e "\n${GREEN}Ingestion namespace:${NC}"
kubectl get secrets -n ingestion

echo -e "\n${GREEN}Orchestrator namespace:${NC}"
kubectl get secrets -n orchestrator

echo -e "\n${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✓ SECRETS CONFIGURATION COMPLETE                       ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}\n"

echo -e "${CYAN}Next steps:${NC}"
echo "1. Deploy PostgreSQL: kubectl apply -f k8s/storage/postgresql.yaml"
echo "2. Deploy ingestion CronJob: kubectl apply -f k8s/ingestion/"
echo "3. Deploy orchestrator: kubectl apply -f k8s/orchestrator/"
echo ""
echo -e "${YELLOW}Security note: Secrets are base64 encoded, not encrypted at rest by default.${NC}"
echo -e "${YELLOW}For production, consider using GCP Secret Manager or Sealed Secrets.${NC}"
