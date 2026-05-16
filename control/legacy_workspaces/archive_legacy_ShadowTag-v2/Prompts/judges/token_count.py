#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Token counter for Judge #6 prompt verification.
Estimates token count using simple word-based approximation.
"""


def estimate_tokens(text: str) -> int:
  """
  Rough token estimation: ~0.75 tokens per word for English text.
  More accurate would require tiktoken, but this gives ballpark.
  """
  words = len(text.split())
  # GPT tokenizers average ~1.3 words per token
  # So tokens ≈ words / 1.3 ≈ words * 0.75
  return int(words / 1.3)


def count_characters(text: str) -> int:
  """Count total characters including whitespace."""
  return len(text)


if __name__ == "__main__":
  with open("judge_6_v2_compressed.txt") as f:
    content = f.read()

  words = len(content.split())
  chars = count_characters(content)
  tokens_estimated = estimate_tokens(content)

  print("=" * 60)
  print("JUDGE #6 V2 COMPRESSED - TOKEN ANALYSIS")
  print("=" * 60)
  print(f"Words:              {words}")
  print(f"Characters:         {chars}")
  print(f"Estimated Tokens:   {tokens_estimated}")
  print("=" * 60)
  print("Target:             <450 tokens (to ensure p99 < 90ms)")
  print(f"Status:             {'✓ PASS' if tokens_estimated < 450 else '✗ FAIL'}")
  print("=" * 60)
  print()
  print("Note: Token estimate uses 1.3 words/token ratio.")
  print("For exact count, use tiktoken with cl100k_base encoding.")
