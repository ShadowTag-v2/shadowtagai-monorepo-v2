#!/usr/bin/env python3
"""Gemini Sustained Load Calculator & Runner
Maximum indefinite throughput without quota exhaustion.
"""

import asyncio
import json
import os
import time
from dataclasses import dataclass

import google.generativeai as genai
from google.generativeai.types import HarmBlockThreshold, HarmCategory


@dataclass
class QuotaLimits:
    """Gemini Pro API quota limits per account."""

    # Free tier limits (conservative estimates)
    requests_per_minute: int = 60
    requests_per_day: int = 1500
    tokens_per_minute: int = 1_000_000

    # Pro subscription adds more headroom
    # But we use free tier limits for sustainability


class SustainedLoadEngine:
    """Maximum sustained load without quota exhaustion.

    Math for 10 accounts:
    - 60 RPM × 10 = 600 RPM total
    - But daily limit: 1500/day × 10 = 15,000/day
    - 15,000 / 1440 minutes = 10.4 RPM sustained

    To avoid daily exhaustion:
    - Target: 10 RPM per account = 100 RPM total
    - Safety margin: 8 RPM per account = 80 RPM total
    """

    # Sustainable rates (won't exhaust daily quota)
    SAFE_RPM_PER_KEY = 8  # Conservative
    MAX_RPM_PER_KEY = 10  # Aggressive

    def __init__(self, mode: str = "safe"):
        # Load keys
        self.keys: list[str] = []
        for i in range(1, 11):
            key = os.getenv(f"GEMINI_KEY_{i}")
            if key:
                self.keys.append(key)

        if not self.keys:
            default = os.getenv("GEMINI_API_KEY")
            if default:
                self.keys = [default]

        if not self.keys:
            raise ValueError("No API keys found")

        self.num_keys = len(self.keys)
        self.mode = mode

        # Calculate rates
        rpm_per_key = self.SAFE_RPM_PER_KEY if mode == "safe" else self.MAX_RPM_PER_KEY
        self.total_rpm = rpm_per_key * self.num_keys
        self.interval = 60.0 / self.total_rpm  # Seconds between requests

        # Stats
        self.total_requests = 0
        self.total_errors = 0
        self.start_time = None

        # Key rotation
        self.current_key_idx = 0

        # Safety config
        self.safety_config = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }

        print(f"///▞ SUSTAINED :: {self.num_keys} keys loaded")
        print(f"///▞ SUSTAINED :: Mode: {mode}")
        print(f"///▞ SUSTAINED :: Target: {self.total_rpm} RPM ({self.interval:.2f}s interval)")
        print(f"///▞ SUSTAINED :: Daily capacity: {self.total_rpm * 60 * 24:,} requests")

    def _next_key(self) -> str:
        """Round-robin key selection."""
        key = self.keys[self.current_key_idx]
        self.current_key_idx = (self.current_key_idx + 1) % self.num_keys
        return key

    def _get_model(self, key: str):
        """Get model for key."""
        genai.configure(api_key=key)
        return genai.GenerativeModel("gemini-3.1-flash-lite-preview")

    async def generate(self, prompt: str) -> str:
        """Generate with rate limiting."""
        key = self._next_key()
        model = self._get_model(key)

        try:
            response = await asyncio.to_thread(
                model.generate_content,
                prompt,
                safety_settings=self.safety_config,
            )
            self.total_requests += 1
            return response.text
        except Exception as e:
            self.total_errors += 1
            return f"[Error: {e}]"

    async def run_sustained(self, prompt_generator, duration_hours: float = None):
        """Run sustained load indefinitely or for specified duration.

        Args:
            prompt_generator: Callable that returns next prompt
            duration_hours: None for indefinite, or hours to run

        """
        self.start_time = time.time()
        end_time = None
        if duration_hours:
            end_time = self.start_time + (duration_hours * 3600)

        print(
            f"\n///▞ SUSTAINED :: Starting {'indefinite' if not end_time else f'{duration_hours}h'} run",
        )
        print("///▞ SUSTAINED :: Press Ctrl+C to stop\n")

        try:
            while True:
                # Check duration
                if end_time and time.time() >= end_time:
                    break

                # Generate
                prompt = prompt_generator()
                await self.generate(prompt)

                # Log progress every 100 requests
                if self.total_requests % 100 == 0:
                    elapsed = time.time() - self.start_time
                    actual_rpm = (self.total_requests / elapsed) * 60
                    print(
                        f"///▞ SUSTAINED :: {self.total_requests} requests, "
                        f"{actual_rpm:.1f} actual RPM, "
                        f"{self.total_errors} errors",
                    )

                # Rate limit
                await asyncio.sleep(self.interval)

        except KeyboardInterrupt:
            print("\n///▞ SUSTAINED :: Stopped by user")

        self.print_stats()

    async def run_batch_sustained(self, prompts: list[str], loop: bool = True):
        """Run through a batch of prompts at sustained rate.

        Args:
            prompts: List of prompts
            loop: Whether to loop through prompts indefinitely

        """
        idx = 0

        def get_prompt():
            nonlocal idx
            prompt = prompts[idx % len(prompts)]
            idx += 1
            if not loop and idx >= len(prompts):
                raise StopIteration
            return prompt

        await self.run_sustained(get_prompt)

    def print_stats(self):
        """Print final stats."""
        elapsed = time.time() - self.start_time if self.start_time else 0
        actual_rpm = (self.total_requests / elapsed) * 60 if elapsed > 0 else 0

        print("\n" + "=" * 60)
        print("///▞ SUSTAINED LOAD STATS")
        print("=" * 60)
        print(f"Duration: {elapsed / 3600:.2f} hours ({elapsed:.0f} seconds)")
        print(f"Total Requests: {self.total_requests:,}")
        print(f"Total Errors: {self.total_errors}")
        print(f"Error Rate: {(self.total_errors / max(1, self.total_requests)) * 100:.2f}%")
        print(f"Actual RPM: {actual_rpm:.1f}")
        print(f"Target RPM: {self.total_rpm}")
        print(f"Efficiency: {(actual_rpm / self.total_rpm) * 100:.1f}%")
        print("=" * 60)

        # Projection
        daily_projection = actual_rpm * 60 * 24
        print(f"\nProjected Daily Throughput: {daily_projection:,.0f} requests")
        print(f"Projected Monthly Throughput: {daily_projection * 30:,.0f} requests")


