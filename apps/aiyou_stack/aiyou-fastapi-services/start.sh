#!/bin/bash

# Performance Engineer API Startup Script

echo "🚀 Starting Performance Engineer API..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please review and update .env with your configuration"
fi

# Start Redis (optional - check if Docker is available)
if command -v docker &> /dev/null; then
    echo "🔍 Checking Redis..."
    if ! docker ps | grep -q redis; then
        echo "🚀 Starting Redis container..."
        docker run -d --name redis-performance -p 6379:6379 redis:latest
    else
        echo "✅ Redis is already running"
    fi
else
    echo "⚠️  Docker not found. Please start Redis manually if you want caching."
    echo "   Or set ENABLE_CACHE=false in .env"
fi

# Run the application
echo ""
echo "✨ Starting Performance Engineer API..."
echo "📊 API will be available at: http://localhost:8000"
echo "📖 Documentation: http://localhost:8000/docs"
echo "🎯 Performance Summary: http://localhost:8000/performance/summary"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
