#!/usr/bin/env bash
set -euo pipefail

echo "Enabling required Google Cloud services..."
# gcloud services enable aiplatform.googleapis.com

echo "Installing Python dependencies..."
python3 -m pip install -q --upgrade vertexai google-cloud-aiplatform supabase

echo "Setup complete."
