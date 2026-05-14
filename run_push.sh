#!/bin/bash
PYTHON_BIN="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.venv/bin/python3"
RAW_TOKEN=$($PYTHON_BIN tools/scripts/generate_token.py)
CLEAN_TOKEN=$(echo "$RAW_TOKEN" | tr -d '[:space:]')
GIT_TRACE=1 GIT_CURL_VERBOSE=1 git push --force --no-verify "https://x-access-token:${CLEAN_TOKEN}@github.com/ShadowTag-v2/Monorepo-Uphillsnowball.git" HEAD:refs/heads/main > push_out2.txt 2>&1
echo "Exit code: $?" >> push_out2.txt
