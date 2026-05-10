#!/bin/bash
set -e

echo "🚀 Starting Repository Setup (Skipping System Install)..."

# 3. Clone/Setup Repositories

# Current Repo (ShadowTag-v2-fastapi-services)
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

echo "🎉 Repository Setup Complete!"
