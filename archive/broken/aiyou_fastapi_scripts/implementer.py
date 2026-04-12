#!/usr/bin/env python3
"""
Implementer Agent: Generates test plan from PR diff
Uses n-autoresearch/Kosmos/BioAgents (Gemini Flash) for cost efficiency
Stage 1 of Dual-Model CI Pipeline

Cost: ~$0.001/PR
"""

import json
import os
import sys

import requests

n-autoresearch/Kosmos/BioAgents_URL = os.environ.get("n-autoresearch/Kosmos/BioAgents_URL", "http://localhost:8600")

IMPLEMENTER_PROMPT = """
Analyze this code diff and generate a test plan.

For each changed function/class:
1. Identify the core behavior being modified
2. List invariants that must hold
3. Suggest edge cases to test
4. Flag any security-sensitive changes

Output JSON:
{
  "changes": [
    {
      "file": "path/to/file.py",
      "function": "function_name",
      "behavior": "what it does",
      "invariants": ["inv1", "inv2"],
      "edge_cases": ["case1", "case2"],
      "security_flag": true/false
    }
  ],
  "overall_risk": "low|medium|high"
}

IMPORTANT: Output ONLY valid JSON, no other text.

DIFF:
{diff}
"""


def main(diff_file: str):
    with open(diff_file) as f:
        diff = f.read()

    if not diff.strip():
        # Empty diff - return minimal plan
        result = {"changes": [], "overall_risk": "low", "note": "No changes detected"}
        print(json.dumps(result, indent=2))
        return

    try:
        response = requests.post(
            f"{n-autoresearch/Kosmos/BioAgents_URL}/task",
            json={"prompt": IMPLEMENTER_PROMPT.format(diff=diff[:50000])},  # Limit diff size
            timeout=60,
        )
        response.raise_for_status()
        result = response.json()

        # Extract the response content
        if isinstance(result.get("response"), str):
            # Try to parse JSON from response
            try:
                parsed = json.loads(result["response"])
                print(json.dumps(parsed, indent=2))
            except json.JSONDecodeError:
                # If not valid JSON, wrap in structure
                print(
                    json.dumps(
                        {
                            "changes": [],
                            "overall_risk": "medium",
                            "raw_analysis": result["response"][:2000],
                        },
                        indent=2,
                    )
                )
        else:
            print(json.dumps(result.get("response", result), indent=2))

    except requests.RequestException as e:
        # Fallback if n-autoresearch/Kosmos/BioAgents unavailable
        print(
            json.dumps(
                {
                    "changes": [],
                    "overall_risk": "unknown",
                    "error": f"n-autoresearch/Kosmos/BioAgents unavailable: {str(e)}",
                    "fallback": True,
                },
                indent=2,
            ),
            file=sys.stderr,
        )
        # Still output valid JSON to stdout
        print(
            json.dumps(
                {
                    "changes": [],
                    "overall_risk": "medium",
                    "note": "Implementer analysis skipped - n-autoresearch/Kosmos/BioAgents unavailable",
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: implementer.py <diff_file>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
