#!/bin/bash
set -e
cd /Users/pikeymickey/ShadowTag-v2-fastapi-services

echo "🔍 Checking for R installation..."

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Homebrew is installed
if ! command_exists brew; then
    echo "🍺 Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # Add Homebrew to PATH for the current session
    if [[ "$(uname -m)" == "arm64" ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    else
        eval "$(/usr/local/bin/brew shellenv)"
    fi
else
    echo "✅ Homebrew is already installed."
fi

# Check if R is installed
if ! command_exists R; then
    echo "📉 R not found. Installing R via Homebrew..."
    brew install r
else
    echo "✅ R is already installed at $(which R)."
fi

# Verify R installation
R_PATH=$(which R)
if [ -z "$R_PATH" ]; then
    echo "❌ Failed to install R. Please install it manually."
    exit 1
fi

echo "✅ R installed at: $R_PATH"

# Update VS Code settings if needed
SETTINGS_FILE=".vscode/settings.json"
if [ -f "$SETTINGS_FILE" ]; then
    echo "⚙️  Updating $SETTINGS_FILE..."
    # Use python to update the JSON safely
    python3 -c "import json; import os;
with open('$SETTINGS_FILE', 'r') as f: data = json.load(f);
data['r.rpath.mac'] = '$R_PATH';
with open('$SETTINGS_FILE', 'w') as f: json.dump(data, f, indent=2)"
    echo "✅ Updated r.rpath.mac to $R_PATH"
else
    echo "⚠️  $SETTINGS_FILE not found. Skipping settings update."
fi

echo "🎉 R setup complete!"
read -p "Press [Enter] to close this window..."
