#!/bin/bash
# ╔═══════════════════════════════════════════════╗
# ║  Antigravity Daemon — Monorepo Monitor         ║
# ║  Replaces legacy aiyou-fastapi binary           ║
# ║  Model: gemini-3.1-flash-lite-preview           ║
# ║  Project: shadowtag-omega-v4                    ║
# ╚═══════════════════════════════════════════════╝

set -euo pipefail

export PATH="/opt/homebrew/bin:/usr/bin:/usr/sbin:/bin:$PATH"
export HOME="/Users/pikeymickey"

REPO="$HOME/.gemini/antigravity/Monorepo-Uphillsnowball"
LOG="$REPO/logs/daemon.out.log"
MODE="${1:-monitor}"

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Antigravity daemon starting (mode: $MODE)" >> "$LOG"

case "$MODE" in
    monitor)
        # Health check loop
        while true; do
            # Check: gitsync still loaded
            if ! launchctl list | grep -q "com.antigravity.gitsync"; then
                echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] WARN: gitsync not loaded" >> "$LOG"
            fi
            
            # Check: temporal still running
            if ! launchctl list | grep -q "com.pnkln.temporal-server"; then
                echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] WARN: temporal not loaded" >> "$LOG"
            fi
            
            # Check disk space
            DISK_FREE=$(df -g "$REPO" | tail -1 | awk '{print $4}')
            if [ "${DISK_FREE:-0}" -lt 5 ]; then
                echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] CRITICAL: <5GB free disk" >> "$LOG"
            fi
            
            # Heartbeat
            echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] OK: heartbeat" >> "$LOG"
            
            sleep 300  # 5-minute intervals
        done
        ;;
    *)
        echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Unknown mode: $MODE" >> "$LOG"
        exit 1
        ;;
esac
