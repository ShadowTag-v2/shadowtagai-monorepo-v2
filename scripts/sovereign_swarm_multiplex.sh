#!/usr/bin/env bash

echo "=================================================="
echo "    SOVEREIGN MLX: MULTIPLEX SWARM INITIATOR"
echo "=================================================="
echo ""

# 1. Hardware Override (Elevate GPU RAM Limit to 58GB)
echo "[i] Requesting superuser to unlock macOS GPU iogpu limit..."
echo "[i] This allocates up to 58GB of the 64GB Unified Memory pool strictly for the MLX context window."
sudo sysctl iogpu.wired_limit_mb=59392

echo ""
echo "[+] Hardware limits unlocked."
echo "[i] Booting the TurboQuant KV-Cache Distillation Phase..."

# 2. Build the Sovereign TurboQuant Slab
cd /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball
export PYTHONPATH=$PYTHONPATH:$(pwd)/core/sovereign_mlx
source .venv/bin/activate

# We run the slab builder which utilizes the newly written MLXTurboQuantCompressorV2
echo "[>] Forging the 1.5 Million Token Master Memory Slab..."
python core/sovereign_mlx/kv_cache_slab.py --build --force

echo ""
echo "[+] Master Memory Slab generated in data/sovereign_mlx/"
echo "[>] Booting the Unified Codebase Swarm Loop..."

# Load env variables safely for Gemini Keys
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# 3. Fire the Local Agent Swarm
python scripts/gemini_agent_swarm.py --query "Execute deep AST trace across apps/gitnexus and project financial impact."
