#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
cd "$ROOT"

echo "=== PNKLN AUTO-UPDATE DAEMON ==="
echo "Time: $(date)"

# Invoke the meta-evolve layer to let the swarm modify its underlying prompt templates.
source .venv/bin/activate
export PYTHONPATH="$ROOT"
python3 core/meta-evolve.py

# Invoke the nightly evolve loop
python3 core/pnkln-evolve.py --dry-run

echo "Daemon Execution Complete."
