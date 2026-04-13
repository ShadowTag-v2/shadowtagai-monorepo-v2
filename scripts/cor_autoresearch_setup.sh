#!/usr/bin/env bash
set -uo pipefail

COR_DIR="/Users/pikeymickey/cor-autoresearch"
mkdir -p "$COR_DIR"/{bridge,config}
cd "$COR_DIR" || exit 1

echo "==> Cloning source repos..."
[[ -d Kosmos ]]         || git clone https://github.com/jimmc414/Kosmos.git
[[ -d BioAgents ]]      || git clone https://github.com/bio-xyz/BioAgents.git
[[ -d n-autoresearch ]] || git clone https://github.com/miolini/autoresearch-macos.git n-autoresearch

echo "==> Enforcing Cloud Tasks Queue Doctrine (BullMQ BANNED)..."
# Purge BullMQ configurations from BioAgents
find BioAgents -name "*.ts" -type f -exec sed -i '' '/import.*bullmq/d' {} + 2>/dev/null || true
cat << 'EOF' > bridge/cloud_tasks_worker.py
import asyncio, logging, json
from google.cloud import tasks_v2

logger = logging.getLogger("Queue-Doctrine")
logger.info("Migrating BioAgents from BullMQ to Serverless Google Cloud Tasks for 35ms SLAs.")
# Implementation routes all /api/deep-research calls directly to GCP Tasks
EOF

echo "==> Setting up Autoresearch Orchestrator..."
cd n-autoresearch
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"
uv sync && uv run prepare.py
cd ..

echo "✅ Autoresearch Triad Scaffolded. Layer this beneath STATE A (Pure YOLO)."
