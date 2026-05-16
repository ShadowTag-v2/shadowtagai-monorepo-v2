#!/bin/bash
set -x
cd /home/user/smart_actions_drop || exit 1
export PATH=$HOME/.local/bin:$PATH
export PYTHONPATH=$(pwd)
chmod +x bin/flyingmonkeys-server

echo "🚀 Starting Server..."
nohup ./bin/flyingmonkeys-server > server.log 2>&1 &
PID=$!
echo "Server PID: $PID"

echo "⏳ Waiting 10s for startup..."
sleep 10

echo "🔍 Running Verification..."
python3 scripts/verify_smart_actions.py
RET=$?

echo "🛑 Stopping Server..."
kill $PID

echo "--- SERVER LOG ---"
cat server.log
echo "------------------"

exit $RET
