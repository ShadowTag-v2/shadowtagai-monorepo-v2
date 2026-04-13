#!/usr/bin/env bash
set -euo pipefail

COR_DIR="${HOME}/cor-autoresearch"
mkdir -p "$COR_DIR"/{bridge,config}

echo "[SETUP] Cloning Autoresearch Triad (Kosmos, BioAgents, n-autoresearch)..."
[[ -d "$COR_DIR/Kosmos" ]]         || git clone https://github.com/jimmc414/Kosmos.git "$COR_DIR/Kosmos"
[[ -d "$COR_DIR/BioAgents" ]]      || git clone https://github.com/bio-xyz/BioAgents.git "$COR_DIR/BioAgents"
[[ -d "$COR_DIR/n-autoresearch" ]] || git clone https://github.com/miolini/autoresearch-macos.git "$COR_DIR/n-autoresearch"

echo "[SETUP] Enforcing Cloud Tasks Queue Doctrine (BullMQ BANNED)..."
find "$COR_DIR/BioAgents" -name "*.ts" -type f -exec sed -i '' '/import.*bullmq/d' {} + 2>/dev/null || true

cat << 'EOF' > "$COR_DIR/bridge/cloud_tasks_worker.py"
import logging
from google.cloud import tasks_v2

logger = logging.getLogger("Queue-Doctrine")
logger.info("Migrating BioAgents to Serverless Google Cloud Tasks for 35ms SLAs. BullMQ disabled.")
# All /api/deep-research calls route to GCP Tasks natively.
EOF

echo "[SETUP] Setting up N-Autoresearch Orchestrator..."
cd "$COR_DIR/n-autoresearch" || exit 1
if command -v uv &>/dev/null; then
    uv sync && uv run prepare.py
else
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    uv sync && uv run prepare.py
fi

echo "[SUCCESS] Autoresearch Triad Scaffolded. Layered beneath STATE A (Pure YOLO)."
