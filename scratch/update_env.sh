#!/bin/bash
export PATH="/usr/local/share/dotnet:$PATH"
export CI=true DEBIAN_FRONTEND=noninteractive
echo "Updating pip, curl, php, homebrew..."
brew update && brew upgrade curl php

echo "Re-running uv sync and npm install..."
uv sync
npm install --no-audit --no-fund

echo "Recompiling mlx-metal, grpcio, google-cloud-aiplatform, and numpy..."
source .venv/bin/activate
uv pip install --reinstall mlx-metal grpcio google-cloud-aiplatform numpy
