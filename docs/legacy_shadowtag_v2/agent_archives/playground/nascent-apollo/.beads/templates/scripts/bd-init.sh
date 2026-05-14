#!/usr/bin/env bash
# bd-init.sh - Initialize Beads issue tracker for any project
#
# Usage: ./scripts/bd-init.sh [--stealth] [--no-hooks] [--quiet]
#
# Options:
#   --stealth    Local-only mode (not committed to git)
#   --no-hooks   Skip installing git hooks
#   --quiet      Non-interactive mode (for agents)
#   --help       Show this help message
#
# Installation:
#   mkdir -p scripts && curl -o scripts/bd-init.sh https://raw.githubusercontent.com/<user>/beads-templates/main/scripts/bd-init.sh
#   chmod +x scripts/bd-init.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

show_help() {
    sed -n '2,13p' "$0" | sed 's/^# //' | sed 's/^#//'
    exit 0
}

main() {
    local stealth_mode=false
    local install_hooks=true
    local quiet_mode=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --stealth) stealth_mode=true; shift ;;
            --no-hooks) install_hooks=false; shift ;;
            --quiet) quiet_mode=true; shift ;;
            --help|-h) show_help ;;
            *) echo "Unknown option: $1"; show_help ;;
        esac
    done

    cd "$PROJECT_ROOT"

    # Check if beads is installed
    if ! command -v bd &> /dev/null; then
        echo "Error: Beads (bd) is not installed."
        echo ""
        echo "Install via one of:"
        echo "  brew tap steveyegge/beads && brew install bd  (recommended)"
        echo "  curl -fsSL https://raw.githubusercontent.com/steveyegge/beads/main/scripts/install.sh | bash"
        echo "  npm install -g @beads/bd"
        echo "  go install github.com/steveyegge/beads/cmd/bd@latest"
        exit 1
    fi

    # Check if already initialized
    if [[ -d ".beads" ]]; then
        echo "Beads already initialized in this project."
        echo "Run 'bd ready' to see available tasks."
        exit 0
    fi

    # Initialize beads
    local init_flags=""
    [[ "$stealth_mode" == true ]] && init_flags="$init_flags --stealth"
    [[ "$quiet_mode" == true ]] && init_flags="$init_flags --quiet"

    echo "Initializing Beads..."
    bd init $init_flags

    # Install git hooks (pre-commit, pre-push, post-merge)
    if [[ "$install_hooks" == true ]]; then
        echo ""
        echo "Installing git hooks..."
        if bd hooks install 2>/dev/null; then
            echo "  Installed: pre-commit, pre-push, post-merge"
        else
            echo "  (hooks not available in this version)"
        fi
    fi

    # Setup Claude Code integration if available
    if bd setup claude --help &>/dev/null 2>&1; then
        echo ""
        echo "Setting up Claude Code integration..."
        bd setup claude 2>/dev/null || true
    fi

    # Update .gitignore if needed
    if [[ -f ".gitignore" ]]; then
        if ! grep -q "^\.beads/" .gitignore 2>/dev/null; then
            echo ""
            echo "Updating .gitignore..."
            cat >> .gitignore << 'EOF'

# Beads issue tracker
.beads/*
!.beads/issues.jsonl
EOF
            echo "  Added .beads/ entries"
        fi
    else
        echo ""
        echo "Creating .gitignore..."
        cat > .gitignore << 'EOF'
# Beads issue tracker
.beads/*
!.beads/issues.jsonl
EOF
    fi

    echo ""
    echo "Beads initialized successfully!"
    echo ""
    echo "Agent workflow:"
    echo "  1. bd ready --json              # Find unblocked work"
    echo "  2. bd update <id> --status in_progress"
    echo "  3. [do the work]"
    echo "  4. bd close <id> --reason \"Done\""
    echo "  5. bd sync                      # Flush to git (session end)"
    echo ""
    echo "Create issues:"
    echo "  bd create \"Title\" -p 1 -t task  # Types: bug, feature, task, epic, chore"
    echo "  bd dep add <child> <parent>     # Child blocked by parent"
    echo ""
    echo "Priority levels: 0=Critical, 1=High, 2=Medium, 3=Low, 4=Backlog"
}

main "$@"
