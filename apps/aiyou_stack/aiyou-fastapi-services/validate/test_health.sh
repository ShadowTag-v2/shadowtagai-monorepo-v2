#!/bin/bash
# Health check script for Judge 6 deployment
# Tests basic endpoint availability before latency testing

set -e

ENDPOINT="${ENDPOINT:-http://Cor.Claude_Code_6.pnkln.svc.cluster.local}"
MAX_RETRIES=30
RETRY_DELAY=5

echo "🏥 Health Check for Judge 6"
echo "================================"
echo "Endpoint: $ENDPOINT"
echo ""

# Function to check health
check_health() {
    local retry=0

    while [ $retry -lt $MAX_RETRIES ]; do
        echo -n "Attempt $((retry + 1))/$MAX_RETRIES: "

        if curl -sf "$ENDPOINT/health" > /dev/null 2>&1; then
            echo "✅ Healthy"
            return 0
        else
            echo "❌ Not ready"
            ((retry++))

            if [ $retry -lt $MAX_RETRIES ]; then
                echo "   Waiting ${RETRY_DELAY}s before retry..."
                sleep $RETRY_DELAY
            fi
        fi
    done

    echo ""
    echo "❌ Health check failed after $MAX_RETRIES attempts"
    return 1
}

# Run health check
if check_health; then
    echo ""
    echo "✅ Service is healthy and ready for testing"
    echo ""

    # Show service info
    echo "📊 Service Information:"
    curl -s "$ENDPOINT/health" | python3 -m json.tool || echo "Could not parse health response"

    exit 0
else
    echo ""
    echo "💡 Troubleshooting steps:"
    echo "   1. Check pods: kubectl get pods -n pnkln"
    echo "   2. Check logs: kubectl logs -n pnkln -l app=Cor.Claude_Code_6"
    echo "   3. Check service: kubectl get svc -n pnkln Cor.Claude_Code_6"
    echo ""
    exit 1
fi
