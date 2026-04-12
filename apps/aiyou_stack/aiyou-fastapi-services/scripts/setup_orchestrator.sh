#!/bin/bash
set -e

echo "Setting up ShadowTag-v2 Orchestrator..."

# Install dependencies
echo "Installing Python dependencies..."
python3 -m pip install huggingface_hub langchain langchain-openai langchain-core openai

# Create directories
echo "Creating directories..."
mkdir -p .cursor/agents
mkdir -p docs/model-spec

# Download Model Spec v2 (if not exists)
if [ ! -f docs/model-spec/model_spec.md ]; then
    echo "Downloading OpenAI Model Spec v2..."
    curl -L https://raw.githubusercontent.com/openai/model_spec/main/model_spec.md -o docs/model-spec/model_spec.md || echo "Failed to download model spec, skipping."
fi

echo "Setup complete. Please ensure HF_KEY_1, HF_KEY_2, and OPENAI_API_KEY are set in your environment."
