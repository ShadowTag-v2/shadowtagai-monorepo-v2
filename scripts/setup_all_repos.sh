#!/bin/bash
set -e
cd /Users/pikeymickey/ShadowTag-v2-fastapi-services

echo "🚀 Starting Setup Script..."

# 1. Homebrew Setup
if ! command -v brew &> /dev/null; then
    echo "🍺 Homebrew not found. Installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # Add Homebrew to PATH for Apple Silicon or Intel
    if [[ "$(uname -m)" == "arm64" ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    else
        echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/usr/local/bin/brew shellenv)"
    fi
else
    echo "✅ Homebrew already installed."
    echo "🔄 Updating Homebrew..."
    brew update
fi

# 2. Install Core Dependencies
echo "📦 Installing core dependencies..."
brew install git gh python@3.11 node

# Link python@3.11 if needed or ensure it's in path
# (Homebrew usually requires manual linking or path adjustment for keg-only)
echo "   Note: You may need to link python@3.11 or add it to your PATH if not already done."

# 3. Clone/Setup Repositories

# Current Repo (ShadowTag-v2-fastapi-services)
# Assuming we are running this script FROM the repo, but let's ensure dependencies are installed.
echo "🐍 Installing dependencies for ShadowTag-v2-fastapi-services..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
fi
if [ -f "package.json" ]; then
    npm install
fi

# erik-hancock-llm-memory
REPO_MEMORY="erik-hancock-llm-memory"
URL_MEMORY="https://github.com/ehanc69/erik-hancock-llm-memory.git"

if [ ! -d "$REPO_MEMORY" ]; then
    echo "📥 Cloning $REPO_MEMORY..."
    git clone "$URL_MEMORY"
else
    echo "✅ $REPO_MEMORY directory exists. Checking git status..."
    cd "$REPO_MEMORY"
    if [ -d ".git" ]; then
        echo "   Pulling latest changes..."
        git pull origin main || git pull origin master
    else
        echo "   Initializing git repo..."
        git init
        git remote add origin "$URL_MEMORY"
        git pull origin main || git pull origin master
    fi
    cd ..
fi

# Install dependencies for erik-hancock-llm-memory
if [ -d "$REPO_MEMORY" ]; then
    echo "🐍 Installing dependencies for $REPO_MEMORY..."
    if [ -f "$REPO_MEMORY/requirements.txt" ]; then
        pip3 install -r "$REPO_MEMORY/requirements.txt"
    fi
    # Check for specific drive requirements mentioned in docs
    if [ -f "$REPO_MEMORY/requirements-drive.txt" ]; then
        pip3 install -r "$REPO_MEMORY/requirements-drive.txt"
    fi
fi


# 4. Nice-to-have Tools
echo "✨ Installing 'Nice to Have' tools..."
TOOLS=(
    "jq"        # JSON processor
    "yq"        # YAML processor
    "ripgrep"   # Fast grep (rg)
    "fd"        # Fast find
    "bat"       # Better cat
    "fzf"       # Fuzzy finder
    "htop"      # Process viewer
    "tldr"      # Simplified man pages
    "tree"      # Directory structure viewer
    "wget"
)

for tool in "${TOOLS[@]}"; do
    if brew list "$tool" &>/dev/null; then
        echo "   ✅ $tool already installed"
    else
        echo "   ⬇️  Installing $tool..."
        brew install "$tool"
    fi
done

# 5. Google Cloud SDK (Optional but recommended for this project)
if ! command -v gcloud &> /dev/null; then
    echo "☁️  Installing Google Cloud SDK..."
    brew install --cask google-cloud-sdk
else
    echo "✅ Google Cloud SDK already installed."
fi

# 6. Install R
if ! command -v R &> /dev/null; then
    echo "📉 Installing R..."
    brew install r
else
    echo "✅ R already installed."
fi

# Update VS Code settings for R
R_PATH=$(which R || echo "/opt/homebrew/bin/R")
SETTINGS_FILE=".vscode/settings.json"
if [ -f "$SETTINGS_FILE" ]; then
    echo "⚙️  Updating $SETTINGS_FILE..."
    python3 -c "import json; import os;
with open('$SETTINGS_FILE', 'r') as f: data = json.load(f);
data['r.rpath.mac'] = '$R_PATH';
with open('$SETTINGS_FILE', 'w') as f: json.dump(data, f, indent=2)"
    echo "✅ Updated r.rpath.mac to $R_PATH"
fi

echo "🎉 Setup Complete! You are ready to go."
read -p "Press [Enter] to close this window..."
