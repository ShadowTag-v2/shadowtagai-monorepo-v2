#!/bin/bash
set -e

BASE_URL="http://localhost:8000"

echo "=== Testing Pnkln File Search Local Instance ==="
echo ""

echo "1. Root endpoint..."
curl -s ${BASE_URL}/ | jq .
echo ""

echo "2. Health check..."
curl -s ${BASE_URL}/health | jq .
echo ""

echo "3. Liveness check..."
curl -s ${BASE_URL}/health/live | jq .
echo ""

echo "4. List verticals (first 3)..."
curl -s ${BASE_URL}/api/v1/verticals | jq '.[0:3]'
echo ""

echo "5. Get defense vertical..."
curl -s ${BASE_URL}/api/v1/verticals/defense | jq .
echo ""

echo "6. Test query (defense)..."
curl -s -X POST ${BASE_URL}/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Can we share classified information with contractors?",
    "vertical": "defense"
  }' | jq '.enforcement, .timing'
echo ""

echo "7. Test query (healthcare)..."
curl -s -X POST ${BASE_URL}/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Can we share patient data with insurance company?",
    "vertical": "healthcare"
  }' | jq '.enforcement, .timing'
echo ""

echo "8. Kill switch status..."
curl -s ${BASE_URL}/api/v1/monitoring/health | jq '.state, .healthy'
echo ""

echo "9. Prometheus metrics (sample)..."
curl -s ${BASE_URL}/metrics | grep -E "file_search_latency|judge_layer1" | head -5
echo ""

echo "=== All tests complete! ==="