def code_generation_prompts():
    """Generator for code-related prompts."""
    tasks = [
        "Write a Python function to validate email addresses",
        "Create a Redis caching decorator in Python",
        "Implement a rate limiter using token bucket algorithm",
        "Write a FastAPI endpoint for user authentication",
        "Create a Kubernetes deployment YAML for a Python app",
        "Write unit tests for a REST API client",
        "Implement a circuit breaker pattern in Python",
        "Create a Dockerfile for a FastAPI application",
        "Write a GitHub Actions workflow for CI/CD",
        "Implement a pub/sub system using Redis",
    ]
    idx = 0
    while True:
        yield f"{tasks[idx % len(tasks)]} (variation #{idx // len(tasks) + 1})"
        idx += 1


async def main():
    """Demo sustained load."""
    import argparse

    parser = argparse.ArgumentParser(description="Gemini Sustained Load Runner")
    parser.add_argument(
        "--mode",
        choices=["safe", "aggressive"],
        default="safe",
        help="Rate limiting mode",
    )
    parser.add_argument(
        "--hours",
        type=float,
        default=None,
        help="Duration in hours (default: indefinite)",
    )
    args = parser.parse_args()

    engine = SustainedLoadEngine(mode=args.mode)

    # Use code generation prompts
    prompt_gen = code_generation_prompts()

    await engine.run_sustained(lambda: next(prompt_gen), duration_hours=args.hours)

    # Save results
    output_path = "/Users/pikeymickey/Documents/Claude Code/Code/Claude Demo/shadowtag_v4-fastapi-services/sustained_results.json"
    with open(output_path, "w") as f:
        elapsed = time.time() - engine.start_time if engine.start_time else 0
        json.dump(
            {
                "mode": args.mode,
                "num_keys": engine.num_keys,
                "target_rpm": engine.total_rpm,
                "total_requests": engine.total_requests,
                "total_errors": engine.total_errors,
                "elapsed_seconds": elapsed,
                "actual_rpm": (engine.total_requests / elapsed) * 60 if elapsed > 0 else 0,
            },
            f,
            indent=2,
        )
    print(f"\nResults saved to {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
