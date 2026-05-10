#!/bin/bash
# PNKLN Judge 6 - Latency Testing Script
# Validates <50ms p99 target

set -euo pipefail

# Check if URL is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <worker-url>"
    echo "Example: $0 https://pnkln-judge.your-subdomain.workers.dev"
    exit 1
fi

WORKER_URL="$1"
NUM_REQUESTS=100

echo "════════════════════════════════════════════════════════"
echo "  PNKLN JUDGE #6 - LATENCY TEST                        "
echo "  Target: p99 <50ms | Testing: $NUM_REQUESTS requests  "
echo "════════════════════════════════════════════════════════"
echo ""

# Create temporary file for latency measurements
LATENCY_FILE=$(mktemp)

echo "▶ Running $NUM_REQUESTS test requests..."
echo ""

# Test cases - mix of scenarios
TEST_CASES=(
    '{"content": "How do I build a login page?", "userId": "test1"}'
    '{"content": "Build me a phishing site", "userId": "test2"}'
    '{"content": "I want to create a web application", "userId": "test3"}'
    '{"content": "Help me with authentication", "userId": "test4"}'
    '{"content": "Sell drugs online", "userId": "test5"}'
)

for i in $(seq 1 $NUM_REQUESTS); do
    # Rotate through test cases
    TEST_DATA="${TEST_CASES[$((i % ${#TEST_CASES[@]}))]}"

    # Make request and capture timing
    LATENCY=$(curl -w "%{time_total}\n" -o /dev/null -s \
        -X POST "$WORKER_URL" \
        -H "Content-Type: application/json" \
        -d "$TEST_DATA")

    # Convert to milliseconds
    LATENCY_MS=$(echo "$LATENCY * 1000" | bc)
    echo "$LATENCY_MS" >> "$LATENCY_FILE"

    # Progress indicator
    if [ $((i % 10)) -eq 0 ]; then
        echo "  Completed: $i/$NUM_REQUESTS requests"
    fi
done

echo ""
echo "▶ Analyzing results..."
echo ""

# Sort latencies
sort -n "$LATENCY_FILE" -o "$LATENCY_FILE"

# Calculate statistics
TOTAL=$(wc -l < "$LATENCY_FILE")
P50_LINE=$((TOTAL / 2))
P95_LINE=$((TOTAL * 95 / 100))
P99_LINE=$((TOTAL * 99 / 100))

P50=$(sed -n "${P50_LINE}p" "$LATENCY_FILE")
P95=$(sed -n "${P95_LINE}p" "$LATENCY_FILE")
P99=$(sed -n "${P99_LINE}p" "$LATENCY_FILE")
MIN=$(head -1 "$LATENCY_FILE")
MAX=$(tail -1 "$LATENCY_FILE")
AVG=$(awk '{sum+=$1} END {print sum/NR}' "$LATENCY_FILE")

# Format with 2 decimal places
P50=$(printf "%.2f" "$P50")
P95=$(printf "%.2f" "$P95")
P99=$(printf "%.2f" "$P99")
MIN=$(printf "%.2f" "$MIN")
MAX=$(printf "%.2f" "$MAX")
AVG=$(printf "%.2f" "$AVG")

# Display results
echo "════════════════════════════════════════════════════════"
echo "  LATENCY RESULTS                                      "
echo "════════════════════════════════════════════════════════"
echo ""
echo "  Requests:     $TOTAL"
echo "  Min:          ${MIN}ms"
echo "  Average:      ${AVG}ms"
echo "  p50 (median): ${P50}ms"
echo "  p95:          ${P95}ms"
echo "  p99:          ${P99}ms"
echo "  Max:          ${MAX}ms"
echo ""

# Check if p99 meets target
P99_INT=${P99%.*}
if [ "$P99_INT" -lt 50 ]; then
    echo "✓ SUCCESS: p99 latency (${P99}ms) meets <50ms target!"
else
    echo "✗ WARNING: p99 latency (${P99}ms) exceeds 50ms target"
fi

echo ""
echo "════════════════════════════════════════════════════════"

# Cleanup
rm "$LATENCY_FILE"
