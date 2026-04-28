# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""ArchLint: The Ironwood Architecture Enforcer.
Part of the Cor.56 CI Protocol.
Enforces "Pure Gemini/JAX" and bans "Legacy/PyTorch" patterns.
"""

import argparse
import os
import sys

# DEFINING THE "OLD LEAVEN" (Forbidden Patterns)
FORBIDDEN_PATTERNS = {
    "import torch": "Legacy PyTorch dependency detected. Use JAX/Flax (Ironwood).",
    "class GPT": "Legacy nomenclature 'GPT' detected. Use 'Gemini' or 'Transformer'.",
    "SlowBuffer": "Deprecated Node.js buffer detected. Causes v25 crashes.",
    "MagicMock": "Lazy testing detected. Use real verified fakes or integration tests.",
    "openai": "OpenAI dependency detected. We are a Google/Gemini shop.",
    "anthropic": "Anthropic dependency detected. We are a Google/Gemini shop.",
    "langchain": "LangChain dependency detected. Use native JURA protocol.",
    "pinecone": "Pinecone dependency detected. Use Neural Memory (Titans).",
}

# EXCEPTIONS (Files allowed to break rules, e.g., for comparison or legacy adapters)
EXCLUSIONS = [
    "archlint.py",  # Self
    "tinytorch_sandbox.py",  # Educational/Comparison
    "requirements.txt",
    "pyproject.toml",
]


class ArchLint:
    def __init__(self, root_dir: str = "."):
        self.root_dir = root_dir
        self.violations: list[tuple[str, int, str, str]] = []

    def scan_file(self, filepath: str):
        # Check against exclusions list
        if any(ex in filepath for ex in EXCLUSIONS):
            return

        try:
            with open(filepath, encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    for pattern, message in FORBIDDEN_PATTERNS.items():
                        if pattern in line:
                            # EXCEPTIONS LOGIC
                            if pattern == "import torch":  # noqa: SIM102
                                # Allow torch in tinytorch/steel components only (the 'containment zone')
                                if "tinytorch" in filepath or "/steel/" in filepath:
                                    continue

                            self.violations.append((filepath, i + 1, pattern, message))
        except Exception as e:
            print(f"⚠️  Could not scan {filepath}: {e}")

    def run(self):
        print(f"🛡️  ArchLint: Scanning {self.root_dir}...")

        for root, dirs, files in os.walk(self.root_dir):
            # Prune directories in-place to avoid walking them
            dirs[:] = [
                d
                for d in dirs
                if d
                not in {
                    ".git",
                    "node_modules",
                    "venv",
                    "__pycache__",
                    "dist",
                    "build",
                    "antigravity-flattened",
                    "docs",
                }
            ]

            for file in files:
                if file.endswith(".py") or file.endswith(".js") or file.endswith(".ts"):
                    self.scan_file(os.path.join(root, file))

        return self.report()

    def report(self) -> int:
        if not self.violations:
            print("✅ Cor.56 Compliance: PURE. No legacy patterns found.")
            return 0

        print(f"❌ Cor.56 Violation: Found {len(self.violations)} impure patterns.")
        print("-" * 60)
        print(f"{'FILE':<40} | {'LINE':<5} | {'PATTERN':<15} | {'ISSUE'}")
        print("-" * 60)

        for v in self.violations:
            path, line, pattern, msg = v
            # Shorten path for display
            short_path = path if len(path) < 40 else "..." + path[-37:]
            print(f"{short_path:<40} | {line:<5} | {pattern:<15} | {msg}")

        print("-" * 60)
        print("ACTION REQUIRED: Purge these patterns to maintain Ironwood purity.")
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cor.56 ArchLint Enforcer")
    parser.add_argument("--path", type=str, default=".", help="Root path to scan")
    args = parser.parse_args()

    linter = ArchLint(args.path)
    sys.exit(linter.run())
