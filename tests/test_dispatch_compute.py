#!/usr/bin/env python3
"""Test script for dispatch_compute() 4-tier cascade.

Verifies:
  1. ANE bridge loads and init works
  2. TurboQuant KV cache compiles (if torch available)
  3. Vertex AI fallback path (litellm)
  4. dispatch_compute() returns a result
"""

from __future__ import annotations

import sys
import os

# Add aiyou-fastapi-services to path for modules that live there
# (ane_bridge, zero_cpu_router, vector_db, etc.) but DO NOT let it
# shadow the root `app` package.  We append instead of insert-at-0
# so that the monorepo-root `app/` always wins for `app.*` imports.
_aiyou_services_dir = os.path.join(
  os.path.dirname(__file__), "..", "apps", "aiyou_stack", "aiyou-fastapi-services"
)
if _aiyou_services_dir not in sys.path:
  sys.path.append(_aiyou_services_dir)


def test_ane_bridge():
  """Test ANE bridge loads and inits."""
  print("=== Test 1: ANE Bridge ===")
  try:
    from ane_bridge import init_bridge

    result = init_bridge()
    print(f"  init_bridge(): {result}")

    # get_compile_count is optional — may not be implemented
    try:
      from ane_bridge import get_compile_count

      print(f"  compile_count: {get_compile_count()}")
    except ImportError:
      print("  compile_count: not implemented (skipped)")

    assert result is True, "ANE bridge init failed"
    print("  ✅ PASS")
  except Exception as e:
    print(f"  ❌ FAIL: {e}")
    raise


def test_turboquant():
  """Test TurboQuant KV cache (requires torch)."""
  print("\n=== Test 2: TurboQuant KV Cache ===")
  try:
    import torch
    from src.ml.turboquant_engine import TurboQuantKVCache

    cache = TurboQuantKVCache(key_dim=64, val_dim=64, bits=3, device="cpu")
    # Create fake KV states: (B=1, H=1, S=4, D=64)
    k = torch.randn(1, 1, 4, 64)
    v = torch.randn(1, 1, 4, 64)
    cache.append(k, v)

    q = torch.randn(1, 1, 1, 64)
    scores = cache.attention_scores(q)
    values = cache.get_values()
    print(f"  Attention scores shape: {scores.shape}")
    print(f"  Values shape: {values.shape}")
    assert scores.numel() > 0, "Empty attention scores"
    print("  ✅ PASS")
  except ImportError:
    import pytest

    pytest.skip("torch not installed")
  except Exception as e:
    print(f"  ❌ FAIL: {e}")
    raise


def test_aimdo_allocator():
  """Test AimdoAllocator (requires torch + psutil)."""
  print("\n=== Test 3: AimdoAllocator ===")
  try:
    import torch
    from src.ml.dynamic_vram import AimdoAllocator, apply_mixquant_blocks

    # MixQuant blockwise rotation
    tensor = torch.randn(128, 256)
    rotated = apply_mixquant_blocks(tensor, block_size=32)
    print(f"  MixQuant: {tensor.shape} → {rotated.shape}")
    assert rotated.shape == tensor.shape, "Shape mismatch"

    # Allocator init
    alloc = AimdoAllocator()
    print(f"  AimdoAllocator created (VBARs: {len(alloc._vbars)})")
    print("  ✅ PASS")
  except ImportError:
    import pytest

    pytest.skip("torch/psutil not installed")
  except Exception as e:
    print(f"  ❌ FAIL: {e}")
    raise


def test_dispatch_compute():
  """Test the dispatch_compute() entry point."""
  print("\n=== Test 4: dispatch_compute() ===")
  try:
    from zero_cpu_router import dispatch_compute, _has_ane

    print(f"  _has_ane(): {_has_ane()}")

    # dispatch_compute(text, prompt_description, examples, file_name)
    result = dispatch_compute(
      text="Hello world, this is a test.",
      prompt_description="Classify the text",
      examples=[{"input": "Hi", "output": "greeting"}],
      file_name="test.txt",
    )
    print(f"  Result type: {type(result)}")
    print(f"  Result: {str(result)[:200]}")
    print("  ✅ PASS")
  except Exception as e:
    print(f"  ❌ FAIL: {e}")
    # This is expected to fail without proper model/litellm setup
    print("  (Expected — no model loaded, all tiers cascaded)")
    raise


def test_vector_db():
  """Test vector_db module loads."""
  print("\n=== Test 5: Vector DB ===")
  try:
    from vector_db import DB_PATH, TABLE_NAME, EMBED_DIM

    print(f"  DB_PATH: {DB_PATH}")
    print(f"  TABLE_NAME: {TABLE_NAME}")
    print(f"  EMBED_DIM: {EMBED_DIM}")
    assert EMBED_DIM == 768
    print("  ✅ PASS")
  except Exception as e:
    print(f"  ❌ FAIL: {e}")
    raise


if __name__ == "__main__":
  results = {
    "ane_bridge": test_ane_bridge(),
    "turboquant": test_turboquant(),
    "aimdo": test_aimdo_allocator(),
    "dispatch": test_dispatch_compute(),
    "vector_db": test_vector_db(),
  }
  print("\n" + "=" * 60)
  print("SUMMARY")
  print("=" * 60)
  for name, result in results.items():
    status = "✅" if result is True else ("⚠️ SKIP" if result is None else "❌")
    print(f"  {name}: {status}")

  failures = sum(1 for r in results.values() if r is False)
  print(f"\n{'ALL PASSED' if failures == 0 else f'{failures} FAILED'}")
  sys.exit(failures)
