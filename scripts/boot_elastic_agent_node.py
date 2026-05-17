# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import os
import sys

# Append internal paths for ANE bridge and local libraries
sys.path.append(
  os.path.abspath(
    os.path.join(
      os.path.dirname(__file__), "../apps/aiyou_stack/aiyou-fastapi-services"
    )
  )
)
sys.path.append(
  os.path.abspath(os.path.join(os.path.dirname(__file__), "../libs/kvcached"))
)

try:
  from zero_cpu_router import dispatch_compute
except ImportError:
  print("[Warning] zero_cpu_router not found or misconfigured. ANE routing disabled.")
  dispatch_compute = None

try:
  import kvcached
  from vllm import LLM
except ImportError:
  print("[Warning] vllm or kvcached not found. GPU Elastic fallback disabled.")
  kvcached = None
  LLM = None


class PnklnHybridEngine:
  """
  The master Pnkln orchestration engine.
  Routes inference workloads dynamically between the zero-overhead Apple Neural Engine (ANE)
  via Pickle Rick (ane_bridge.py), and the highly elastic abstract GPU caching layer (kvcached).
  """

  def __init__(
    self, model_path: str, max_concurrent_agents: int = 50, prefer_ane: bool = True
  ):
    self.prefer_ane = prefer_ane
    self.model_path = model_path
    self.gpu_engine = None

    print(f"[Boot] Initializing Pnkln Hybrid Engine: {model_path}")

    # 1. Attempt ANE (Apple Neural Engine) Zero-CPU Boot First
    if self.prefer_ane and dispatch_compute:
      print("[Boot] Routing to ANE master dispatch (zero_cpu_router.py)...")
      # dispatch_compute implicitly orchestrates ane_bridge.py (Pickle Rick)
      # which talks to the C-bridge in third_party/ANE/bridge/
      self.mode = "ANE_ZERO_CPU"

    # 2. Fallback / Scaling to Virtualized GPU KV Cache
    elif kvcached and LLM:
      print("[Boot] ANE disabled or unavailable. Spinning up Elastic GPU (kvcached)...")
      kvcached.init(
        enable_virtual_memory=True, max_logical_cache_size_gb=120, eviction_policy="lru"
      )
      self.gpu_engine = LLM(
        model=self.model_path,
        trust_remote_code=True,
        gpu_memory_utilization=0.9,
        enable_kvcached=True,
      )
      self.mode = "ELASTIC_GPU"

    else:
      raise RuntimeError(
        "[Boot Error] No inferrence backbone available (ANE or GPU/KVCached)."
      )

  def generate(self, prompt: str):
    """
    Executes standard prompt completion over the actively routed compute plane.
    """
    if self.mode == "ANE_ZERO_CPU":
      # Delegate to the master ANE router, keeping CPU/GPU idle
      print("[Compute] Delegating to ANE Pickle Rick...")
      return dispatch_compute(prompt, model=self.model_path)

    elif self.mode == "ELASTIC_GPU":
      print("[Compute] Delegating to Elastic GPU Cache...")
      return self.gpu_engine.generate(prompt)


if __name__ == "__main__":
  # Example execution integrating both user requests:
  # 'fold into here' ANE logic + previous elastic cache logic
  engine = PnklnHybridEngine(
    model_path="meta-llama/Meta-Llama-3.1-8B-Instruct", prefer_ane=True
  )
  # response = engine.generate("Establish material facts regarding the requested arbitration.")
