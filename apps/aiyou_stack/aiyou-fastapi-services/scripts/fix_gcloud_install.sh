#!/bin/bash
set -e

echo "🛠️ Fixing Google Cloud SDK installation..."

# Install Google Cloud SDK non-interactively
# This fixes the "stuck at prompt" issue by disabling prompts
curl -sSL https://sdk.cloud.google.com | bash -s -- --disable-prompts

echo "✅ Google Cloud SDK installed."
echo "🔄 Please restart your terminal or run: source ~/.bashrc (or ~/.zshrc)"
