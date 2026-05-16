#!/bin/bash
# Antigravity Local Toolchain Launcher
# Manages all local Antigravity development tools

set -e

BASE_DIR="/Users/pikeymickey"
PROXY_DIR="$BASE_DIR/antigravity-proxy"
API_DIR="$BASE_DIR/antigravity2api-nodejs"
MANAGER_DIR="$BASE_DIR/Antigravity-Manager"
WORKSPACE_DIR="$BASE_DIR/antigravity-workspace-template"
RULES_DIR="$BASE_DIR/windsurf-antigravity-rules"
GCLI_DIR="$BASE_DIR/gcli-nexus"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║       🚀 ANTIGRAVITY LOCAL TOOLCHAIN                       ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_menu() {
    echo -e "${GREEN}Available Commands:${NC}"
    echo ""
    echo "  1) proxy       - Start mitmproxy (use your own API key)"
    echo "  2) antigravity - Launch Antigravity through proxy"
    echo "  3) api         - Start OpenAI-compatible API server (port 8045)"
    echo "  4) manager     - Launch Antigravity Account Manager (GUI)"
    echo "  5) workspace   - Run workspace template agent"
    echo "  6) rules       - Copy AI rules to current project"
    echo ""
    echo "  all            - Start proxy + API server + launch Antigravity"
    echo "  status         - Show running services"
    echo "  stop           - Stop all services"
    echo ""
}

start_proxy() {
    echo -e "${YELLOW}Starting mitmproxy (headless)...${NC}"
    cd "$PROXY_DIR"
    if pgrep -f "mitmdump.*mitmproxy-addon" > /dev/null; then
        echo -e "${GREEN}Proxy already running${NC}"
    else
        mitmdump -s mitmproxy-addon.py --listen-port 8080 &
        echo -e "${GREEN}Proxy started on port 8080${NC}"
    fi
}

launch_antigravity() {
    echo -e "${YELLOW}Launching Antigravity through proxy...${NC}"
    HTTP_PROXY=http://localhost:8080 \
    HTTPS_PROXY=http://localhost:8080 \
    NODE_TLS_REJECT_UNAUTHORIZED=0 \
    ELECTRON_DISABLE_SECURITY_WARNINGS=true \
    /Applications/Antigravity.app/Contents/MacOS/Electron --ignore-certificate-errors &
    echo -e "${GREEN}Antigravity launched with proxy${NC}"
}

start_api() {
    echo -e "${YELLOW}Starting OpenAI-compatible API server...${NC}"
    cd "$API_DIR"
    if pgrep -f "node.*antigravity2api" > /dev/null; then
        echo -e "${GREEN}API server already running on port 8045${NC}"
    else
        npm start &
        echo -e "${GREEN}API server starting on http://localhost:8045${NC}"
    fi
}

launch_manager() {
    echo -e "${YELLOW}Launching Account Manager...${NC}"
    cd "$MANAGER_DIR"
    python gui/main.py &
    echo -e "${GREEN}Account Manager launched${NC}"
}

run_workspace() {
    echo -e "${YELLOW}Running workspace agent...${NC}"
    cd "$WORKSPACE_DIR"
    export GOOGLE_API_KEY="AIzaSyAxgD_goF3I9hC_DaWGoIt7Cu7yB6PTGQg"
    python src/agent.py
}

copy_rules() {
    if [ -z "$1" ]; then
        TARGET_DIR="$(pwd)"
    else
        TARGET_DIR="$1"
    fi
    echo -e "${YELLOW}Copying AI rules to $TARGET_DIR...${NC}"
    cp -r "$RULES_DIR/en/.agent" "$TARGET_DIR/" 2>/dev/null || true
    echo -e "${GREEN}Rules copied to $TARGET_DIR/.agent/${NC}"
}

show_status() {
    echo -e "${YELLOW}Service Status:${NC}"
    echo ""
    if pgrep -f "mitmdump.*mitmproxy-addon" > /dev/null; then
        echo -e "  mitmproxy:     ${GREEN}RUNNING${NC} (port 8080)"
    else
        echo -e "  mitmproxy:     ${RED}STOPPED${NC}"
    fi

    if pgrep -f "node.*server" > /dev/null; then
        echo -e "  API Server:    ${GREEN}RUNNING${NC} (port 8045)"
    else
        echo -e "  API Server:    ${RED}STOPPED${NC}"
    fi

    if pgrep -f "Antigravity" > /dev/null; then
        echo -e "  Antigravity:   ${GREEN}RUNNING${NC}"
    else
        echo -e "  Antigravity:   ${RED}STOPPED${NC}"
    fi
    echo ""
}

stop_all() {
    echo -e "${YELLOW}Stopping all services...${NC}"
    pkill -f "mitmdump.*mitmproxy-addon" 2>/dev/null || true
    pkill -f "node.*server" 2>/dev/null || true
    echo -e "${GREEN}All services stopped${NC}"
}

start_all() {
    start_proxy
    sleep 2
    start_api
    sleep 2
    launch_antigravity
}

# Main
print_header

case "${1:-menu}" in
    proxy|1)
        start_proxy
        ;;
    antigravity|2)
        launch_antigravity
        ;;
    api|3)
        start_api
        ;;
    manager|4)
        launch_manager
        ;;
    workspace|5)
        run_workspace
        ;;
    rules|6)
        copy_rules "$2"
        ;;
    all)
        start_all
        ;;
    status)
        show_status
        ;;
    stop)
        stop_all
        ;;
    menu|*)
        print_menu
        ;;
esac
