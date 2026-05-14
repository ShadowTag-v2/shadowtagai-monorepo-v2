#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import os
import sys
import argparse
import json

# Bind the ANE bridge path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../apps/aiyou_stack/aiyou-fastapi-services")))

try:
    from zero_cpu_router import dispatch_compute
except ImportError:
    dispatch_compute = None


def antigravity_local_infer(prompt: str, model: str = "pnkln-logic-8b", require_json: bool = False):
    """
    Antigravity Native Protocol: Executing reasoning locally
    on the user's Apple Silicon (ANE) to avoid cloud round-trips for sensitive data.
    """
    if not dispatch_compute:
        print(json.dumps({"error": "zero_cpu_router is missing. ANE offline."}))
        sys.exit(1)

    try:
        # Antigravity explicitly invoking Pickle Rick (ANE) autonomously
        result = dispatch_compute(prompt, model=model)

        if require_json:
            print(json.dumps({"status": "success", "backend": "ANE", "output": result}))
        else:
            print(f"[ANTIGRAVITY ANE EXECUTION]\n{result}")

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Antigravity Autonomous Local ANE Interface")
    parser.add_argument("--prompt", type=str, required=True, help="The prompt to evaluate locally.")
    parser.add_argument("--model", type=str, default="pnkln-logic-8b", help="Target local model.")
    parser.add_argument("--json", action="store_true", help="Output strict JSON for MCP parsing.")

    args = parser.parse_args()
    antigravity_local_infer(args.prompt, args.model, args.json)
