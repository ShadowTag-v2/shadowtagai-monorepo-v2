#!/usr/bin/env bash
# generate_app_token.sh — Headless GitHub App token for CLI use
# Sources: auth_github_app.py (Python) or github-app-mcp-wrapper.mjs (Node.js)
#
# Usage:
#   source <(bash scripts/generate_app_token.sh)   # exports GH_TOKEN + GITHUB_TOKEN
#   eval "$(bash scripts/generate_app_token.sh)"    # alternative
#
# After sourcing, `gh` CLI and git HTTPS operations use the App token.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Try Node.js wrapper first (zero external deps)
if command -v node &>/dev/null && [[ -f "$SCRIPT_DIR/github-app-mcp-wrapper.mjs" ]]; then
  TOKEN=$(node "$SCRIPT_DIR/github-app-mcp-wrapper.mjs" --token 2>/dev/null)
  if [[ -n "$TOKEN" && ${#TOKEN} -gt 20 ]]; then
    echo "export GITHUB_TOKEN=$TOKEN"
    echo "export GH_TOKEN=$TOKEN"
    exit 0
  fi
fi

# Fallback: Python wrapper
if command -v python3 &>/dev/null && [[ -f "$SCRIPT_DIR/auth_github_app.py" ]]; then
  EXPORTS=$(python3 "$SCRIPT_DIR/auth_github_app.py" --export 2>/dev/null)
  if [[ -n "$EXPORTS" ]]; then
    echo "$EXPORTS"
    exit 0
  fi
fi

echo "ERROR: Could not generate GitHub App token. Check PEM availability." >&2
exit 1
