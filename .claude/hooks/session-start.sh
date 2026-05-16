#!/bin/bash
# SessionStart hook - Loads development context at session start

set -e

# Read hook input from stdin
INPUT=$(cat)

# Extract session source
SOURCE=$(echo "$INPUT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('source', 'unknown'))")

echo "=== Session Starting ==="
echo "Source: $SOURCE"
echo ""

# Show current git status
echo "Git Status:"
git status --short 2>/dev/null || echo "Not a git repository"
echo ""

# Show current branch
BRANCH=$(git branch --show-current 2>/dev/null || echo "N/A")
echo "Current Branch: $BRANCH"
echo ""

# Show recent commits
echo "Recent Commits (last 3):"
git log --oneline -3 2>/dev/null || echo "No git history"
echo ""

# Check for package.json and show available scripts
if [ -f "$CLAUDE_PROJECT_DIR/package.json" ]; then
    echo "Available npm scripts:"
    python3 -c "
import json
try:
    with open('$CLAUDE_PROJECT_DIR/package.json') as f:
        pkg = json.load(f)
        scripts = pkg.get('scripts', {})
        if scripts:
            for name in scripts.keys():
                print(f'  - npm run {name}')
        else:
            print('  (no scripts defined)')
except:
    pass
    "
    echo ""
fi

# Check for Python virtual environment
if [ -d "$CLAUDE_PROJECT_DIR/venv" ] || [ -d "$CLAUDE_PROJECT_DIR/.venv" ]; then
    echo "Python virtual environment detected"
    echo "  Tip: Activate with 'source venv/bin/activate' or 'source .venv/bin/activate'"
    echo ""
fi

# Check for requirements.txt
if [ -f "$CLAUDE_PROJECT_DIR/requirements.txt" ]; then
    echo "Python requirements.txt found"
    echo "  Tip: Install with 'pip install -r requirements.txt'"
    echo ""
fi

# Load environment variables if .env exists
if [ -f "$CLAUDE_PROJECT_DIR/.env" ]; then
    echo "Found .env file (not loaded for security)"
    echo "  Tip: Source it manually if needed: 'source .env'"
    echo ""
fi

# Persist useful environment variables for this session
if [ -n "$CLAUDE_ENV_FILE" ]; then
    # Set NODE_ENV if not already set
    if [ -z "$NODE_ENV" ]; then
        echo 'export NODE_ENV=development' >> "$CLAUDE_ENV_FILE"
    fi

    # Add node_modules/.bin to PATH if package.json exists
    if [ -f "$CLAUDE_PROJECT_DIR/package.json" ]; then
        echo 'export PATH="$PATH:'"$CLAUDE_PROJECT_DIR"'/node_modules/.bin"' >> "$CLAUDE_ENV_FILE"
    fi
fi

echo "=== Session Context Loaded ==="

exit 0
