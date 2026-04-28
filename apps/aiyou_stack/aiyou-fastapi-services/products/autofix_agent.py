# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Pnkln Autofix Agent (Green Loop)
A self-healing TDD loop that fixes failing tests using Vertex AI.

Usage:
    python autofix_agent.py --tests "pytest tests/" --max-iters 5
"""

import argparse
import os
import subprocess

try:
    from google.cloud import aiplatform as v  # noqa: F401
    from google.cloud.aiplatform.explain.metadata.tf.v2 import SavedModelMetadata  # noqa: F401
except ImportError:
    print("Error: google-cloud-aiplatform not installed.")
    print("pip install google-cloud-aiplatform")

# Configuration
MODEL_ID = os.getenv("PNKLN_VERTEX_MODEL", "gemini-pro")
MAX_LINES_PATCH = int(os.getenv("PNKLN_GL_MAX_LINES", "300"))


def run_tests(cmd: str) -> tuple[bool, str]:
    """Run the test command and return (success, output)."""
    print(f"Running tests: {cmd}")
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.returncode == 0, (p.stdout + "\n" + p.stderr)


def ask_vertex_for_patch(test_output: str, write_paths: list[str]) -> str:
    """Ask Vertex AI to generate a patch for the failing tests."""
    f"""You are an expert software engineer (Pnkln Repair Agent).
Your goal is to fix the failing tests below.

Rules:
1. Return a UNIFIED DIFF only. No markdown, no prose, no backticks.
2. Only modify files in these paths: {", ".join(write_paths)}
3. Keep the patch minimal and correct.

Test Output:
{test_output[:10000]}  # Truncated if too long
"""
    # Note: In a real deploy, specific model init would be here.
    # assuming v.init() is called externally or globally configured

    # Placeholder for actual Vertex call structure with Gemini
    # model = v.GenerativeModel(MODEL_ID)
    # response = model.generate_content(prompt)
    # return response.text

    return "diff --git a/src/example.py b/src/example.py\n..."


def apply_patch(patch_content: str) -> bool:
    """Apply a patch file."""
    if not patch_content.strip():
        return False

    patch_path = "pnkln_autofix.patch"
    with open(patch_path, "w") as f:
        f.write(patch_content)

    print(f"Applying patch: {patch_path}")
    # Try applying
    p = subprocess.run(f"git apply {patch_path}", shell=True)
    return p.returncode == 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tests", default="pytest", help="Test command to run")
    parser.add_argument("--max-iters", type=int, default=5, help="Max repair attempts")
    parser.add_argument("--paths", default="src", help="Comma-separated paths allowed to edit")
    args = parser.parse_args()

    paths = args.paths.split(",")

    print(f"🚀 Pnkln Autofix Agent (Model: {MODEL_ID})")

    for i in range(1, args.max_iters + 1):
        print(f"\n--- Iteration {i}/{args.max_iters} ---")
        success, output = run_tests(args.tests)

        if success:
            print("\n✅ GREEN: All tests passed!")
            return 0

        print("❌ RED: Tests failed. Predicting fix...")
        patch = ask_vertex_for_patch(output, paths)

        if not patch or "diff" not in patch[:20].lower():
            print("⚠️ Model failed to generate valid diff. Skipping.")
            continue

        applied = apply_patch(patch)
        if not applied:
            print("⚠️ Patch application failed.")
        else:
            print("✅ Patch applied.")

    print("\n❌ Failed to fix within max iterations.")
    return 1


if __name__ == "__main__":
    main()
