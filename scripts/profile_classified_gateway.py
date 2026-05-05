#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""cProfile hotspot analysis for ClassifiedGateway + BashSecurityClassifier.

Profiles the Tier 1.75 hot-path where shell tool invocations are routed
through the 30-check BashSecurityClassifier pipeline.

Usage:
    python scripts/profile_classified_gateway.py
"""

from __future__ import annotations

import cProfile
import pstats
import io
import time
from pathlib import Path
from unittest.mock import MagicMock

# --- Setup mock environment ---

# Mock the dependencies that require YAML configs and external modules
import sys

# Create mock modules for imports that won't resolve in isolation
mock_modules = [
    'agnt_classifier',
    'tool_gateway.block_allow_engine',
    'tool_gateway.gateway',
    'tool_gateway.sandbox_path_resolver',
    'tool_gateway.telemetry',
]

for mod in mock_modules:
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

# Now import the actual classifier
monorepo_root = str(Path(__file__).resolve().parent.parent)
if monorepo_root not in sys.path:
    sys.path.insert(0, monorepo_root)

from packages.agnt_bash_classifier.classifier import BashSecurityClassifier


def profile_classifier_pipeline() -> None:
    """Profile the 30-check pipeline with various command types."""

    classifier = BashSecurityClassifier(telemetry=None)

    # Test commands: mix of safe, blocked, and edge cases
    test_commands = [
        # Safe commands (full 30-check traversal)
        "echo hello world",
        "ls -la /tmp",
        "cat README.md",
        "git status",
        "python3 --version",
        "npm run build",
        "pip install requests",
        "cd /workspace && ls",
        "grep -r 'pattern' src/",
        "find . -name '*.py' -type f",
        # Blocked commands (short-circuit at various points)
        "echo hello |",                          # Check 1
        "jq 'def f: .; f' input.json",          # Check 2
        "echo `whoami`",                          # Check 5
        "echo $BASH_ENV",                         # Check 6
        "echo $((1+1))",                          # Check 25
        "base64 -d payload.txt",                  # Check 27
    ]

    iterations = 10_000

    print(f"Profiling {len(test_commands)} commands × {iterations} iterations...")
    print(f"Total invocations: {len(test_commands) * iterations:,}")
    print()

    # Warm-up
    for cmd in test_commands:
        classifier.classify(cmd)

    # Profile
    profiler = cProfile.Profile()
    profiler.enable()

    t_start = time.monotonic()
    for _ in range(iterations):
        for cmd in test_commands:
            classifier.classify(cmd)
    t_end = time.monotonic()

    profiler.disable()

    total_ms = (t_end - t_start) * 1000
    total_calls = len(test_commands) * iterations
    avg_us = (total_ms / total_calls) * 1000  # microseconds

    print(f"=== Performance Summary ===")
    print(f"Total time: {total_ms:.1f}ms")
    print(f"Total calls: {total_calls:,}")
    print(f"Avg per call: {avg_us:.1f}µs ({total_ms / total_calls:.3f}ms)")
    print(f"Target: <5ms per call — {'✅ PASS' if avg_us < 5000 else '❌ FAIL'}")
    print()

    # Print top 20 hotspots
    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats('cumulative')
    stats.print_stats(20)
    print(stream.getvalue())

    # Print callee breakdown for classify()
    stream2 = io.StringIO()
    stats2 = pstats.Stats(profiler, stream=stream2)
    stats2.sort_stats('tottime')
    stats2.print_stats(20)
    print("=== By Total Time ===")
    print(stream2.getvalue())


if __name__ == "__main__":
    profile_classifier_pipeline()
