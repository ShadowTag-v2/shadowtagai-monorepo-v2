#!/usr/bin/env bash
set -euo pipefail

echo "🚀 AiYou Safety-Case SaaS Framework - Post-Create Setup"

# Install Python tools (uv, ruff)
echo "📦 Installing Astral tools (uv, Ruff)..."
curl -LsSf https://astral.sh/uv/install.sh | sh
pip install --user ruff

# Install Node dependencies (router, orchestrator)
echo "📦 Installing Node dependencies..."
if [ -f package.json ]; then
  npm install
fi

if [ -f router/package.json ]; then
  cd router && npm install && cd ..
fi

if [ -f tools/orchestrator/package.json ]; then
  cd tools/orchestrator && npm install && cd ..
fi

# Install Python dependencies (computer-use, ingestion)
echo "📦 Installing Python dependencies..."
if [ -f computer-use/requirements.txt ]; then
  pip install --user -r computer-use/requirements.txt
fi

if [ -f ingestion/moondream-requirements.txt ]; then
  pip install --user -r ingestion/moondream-requirements.txt || echo "⚠️ Some Python packages may not be available yet"
fi

# Install Playwright (for Gemini Computer-Use)
echo "📦 Installing Playwright..."
npx --yes playwright@latest install chromium || echo "⚠️ Playwright install skipped (optional)"

# Create directories
echo "📁 Creating artifact directories..."
mkdir -p .ci patches explain review ingest/out

# Setup Git safe directory (for Codespaces)
git config --global --add safe.directory /workspaces/aiyou-fastapi-services || true

echo "✅ Post-create setup complete!"
echo ""
echo "📋 Quick Start Commands:"
echo "  - npm run dev                    # Start multi-model router"
echo "  - npm run triple:pass            # Run ACE workflow"
echo "  - python -m ingestion.moondream_ingest  # Run vision ingestion"
echo "  - python -m computer_use.agent   # Run Computer-Use agent"
echo ""
echo "🔐 Safety Framework:"
echo "  - safety/item_definition.md      # Service definition"
echo "  - safety/risk_register.yaml      # Risk assessment"
echo "  - safety/monitoring/slos.json    # SLO targets"
echo ""
echo "Happy coding! 🎉"
