#!/bin/bash
set -e

echo "🟢 INITIALIZING ANTIGRAVITY ENVIRONMENT..."

# 1. Virtual Environment Check
if [ ! -d "venv" ]; then
    echo "🛠️  Forging venv..."
    python3 -m venv venv
fi

# 2. Activate
source venv/bin/activate

# 3. Dependencies
if [ -f "requirements.txt" ]; then
    echo "📦 Loading Arsenal (pip install)..."
    pip install -q -r requirements.txt
fi

# 4. Execute Mission
echo "🚀 LAUNCHING PNKLN PROTOCOL..."
python pnkln_mission_start.py
