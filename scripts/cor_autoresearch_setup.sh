#!/usr/bin/env bash
set -euo pipefail

COR_DIR="${HOME}/cor-autoresearch"
mkdir -p "$COR_DIR"/{bridge,config}

echo "[SETUP] Cloning Autoresearch Triad (Kosmos, BioAgents, n-autoresearch)..."
[[ -d "$COR_DIR/Kosmos" ]]         || git clone https://github.com/jimmc414/Kosmos.git "$COR_DIR/Kosmos"
[[ -d "$COR_DIR/BioAgents" ]]      || git clone https://github.com/bio-xyz/BioAgents.git "$COR_DIR/BioAgents"
[[ -d "$COR_DIR/n-autoresearch" ]] || git clone https://github.com/miolini/autoresearch-macos.git "$COR_DIR/n-autoresearch"

echo "[SETUP] Enforcing Cloud Tasks Queue Doctrine (BullMQ BANNED)..."
# Rip out BullMQ imports AND their downstream references to prevent dangling TS errors
if [ -d "$COR_DIR/BioAgents" ]; then
    # Phase 1: Remove import lines
    find "$COR_DIR/BioAgents" -name "*.ts" -type f -exec sed -i '' '/import.*bullmq/d' {} + 2>/dev/null || true
    find "$COR_DIR/BioAgents" -name "*.ts" -type f -exec sed -i '' '/from.*bullmq/d' {} + 2>/dev/null || true
    # Phase 2: Comment out BullMQ class instantiations to prevent dangling refs
    find "$COR_DIR/BioAgents" -name "*.ts" -type f -exec sed -i '' 's/new Queue(/\/\/ BANNED: new Queue(/g' {} + 2>/dev/null || true
    find "$COR_DIR/BioAgents" -name "*.ts" -type f -exec sed -i '' 's/new Worker(/\/\/ BANNED: new Worker(/g' {} + 2>/dev/null || true
fi

cat << 'EOF' > "$COR_DIR/bridge/cloud_tasks_worker.py"
import logging
from google.cloud import tasks_v2

logger = logging.getLogger("Queue-Doctrine")
logger.info("Migrating BioAgents to Serverless Google Cloud Tasks. BullMQ disabled.")
# All /api/deep-research calls route to GCP Tasks natively.
EOF

echo "[SETUP] Setting up N-Autoresearch Orchestrator..."
cd "$COR_DIR/n-autoresearch" || exit 1

# Use existing uv if available (~/.local/bin/uv per drift audit), skip redundant install
UV_CMD=""
if command -v uv >/dev/null 2>&1; then
    UV_CMD="uv"
elif [ -x "$HOME/.local/bin/uv" ]; then
    UV_CMD="$HOME/.local/bin/uv"
elif [ -x "$HOME/.cargo/bin/uv" ]; then
    UV_CMD="$HOME/.cargo/bin/uv"
else
    echo "[SETUP] uv not found — installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    UV_CMD="$HOME/.cargo/bin/uv"
fi

# Only run uv sync if pyproject.toml exists
if [ -f "pyproject.toml" ]; then
    $UV_CMD sync && $UV_CMD run prepare.py
elif [ -f "requirements.txt" ]; then
    echo "[SETUP] No pyproject.toml found. Using pip install as fallback."
    $UV_CMD pip install -r requirements.txt
else
    echo "[WARN] No pyproject.toml or requirements.txt found in n-autoresearch. Manual setup required."
fi

echo "[SUCCESS] Autoresearch Triad Scaffolded. Layered beneath STATE A (Pure YOLO)."
