#!/usr/bin/env bash
# port_killer.sh — Zombie Process Killer (inspired by productdevbook/port-killer)
# Architecture: Uses lsof + SIGTERM→SIGKILL graceful shutdown pattern from
# external_repos/port-killer/platforms/macos/Sources/PortScanner.swift
#
# Usage:
#   ./scripts/port_killer.sh              # Scan and display all listening ports
#   ./scripts/port_killer.sh --kill PORT  # Kill process on PORT (graceful then force)
#   ./scripts/port_killer.sh --deep PORT  # Deep kill: listener + established connections
#   ./scripts/port_killer.sh --zombies    # Find and kill zombie/long-running processes
#   ./scripts/port_killer.sh --age HOURS  # Kill processes older than HOURS hours

set -euo pipefail

GRACE_PERIOD_MS=500  # Match port-killer's 500ms SIGTERM grace period

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

scan_ports() {
    echo -e "${BOLD}${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${CYAN}║  PortKiller Scanner (Swift→Bash port)                        ║${NC}"
    echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    printf "${BOLD}%-8s %-8s %-20s %-25s %-10s${NC}\n" "PORT" "PID" "PROCESS" "ADDRESS" "USER"
    echo "────────────────────────────────────────────────────────────────────────────"

    # Replicate port-killer's lsof flags exactly
    lsof -iTCP -sTCP:LISTEN -P -n +c 0 2>/dev/null | tail -n +2 | while IFS= read -r line; do
        local process pid user name port_num address
        process=$(echo "$line" | awk '{print $1}')
        pid=$(echo "$line" | awk '{print $2}')
        user=$(echo "$line" | awk '{print $3}')
        # Extract the NAME column (contains address:port)
        name=$(echo "$line" | grep -oE '[0-9.*[\]:]+:[0-9]+' | tail -1)
        if [ -n "$name" ]; then
            port_num=$(echo "$name" | rev | cut -d: -f1 | rev)
            address=$(echo "$name" | rev | cut -d: -f2- | rev)
        else
            port_num="?"
            address="?"
        fi
        printf "%-8s %-8s %-20s %-25s %-10s\n" "$port_num" "$pid" "$process" "$address" "$user"
    done
    echo ""
}

kill_port() {
    local target_port=$1
    local pids
    pids=$(lsof -iTCP:"$target_port" -sTCP:LISTEN -P -n -t 2>/dev/null || true)

    if [ -z "$pids" ]; then
        echo -e "${YELLOW}No process found listening on port $target_port${NC}"
        return 1
    fi

    for pid in $pids; do
        local proc_name
        proc_name=$(ps -p "$pid" -o comm= 2>/dev/null || echo "unknown")
        echo -e "${CYAN}Killing ${BOLD}$proc_name${NC}${CYAN} (PID: $pid) on port $target_port...${NC}"

        # Stage 1: SIGTERM (graceful)
        kill -15 "$pid" 2>/dev/null || true
        echo -e "  ${GREEN}→ SIGTERM sent, waiting ${GRACE_PERIOD_MS}ms grace period...${NC}"
        sleep 0.5

        # Stage 2: Check if still alive, force kill
        if kill -0 "$pid" 2>/dev/null; then
            kill -9 "$pid" 2>/dev/null || true
            echo -e "  ${RED}→ SIGKILL sent (process did not exit gracefully)${NC}"
        else
            echo -e "  ${GREEN}→ Process exited gracefully ✓${NC}"
        fi
    done
}

deep_kill() {
    local target_port=$1
    echo -e "${BOLD}${RED}Deep Kill: port $target_port (listener + established connections)${NC}"

    # Kill listener first
    kill_port "$target_port"

    # Then kill established connections (port-killer's findEstablishedPids pattern)
    local established_pids
    established_pids=$(lsof -iTCP:"$target_port" -sTCP:ESTABLISHED -P -n -t 2>/dev/null || true)

    if [ -n "$established_pids" ]; then
        echo -e "${YELLOW}Killing established connections...${NC}"
        for pid in $established_pids; do
            local proc_name
            proc_name=$(ps -p "$pid" -o comm= 2>/dev/null || echo "unknown")
            echo -e "  ${CYAN}Killing established: $proc_name (PID: $pid)${NC}"
            kill -15 "$pid" 2>/dev/null || true
            sleep 0.5
            kill -9 "$pid" 2>/dev/null || true
        done
    fi
    echo -e "${GREEN}Deep kill complete ✓${NC}"
}

