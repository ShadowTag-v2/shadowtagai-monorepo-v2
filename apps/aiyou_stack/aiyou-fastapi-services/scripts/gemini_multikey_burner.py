#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Gemini Multi-Key Burner
Load balances across 10 Gemini Pro accounts for maximum throughput.
No caching, no rate limiting - burn through quotas fast.
"""

import asyncio
import json
import os
import time
from dataclasses import dataclass
from itertools import cycle
from typing import Any

import google.generativeai as genai
from google.generativeai.types import HarmBlockThreshold, HarmCategory


@dataclass
class KeyStats:
    """Track usage per key."""

    key_id: int
    requests: int = 0
    tokens_used: int = 0
    errors: int = 0
    last_used: float = 0


class MultiKeyGeminiBurner:
    """Load balancer for 10 Gemini Pro accounts.
    Round-robin rotation, no caching, max throughput.
    """

    def __init__(self):
        # Load all 10 API keys
        self.keys: list[str] = []
        for i in range(1, 11):
            key = os.getenv(f"GEMINI_KEY_{i}")
            if key:
                self.keys.append(key)
            else:
                # Fall back to single key repeated
                default_key = os.getenv("GEMINI_API_KEY")
                if default_key:
                    self.keys.append(default_key)

        if not self.keys:
            raise ValueError("No GEMINI_KEY_* or GEMINI_API_KEY environment variables found")

        print(f"///▞ BURNER :: Loaded {len(self.keys)} API keys")

        # Initialize stats per key
        self.stats: dict[int, KeyStats] = {i: KeyStats(key_id=i) for i in range(len(self.keys))}

        # Round-robin iterator
        self.key_cycle = cycle(range(len(self.keys)))
        self.current_idx = 0

        # Safety config (minimal blocking)
        self.safety_config = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }

    def _get_next_key(self) -> tuple[int, str]:
        """Get next key in rotation."""
        idx = next(self.key_cycle)
        return idx, self.keys[idx]

    def _get_model(self, key: str):
        """Configure and return model for a specific key."""
        genai.configure(api_key=key)
        return genai.GenerativeModel("gemini-3.1-flash-lite-preview")  # Fast model for burning

    def generate(self, prompt: str) -> str:
        """Generate with next available key."""
        idx, key = self._get_next_key()
        model = self._get_model(key)

        try:
            response = model.generate_content(prompt, safety_settings=self.safety_config)

            # Update stats
            self.stats[idx].requests += 1
            self.stats[idx].last_used = time.time()

            return response.text
        except Exception as e:
            self.stats[idx].errors += 1
            return f"[Key {idx} Error: {e}]"

    async def generate_async(self, prompt: str) -> str:
        """Async generation for parallel requests."""
        return await asyncio.to_thread(self.generate, prompt)

    async def burn_parallel(self, prompts: list[str], concurrency: int = 10) -> list[str]:
        """Burn through prompts in parallel.

        Args:
            prompts: List of prompts to process
            concurrency: Max concurrent requests (default 10 = all keys)

        """
        semaphore = asyncio.Semaphore(concurrency)

        async def limited_generate(prompt: str) -> str:
            async with semaphore:
                return await self.generate_async(prompt)

        tasks = [limited_generate(p) for p in prompts]
        return await asyncio.gather(*tasks)

    def burn_sequential(self, prompts: list[str]) -> list[str]:
        """Burn through prompts sequentially with key rotation."""
        results = []
        for i, prompt in enumerate(prompts):
            print(f"///▞ BURNER :: Request {i + 1}/{len(prompts)}")
            result = self.generate(prompt)
            results.append(result)
        return results

    def get_stats(self) -> dict[str, Any]:
        """Get usage statistics."""
        total_requests = sum(s.requests for s in self.stats.values())
        total_errors = sum(s.errors for s in self.stats.values())

        return {
            "total_keys": len(self.keys),
            "total_requests": total_requests,
            "total_errors": total_errors,
            "per_key": [
                {
                    "key_id": s.key_id,
                    "requests": s.requests,
                    "errors": s.errors,
                    "last_used": s.last_used,
                }
                for s in self.stats.values()
            ],
        }

    def print_stats(self):
        """Print formatted stats."""
        stats = self.get_stats()
        print("\n" + "=" * 50)
        print("///▞ BURNER STATS")
        print("=" * 50)
        print(f"Total Keys: {stats['total_keys']}")
        print(f"Total Requests: {stats['total_requests']}")
        print(f"Total Errors: {stats['total_errors']}")
        print("\nPer-Key Breakdown:")
        for ks in stats["per_key"]:
            print(f"  Key {ks['key_id']}: {ks['requests']} requests, {ks['errors']} errors")
        print("=" * 50)


async def main():
    """Demo: Burn through test prompts."""
    burner = MultiKeyGeminiBurner()

    # Generate 100 test prompts
    test_prompts = [
        f"Generate a unique code snippet #{i}: Write a Python function for {['sorting', 'searching', 'caching', 'logging', 'validation'][i % 5]}"
        for i in range(100)
    ]

    print(f"///▞ BURNER :: Starting burn of {len(test_prompts)} prompts")
    start = time.time()

    # Burn in parallel
    results = await burner.burn_parallel(test_prompts, concurrency=10)

    elapsed = time.time() - start
    print(f"\n///▞ BURNER :: Completed in {elapsed:.2f}s")
    print(f"///▞ BURNER :: Rate: {len(test_prompts) / elapsed:.1f} requests/sec")

    burner.print_stats()

    # Save results
    output_path = "/Users/pikeymickey/Documents/Claude Code/Code/Claude Demo/shadowtag_v4-fastapi-services/burn_results.json"
    with open(output_path, "w") as f:
        json.dump(
            {
                "stats": burner.get_stats(),
                "elapsed_seconds": elapsed,
                "requests_per_second": len(test_prompts) / elapsed,
                "results_count": len(results),
            },
            f,
            indent=2,
        )
    print(f"\n///▞ BURNER :: Results saved to {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
