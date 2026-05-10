#!/bin/bash
# Quick load test script

echo "🧪 Running Quick Load Test..."
echo ""

# Check if server is running
if ! curl -s http://localhost:8000/health/ping > /dev/null; then
    echo "❌ Server is not running!"
    echo "Please start the server first:"
    echo "  ./scripts/start_server.sh"
    exit 1
fi

echo "✅ Server is running"
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run smoke test
echo "Running smoke test (10 users, 30 seconds)..."
python run_load_test.py --scenario smoke

echo ""
echo "✅ Quick test completed!"
echo "📊 Check load_test_reports/ for results"
