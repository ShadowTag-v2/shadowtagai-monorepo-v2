#!/bin/bash
# Full load testing suite

echo "🚀 Running Full Load Test Suite..."
echo ""

# Check if server is running
if ! curl -s http://localhost:8000/health/ping > /dev/null; then
    echo "❌ Server is not running!"
    echo "Please start the server first:"
    echo "  ./scripts/start_server.sh"
    exit 1
fi

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Array of scenarios to run
scenarios=("smoke" "light" "medium" "heavy")

for scenario in "${scenarios[@]}"; do
    echo ""
    echo "═══════════════════════════════════════════════════════"
    echo "Running $scenario test..."
    echo "═══════════════════════════════════════════════════════"

    python run_load_test.py --scenario $scenario

    echo ""
    echo "Waiting 30 seconds before next test..."
    sleep 30
done

echo ""
echo "✅ Full test suite completed!"
echo "📊 Check load_test_reports/ for all results"
