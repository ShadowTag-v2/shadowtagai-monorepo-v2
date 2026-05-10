#!/bin/bash
# V23 PHOSPHOR-AWAKENING: Canonical Zombie Management
# Process sovereignty enforcement for the UphillSnowball Sovereign OS.
# Usage:
#   ./scripts/port_killer.sh --kill <PORT>       # Kill process on specific port
#   ./scripts/port_killer.sh --exterminate 1     # Mass grace-kill all legacy processes

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_kill() {
    echo -e "${RED}⚡ [Port-Killer] $1${NC}"
}

log_ok() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

if [ "${1:-}" == "--kill" ]; then
    PORT="${2:-}"
    if [ -z "$PORT" ]; then
        echo "Usage: $0 --kill <PORT>"
        exit 1
    fi

    PID=$(lsof -t -i:"$PORT" 2>/dev/null || true)
    if [ -n "$PID" ]; then
        log_kill "Sending SIGTERM to PID $PID on port $PORT"
        kill -15 "$PID" 2>/dev/null || true
        sleep 0.5
        # Check if still alive, then SIGKILL
        if kill -0 "$PID" 2>/dev/null; then
            log_kill "Process $PID survived SIGTERM. Sending SIGKILL."
            kill -9 "$PID" 2>/dev/null || true
        fi
        log_ok "Port $PORT cleared."
    else
        log_warn "No process found on port $PORT."
    fi

elif [ "${1:-}" == "--exterminate" ]; then
    log_kill "Executing mass grace-kill on all legacy processes..."

    # Count before
    BEFORE=$(pgrep -c -f "node|bun|dart|python|python3|gcloud" 2>/dev/null || echo "0")
    log_kill "Found $BEFORE target processes."

    # SIGTERM first (graceful)
    killall -15 node bun dart python python3 gcloud 2>/dev/null || true
    sleep 0.5

    # SIGKILL survivors
    killall -9 node bun dart python python3 gcloud 2>/dev/null || true

    # Count after
    AFTER=$(pgrep -c -f "node|bun|dart|python|python3|gcloud" 2>/dev/null || echo "0")
    log_ok "Workspace purified. Zombies eradicated. ($BEFORE → $AFTER processes)"

elif [ "${1:-}" == "--status" ]; then
    echo "=== Active Processes ==="
    echo "Node.js: $(pgrep -c node 2>/dev/null || echo 0)"
    echo "Bun:     $(pgrep -c bun 2>/dev/null || echo 0)"
    echo "Python:  $(pgrep -c python 2>/dev/null || echo 0)"
    echo "Dart:    $(pgrep -c dart 2>/dev/null || echo 0)"
    echo "GCloud:  $(pgrep -c gcloud 2>/dev/null || echo 0)"
    echo ""
    echo "=== Listening Ports ==="
    lsof -iTCP -sTCP:LISTEN -P -n 2>/dev/null | grep -E "(node|bun|python|dart)" || echo "None"

else
    echo "V23 Port-Killer — Process Sovereignty Enforcement"
    echo ""
    echo "Usage:"
    echo "  $0 --kill <PORT>       Kill process on specific port"
    echo "  $0 --exterminate 1     Mass kill all Node/Bun/Python/Dart/GCloud"
    echo "  $0 --status            Show active process counts"
fi
