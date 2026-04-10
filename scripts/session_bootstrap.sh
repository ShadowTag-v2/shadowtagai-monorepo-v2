#!/usr/bin/env bash

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"

echo "💎 Initializing Session Bootstrap Check..."

if [[ "$PWD" != "$ROOT" ]]; then
    echo "❌ CRITICAL: Unauthorized execution outside Monorepo Root."
    exit 1
fi

if [[ -f "$ROOT/scripts/gcloud_auth_solver.py" ]]; then
    echo "   -> Running Keymaster (gcloud_auth_solver)..."
    python3 "$ROOT/scripts/gcloud_auth_solver.py"
fi

if ! pgrep -f "omega_auth_daemon" >/dev/null; then
    if [[ -f "$ROOT/scripts/omega_auth_daemon.py" ]]; then
        echo "   -> Starting Heartbeat (omega_auth_daemon)..."
        nohup python3 "$ROOT/scripts/omega_auth_daemon.py" >/dev/null 2>&1 &
    fi
else
    echo "   -> Heartbeat already running."
fi

echo "✅ Session Bootstrap Complete."
