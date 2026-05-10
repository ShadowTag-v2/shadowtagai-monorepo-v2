#!/usr/bin/env bash
# kvcached-aware inference worker launcher
# Applies to Sovereign Cloud Colab/GCP workers running vLLM or SGLang.
# On Apple Silicon (MPS) this is a no-op — kvcached requires CUDA.
set -euo pipefail

ENGINE="${KVCACHED_ENGINE:-vllm}"          # vllm | sglang
MODEL="${KVCACHED_MODEL:-meta-llama/Llama-3.2-1B-Instruct}"
PORT="${KVCACHED_PORT:-12346}"
GPU_MEM_FRAC="${KVCACHED_GPU_MEM_FRAC:-0.4}"  # low default for multi-model colocate

export ENABLE_KVCACHED=true
export KVCACHED_AUTOPATCH=1

# Install kvcached if not present (Colab / fresh worker)
if ! python3 -c "import kvcached" 2>/dev/null; then
  echo "[kvcached] Installing..."
  pip install "$(dirname "$0")/../third_party/kvcached" --no-build-isolation -q
fi

echo "[kvcached] Launching $ENGINE | model=$MODEL | port=$PORT"

if [[ "$ENGINE" == "vllm" ]]; then
  python3 -m vllm.entrypoints.openai.api_server \
    --model "$MODEL" \
    --port "$PORT" \
    --gpu-memory-utilization "$GPU_MEM_FRAC" \
    "$@"
elif [[ "$ENGINE" == "sglang" ]]; then
  python3 -m sglang.launch_server \
    --model-path "$MODEL" \
    --port "$PORT" \
    --mem-fraction-static "$GPU_MEM_FRAC" \
    "$@"
else
  echo "Unknown engine: $ENGINE (use vllm or sglang)" && exit 1
fi
