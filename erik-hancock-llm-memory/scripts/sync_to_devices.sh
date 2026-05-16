#!/bin/bash
#
# Cross-Device Memory Sync Utility
# Syncs memory between Mac ↔ Vertex ↔ GKE
#
# Usage:
#   ./sync_to_devices.sh pull   # Pull latest from GitHub
#   ./sync_to_devices.sh push   # Push local changes to GitHub
#

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Repository root
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Function to retry git commands with exponential backoff
retry_git() {
    local cmd="$1"
    local max_retries=4
    local retry=0
    local wait_time=2

    while [ $retry -lt $max_retries ]; do
        if eval "$cmd"; then
            return 0
        fi

        retry=$((retry + 1))
        if [ $retry -lt $max_retries ]; then
            echo -e "${YELLOW}⚠️  Network error, retrying in ${wait_time}s...${NC}"
            sleep $wait_time
            wait_time=$((wait_time * 2))
        fi
    done

    echo -e "${RED}✗ Command failed after $max_retries retries${NC}"
    return 1
}

# Function to detect conflicts
check_conflicts() {
    if git diff --name-only --diff-filter=U | grep -q .; then
        echo -e "${RED}✗ Merge conflicts detected!${NC}"
        echo -e "${YELLOW}Conflicts in:${NC}"
        git diff --name-only --diff-filter=U
        echo ""
        echo -e "${YELLOW}Options:${NC}"
        echo "  1. Resolve manually: git mergetool"
        echo "  2. Use LLM resolution: python scripts/merge_conflicts.py"
        echo "  3. Keep local: git checkout --ours <file> && git add <file>"
        echo "  4. Keep remote: git checkout --theirs <file> && git add <file>"
        return 1
    fi
    return 0
}

# Function to pull from GitHub
pull_memory() {
    echo -e "${GREEN}Pulling memory from GitHub...${NC}"

    # Fetch latest
    echo "Fetching latest changes..."
    if ! retry_git "git fetch origin main"; then
        echo -e "${RED}✗ Failed to fetch from GitHub${NC}"
        exit 1
    fi

    # Check if behind
    LOCAL=$(git rev-parse @)
    REMOTE=$(git rev-parse @{u})
    BASE=$(git merge-base @ @{u})

    if [ "$LOCAL" = "$REMOTE" ]; then
        echo -e "${GREEN}✓ Already up to date${NC}"
        return 0
    elif [ "$LOCAL" = "$BASE" ]; then
        # Fast-forward merge
        echo "Fast-forwarding to latest..."
        git merge --ff-only origin/main
    else
        # Need to merge
        echo "Merging changes..."
        git merge origin/main || {
            check_conflicts || exit 1
        }
    fi

    # Update symlink
    echo "Updating current.json symlink..."
    cd memory
    latest_snapshot=$(ls -t snapshots/memory_v*.json | head -1)
    if [ -n "$latest_snapshot" ]; then
        ln -sf "$latest_snapshot" current.json
        echo -e "${GREEN}✓ Symlink updated to $latest_snapshot${NC}"
    fi
    cd ..

    # Sync to Claude Code (if on MacBook)
    if [ -d "$HOME/.claude-code" ]; then
        echo "Syncing to Claude Code..."
        python scripts/claude_code_memory_local.py
    fi

    # Sync to Vertex Workbench (if on Vertex)
    if [ -d "$HOME/.workbench" ]; then
        echo "Syncing to Vertex Workbench..."
        python configs/vertex_workbench_config.py
    fi

    echo -e "${GREEN}✓ Pull complete!${NC}"
}

# Function to push to GitHub
push_memory() {
    echo -e "${GREEN}Pushing memory to GitHub...${NC}"

    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        echo -e "${YELLOW}Uncommitted changes detected${NC}"
        echo "Running extract_and_commit.py..."
        python scripts/extract_and_commit.py || {
            echo -e "${RED}✗ Extraction failed${NC}"
            exit 1
        }
    fi

    # Get current branch
    BRANCH=$(git rev-parse --abbrev-ref HEAD)

    # Push with retry
    echo "Pushing to origin/$BRANCH..."
    if ! retry_git "git push -u origin $BRANCH"; then
        echo -e "${RED}✗ Failed to push to GitHub${NC}"
        exit 1
    fi

    # Push tags
    echo "Pushing tags..."
    retry_git "git push --tags" || echo -e "${YELLOW}⚠️  Could not push tags${NC}"

    echo -e "${GREEN}✓ Push complete!${NC}"
}

# Function to show status
show_status() {
    echo -e "${GREEN}Memory Repository Status${NC}"
    echo "========================"
    echo ""

    # Version
    if [ -f "memory/current.json" ]; then
        VERSION=$(jq -r '.version // "unknown"' memory/current.json)
        UPDATED=$(jq -r '.last_updated // "unknown"' memory/current.json)
        CONVS=$(jq -r '.statistics.total_conversations // 0' memory/current.json)
        echo "Version: $VERSION"
        echo "Last Updated: $UPDATED"
        echo "Conversations: $CONVS"
        echo ""
    fi

    # Git status
    echo "Git Status:"
    git status -sb

    echo ""
    echo "Recent commits:"
    git log --oneline -5

    echo ""
    echo "Snapshots:"
    ls -lh memory/snapshots/ | tail -5
}

# Main command router
case "$1" in
    pull)
        pull_memory
        ;;
    push)
        push_memory
        ;;
    status)
        show_status
        ;;
    *)
        echo "Usage: $0 {pull|push|status}"
        echo ""
        echo "Commands:"
        echo "  pull    - Pull latest memory from GitHub"
        echo "  push    - Push local changes to GitHub"
        echo "  status  - Show repository status"
        echo ""
        echo "Examples:"
        echo "  Morning:  $0 pull    # Get latest updates"
        echo "  Evening:  $0 push    # Share your changes"
        exit 1
        ;;
esac
