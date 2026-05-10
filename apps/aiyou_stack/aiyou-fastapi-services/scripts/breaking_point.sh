#!/bin/bash
# Run breaking point test

echo "🔍 Running Breaking Point Test..."
echo "This will incrementally increase load to find system limits"
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

# Run breaking point test
python run_load_test.py --breaking-point

echo ""
echo "✅ Breaking point test completed!"
echo "📊 Check load_test_reports/ for detailed analysis"
