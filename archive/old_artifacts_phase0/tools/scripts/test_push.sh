#!/bin/bash
set -x
PYTHON_BIN="python3"
GITHUB_TOKEN=$($PYTHON_BIN "/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/tools/scripts/generate_token.py")
echo "Token length: ${#GITHUB_TOKEN}"
git push --force "https://x-access-token:${GITHUB_TOKEN}@github.com/ShadowTag-v2/Monorepo-Uphillsnowball.git" HEAD
