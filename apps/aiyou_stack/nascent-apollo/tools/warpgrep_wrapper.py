# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os
import subprocess
import sys


class WarpGrepWrapper:
    """WarpGrep: AI-Powered Code Search.

    If MORPH_API_KEY is present, uses Morph SDK (mocked command for now).
    Otherwise, falls back to standard ripgrep (rg) with a warning.
    """

    def __init__(self):
        self.api_key = os.getenv("MORPH_API_KEY")

    def search(self, query: str, path: str = "."):
        if self.api_key:
            print(f"🚀 WARPGREP: AI Search initiated for '{query}'...")
            # In a real implementation, we would import MorphClient here.
            # Since we don't have the package installed in this env, we simulate or warn.
            print(
                "⚠️ Morph SDK not installed in this environment. Please run: npm install @morphllm/morphsdk",
            )
            return self._fallback_search(query, path)
        print("🐌 WARPGREP: No MORPH_API_KEY found. Falling back to standard grep.")
        return self._fallback_search(query, path)

    def _fallback_search(self, query: str, path: str):
        # Fallback to ripgrep (rg) or grep
        try:
            # Try ripgrep first
            cmd = ["rg", "-n", query, path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout
            if result.returncode == 1:
                return "No matches found."
            # If rg fails (e.g. not installed), try grep
            cmd = ["grep", "-r", "-n", query, path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            return f"Error during fallback search: {e}"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 tools/warpgrep_wrapper.py <query>")
        sys.exit(1)

    wrapper = WarpGrepWrapper()
    print(wrapper.search(sys.argv[1]))
