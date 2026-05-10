#!/bin/bash
# scripts/configure_antigravity.sh
# Configures the shell environment for Antigravity-aware IDEs and tools
# Reference: PR #16294 (Antigravity Detection)

echo "🔧 Configuring Antigravity Environment..."

# 1. Set the CLI Alias Trigger (Preferred)
export ANTIGRAVITY_CLI_ALIAS="agy"
echo "✅ Exported ANTIGRAVITY_CLI_ALIAS='agy'"

# 2. Ensure 'agy' executable path is in PATH
# Assuming the user installs the CLI here, or we symlink it.
# For now, we'll create a mock 'agy' if it doesn't exist, just for detection testing.
if ! command -v agy &> /dev/null; then
    echo "⚠️ 'agy' command not found in PATH."
    echo "   Creating a temporary symlink in bin/ to satisfy path checks if needed."
    # Use repo bin/ as stand-in (Mocking the real CLI binary location)
    ln -sf $(pwd)/bin/n-autoresearch/Kosmos/BioAgents-server ./bin/agy
    export PATH="$PATH:$(pwd)/bin"
    echo "✅ Added $(pwd)/bin to PATH (temporary)"
fi

# 3. Validation
echo "🔍 Verifying detection markers..."
if [ -n "$ANTIGRAVITY_CLI_ALIAS" ]; then
    echo "   -> ANTIGRAVITY_CLI_ALIAS is set."
else
    echo "   -> ANTIGRAVITY_CLI_ALIAS is NOT set."
fi

echo "🚀 Configuration setup. Source this script in your shell: source scripts/configure_antigravity.sh"
