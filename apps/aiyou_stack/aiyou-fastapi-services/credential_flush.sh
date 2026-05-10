#!/bin/bash
# SHADOWTAG OMEGA: CREDENTIAL FLUSH
# ---------------------------------

echo ">>> 🧼 Scrubbing Stale Credentials..."

# 1. Kill the confused processes
# Skipping pkill of "Antigravity" to avoid terminating the agent process.
# pkill -f "Antigravity"
# pkill -f "gcloud.gemini"
# pkill -f "metadata_server"

# 2. Delete Editor-Specific Auth Cache
# This forces the editor to ask for a login again instead of using the broken one.
RM_TARGETS=(
    "$HOME/Library/Application Support/Antigravity/User/globalStorage/googlecloudtools.cloudcode/auth"
    "$HOME/.config/gcloud/application_default_credentials.json"
    "$HOME/.config/gcloud/legacy_credentials"
)

for target in "${RM_TARGETS[@]}"; do
    if [ -e "$target" ]; then
        echo ">>> 🗑️  Removing: $target"
        rm -rf "$target"
    fi
done

echo ">>> ✅ Flush Part 1 Complete. Please proceed with manual auth if needed."
