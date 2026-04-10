#!/bin/bash
# Automatically initializes the Python environment and IDE settings for Antigravity

# 1. Define our target directories
MONOREPO_ROOT=$(pwd)
APP_DIR="apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services"
VENV_REL_PATH="${APP_DIR}/.venv/bin/python"
VSCODE_DIR=".vscode"
SETTINGS_FILE="${VSCODE_DIR}/settings.json"

echo "🚀 Initializing Antigravity workspace..."

# 2. Generate the .venv and install dependencies
echo "📦 Running 'uv sync' in ${APP_DIR}..."
cd "${APP_DIR}" || { echo "❌ Error: App directory not found!"; exit 1; }
uv sync
cd "${MONOREPO_ROOT}"

# 3. Configure the IDE safely
echo "⚙️ Configuring VS Code / Antigravity interpreter path..."
mkdir -p "${VSCODE_DIR}"

# Use a quick inline Python script to safely update settings.json
# This prevents overwriting other settings (like typescript.tsdk)
python3 -c "
import json
import os

settings_file = '${SETTINGS_FILE}'
settings = {}

# Load existing settings if the file exists
if os.path.exists(settings_file):
    try:
        with open(settings_file, 'r') as f:
            settings = json.load(f)
    except json.JSONDecodeError:
        pass # File is empty or corrupted, start fresh

# Inject the correct python interpreter path
settings['python.defaultInterpreterPath'] = '\${workspaceFolder}/${VENV_REL_PATH}'

# (Optional) explicitly point basedpyright to the same environment
settings['basedpyright.pythonPath'] = '\${workspaceFolder}/${VENV_REL_PATH}'

# Save the updated settings
with open(settings_file, 'w') as f:
    json.dump(settings, f, indent=2)
"

echo "✅ Setup complete! The IDE will now use the correct Python interpreter."