find_zombies() {
    local age_hours=${1:-4}
    echo -e "${BOLD}${YELLOW}Hunting zombies older than ${age_hours}h...${NC}"
    echo ""

    local found=0
    # Find processes older than specified hours
    # Using ps with elapsed time in seconds
    ps -eo pid,etime,command 2>/dev/null | tail -n +2 | while IFS= read -r line; do
        local pid etime cmd
        pid=$(echo "$line" | awk '{print $1}')
        etime=$(echo "$line" | awk '{print $2}')
        cmd=$(echo "$line" | awk '{$1=$2=""; print $0}' | sed 's/^ *//')

        # Parse elapsed time to hours
        local hours=0
        if echo "$etime" | grep -qE '^[0-9]+-'; then
            # Days format: DD-HH:MM:SS
            local days hrs
            days=$(echo "$etime" | cut -d- -f1)
            hrs=$(echo "$etime" | cut -d- -f2 | cut -d: -f1)
            hours=$((days * 24 + hrs))
        elif echo "$etime" | grep -cqE '^[0-9]+:[0-9]+:[0-9]+$' > /dev/null 2>&1; then
            # HH:MM:SS format
            hours=$(echo "$etime" | cut -d: -f1)
        fi

        if [ "$hours" -ge "$age_hours" ] 2>/dev/null; then
            # Filter to known zombie patterns
            if echo "$cmd" | grep -qiE '(curl.*sdk\.cloud|gcloud.*install|npm.*install.*stuck|node.*--inspect|bun.*dev.*server)'; then
                echo -e "  ${RED}ZOMBIE${NC} PID=$pid age=${etime} cmd=$(echo "$cmd" | head -c 80)"
                found=$((found + 1))
            fi
        fi
    done

    if [ "$found" -eq 0 ]; then
        echo -e "  ${GREEN}No zombies found ✓${NC}"
    fi
}

kill_zombies() {
    local age_hours=${1:-4}
    echo -e "${BOLD}${RED}Exterminating zombies older than ${age_hours}h...${NC}"

    ps -eo pid,etime,command 2>/dev/null | tail -n +2 | while IFS= read -r line; do
        local pid etime cmd
        pid=$(echo "$line" | awk '{print $1}')
        etime=$(echo "$line" | awk '{print $2}')
        cmd=$(echo "$line" | awk '{$1=$2=""; print $0}' | sed 's/^ *//')

        local hours=0
        if echo "$etime" | grep -qE '^[0-9]+-'; then
            local days hrs
            days=$(echo "$etime" | cut -d- -f1)
            hrs=$(echo "$etime" | cut -d- -f2 | cut -d: -f1)
            hours=$((days * 24 + hrs))
        elif echo "$etime" | grep -cqE '^[0-9]+:[0-9]+:[0-9]+$' > /dev/null 2>&1; then
            hours=$(echo "$etime" | cut -d: -f1)
        fi

        if [ "$hours" -ge "$age_hours" ] 2>/dev/null; then
            if echo "$cmd" | grep -qiE '(curl.*sdk\.cloud|gcloud.*install|npm.*install.*stuck|node.*--inspect)'; then
                echo -e "  ${RED}KILLING${NC} PID=$pid (${etime} old): $(echo "$cmd" | head -c 60)"
                kill -15 "$pid" 2>/dev/null || true
                sleep 0.5
                kill -9 "$pid" 2>/dev/null || true
            fi
        fi
    done

    echo -e "${GREEN}Zombie extermination complete ✓${NC}"
}

# Main dispatcher
case "${1:-scan}" in
    scan|--scan|-s)
        scan_ports
        ;;
    --kill|-k)
        [ -z "${2:-}" ] && { echo "Usage: $0 --kill PORT"; exit 1; }
        kill_port "$2"
        ;;
    --deep|-d)
        [ -z "${2:-}" ] && { echo "Usage: $0 --deep PORT"; exit 1; }
        deep_kill "$2"
        ;;
    --zombies|-z)
        find_zombies "${2:-4}"
        ;;
    --exterminate|-x)
        kill_zombies "${2:-4}"
        ;;
    --help|-h)
        echo "PortKiller — Zombie Process Killer (Swift→Bash port)"
        echo ""
        echo "Usage:"
        echo "  $0                    Scan all listening TCP ports"
        echo "  $0 --kill PORT        Kill process on PORT (graceful → force)"
        echo "  $0 --deep PORT        Deep kill: listener + established connections"
        echo "  $0 --zombies [HOURS]  Find zombie processes older than HOURS (default: 4)"
        echo "  $0 --exterminate [H]  Kill zombies older than H hours"
        echo ""
        echo "Source: external_repos/port-killer (productdevbook/port-killer)"
        ;;
    *)
        echo "Unknown command: $1. Use --help for usage."
        exit 1
        ;;
esac
