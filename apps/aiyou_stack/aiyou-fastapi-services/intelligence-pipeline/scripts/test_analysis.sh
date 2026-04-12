#!/bin/bash
# PNKLN Intelligence Pipeline - Gemini Analysis Test Script
# Validates analysis framework with dummy data

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🧪 Testing Gemini Analysis Framework                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ ERROR: GOOGLE_API_KEY not set"
    echo ""
    echo "To test Gemini analysis, set your Google API key:"
    echo "  export GOOGLE_API_KEY='your-api-key-here'"
    echo ""
    echo "Get a key at: https://makersuite.google.com/app/apikey"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: python3 not found"
    exit 1
fi

echo "✓ GOOGLE_API_KEY set"
echo "✓ python3 found"

# Check Python dependencies
echo ""
echo "📦 Checking Python dependencies..."

if ! python3 -c "import google.generativeai" 2>/dev/null; then
    echo "⚠️  google-generativeai not installed, installing..."
    pip3 install --quiet google-generativeai
    echo "✓ Installed google-generativeai"
else
    echo "✓ google-generativeai available"
fi

# Run analysis
echo ""
echo "🚀 Running Gemini analysis..."
echo ""

python3 "$SCRIPT_DIR/run_gemini_analysis.py" \
    --base-path "$BASE_DIR" \
    --output "$BASE_DIR/reports/test_analysis_$(date +%Y%m%d_%H%M%S).md"

# Check output
if [ $? -eq 0 ]; then
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║  ✅ Analysis Test Complete                                  ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "📊 Report generated in: $BASE_DIR/reports/"
    echo ""
    echo "To review the report:"
    echo "  cat $BASE_DIR/reports/test_analysis_*.md | less"
else
    echo ""
    echo "❌ Analysis test failed"
    exit 1
fi
