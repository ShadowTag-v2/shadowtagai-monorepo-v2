#!/bin/bash

# Define the function body
FUNC_BODY="
# ANTIGRAVITY MISSION ALIAS
run_mission() {
    pushd /Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2 > /dev/null
    python3 pnkln_mission_start.py \"\$@\"
    popd > /dev/null
}
"

# Detect shell config file
SHELL_CONFIG=""
if [ -f "$HOME/.zshrc" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
else
    echo "❌ Could not detect .zshrc or .bashrc"
    exit 1
fi

# Check if alias already exists to avoid duplication
if grep -q "ANTIGRAVITY MISSION ALIAS" "$SHELL_CONFIG"; then
    echo "✅ Alias already installed in $SHELL_CONFIG"
else
    echo "$FUNC_BODY" >> "$SHELL_CONFIG"
    echo "✅ Installed 'run_mission' alias to $SHELL_CONFIG"
    echo "👉 Run 'source $SHELL_CONFIG' to activate it."
fi
