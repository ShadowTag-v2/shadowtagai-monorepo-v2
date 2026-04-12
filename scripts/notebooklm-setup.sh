#!/bin/bash
# ╔══════════════════════════════════════════════════╗
# ║  NotebookLM Master Brain Setup — v2 (Fixed)     ║
# ║  Model: gemini-3.1-flash-lite-preview            ║
# ║  Project: shadowtag-omega-v4                     ║
# ╚══════════════════════════════════════════════════╝
#
# This script completes interactive Google OAuth for the NotebookLM CLI.
# It MUST be run in an interactive terminal with display access.
#
# Usage: ./scripts/notebooklm-setup.sh

set -euo pipefail

# Fix PATH for Homebrew Python 3.13 and gcloud
export PATH="/Users/pikeymickey/Library/Python/3.13/bin:/Users/pikeymickey/Library/Python/3.14/bin:/opt/homebrew/bin:/opt/homebrew/sbin:$HOME/google-cloud-sdk/bin:$PATH"

MASTER_BRAIN_ID_FILE="$HOME/.notebooklm/master-brain-id"
STORAGE_STATE="$HOME/.notebooklm/storage_state.json"

echo "╔══════════════════════════════════════════╗"
echo "║  NotebookLM Master Brain Setup           ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ─── Preflight ───
echo "▸ Preflight check..."
if ! command -v notebooklm &>/dev/null; then
    echo "❌ notebooklm CLI not found."
    echo "   Install: pip3 install 'notebooklm-py[browser]' --trusted-host pypi.org --trusted-host files.pythonhosted.org"
    exit 1
fi
echo "  ✅ notebooklm $(notebooklm --version 2>/dev/null || echo 'present')"

# ─── Step 1: Login ───
echo ""
echo "▸ Step 1/4: Google Authentication"
echo "  A Chromium window will open. Sign into Google, then wait for the"
echo "  NotebookLM homepage to load. Press ENTER in this terminal when ready."
echo ""

notebooklm login

if [ ! -f "$STORAGE_STATE" ]; then
    echo "❌ Authentication failed — no storage state saved."
    exit 1
fi

# ─── Step 2: Verify ───
echo ""
echo "▸ Step 2/4: Verifying authentication..."
if notebooklm list &>/dev/null; then
    echo "  ✅ Authentication successful!"
else
    echo "❌ Authentication verification failed."
    echo "   Try: notebooklm login"
    exit 1
fi

# ─── Step 3: Create or Find Master Brain ───
echo ""
echo "▸ Step 3/4: Master Brain notebook"

if [ -f "$MASTER_BRAIN_ID_FILE" ]; then
    BRAIN_ID=$(cat "$MASTER_BRAIN_ID_FILE")
    echo "  ✅ Master Brain ID already saved: $BRAIN_ID"
    notebooklm use "$BRAIN_ID" 2>/dev/null || {
        echo "  ⚠️  Saved ID invalid — creating new notebook..."
        rm -f "$MASTER_BRAIN_ID_FILE"
    }
fi

if [ ! -f "$MASTER_BRAIN_ID_FILE" ]; then
    echo "  Creating 'Master Brain — Session Memory'..."
    # The CLI creates notebooks interactively — use the web-created one
    echo "  ⚠️  Please create a notebook titled 'Master Brain - Session Memory' in the"
    echo "     NotebookLM web UI (https://notebooklm.google.com) and paste the ID below."
    echo ""
    read -p "  Notebook ID: " NEW_BRAIN_ID
    mkdir -p "$(dirname "$MASTER_BRAIN_ID_FILE")"
    echo "$NEW_BRAIN_ID" > "$MASTER_BRAIN_ID_FILE"
    echo "  ✅ Master Brain ID saved: $NEW_BRAIN_ID"
fi

# ─── Step 4: Set Active ───
echo ""
echo "▸ Step 4/4: Setting active notebook..."
BRAIN_ID=$(cat "$MASTER_BRAIN_ID_FILE")
notebooklm use "$BRAIN_ID" 2>/dev/null && echo "  ✅ Master Brain is now active." || echo "  ⚠️  Could not set active — verify ID."

# ─── Summary ───
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  Setup Complete!                         ║"
echo "╠══════════════════════════════════════════╣"
echo "║  Master Brain: $(cat "$MASTER_BRAIN_ID_FILE" 2>/dev/null || echo 'NOT SET')"
echo "║  Auth: $([ -f "$STORAGE_STATE" ] && echo '✅ Saved' || echo '❌ Missing')"
echo "║  Project: shadowtag-omega-v4             ║"
echo "║  Model: gemini-3.1-flash-lite-preview    ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "Test: notebooklm ask 'Hello, Master Brain!'"
