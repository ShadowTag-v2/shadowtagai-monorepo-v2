#!/bin/bash

# Health Check Script
# Tests if the application is running and healthy

HEALTH_URL="${1:-http://localhost:8000/health}"
MAX_RETRIES="${2:-30}"
RETRY_DELAY="${3:-2}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "🔍 Checking health at $HEALTH_URL"

for i in $(seq 1 "$MAX_RETRIES"); do
    # Try to connect to health endpoint
    response=$(curl -f -s -w "%{http_code}" -o /dev/null "$HEALTH_URL" 2>/dev/null || echo "000")

    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✅ Application is healthy!${NC}"
        echo "   HTTP Status: $response"
        echo "   URL: $HEALTH_URL"
        exit 0
    fi

    echo -e "${YELLOW}⏳ Attempt $i/$MAX_RETRIES failed (HTTP $response), retrying in ${RETRY_DELAY}s...${NC}"
    sleep "$RETRY_DELAY"
done

echo -e "${RED}❌ Health check failed after $MAX_RETRIES attempts${NC}"
echo "   Last HTTP Status: $response"
echo "   URL: $HEALTH_URL"
exit 1
