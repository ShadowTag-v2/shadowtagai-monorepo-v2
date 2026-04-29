# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os
import re


def scan_for_feature_flags(search_dir):
    # Regex to match getFeatureValue or checkStatsigFeatureGate and their variants
    # Extracts the string literal inside the first argument.
    pattern = re.compile(r"getFeatureValue_CACHED_MAY_BE_STALE\s*\(\s*['\"]([^'\"]+)['\"]")

    flags = set()

    for root, dirs, files in os.walk(search_dir):
        # Filter out test directories
        dirs[:] = [d for d in dirs if not ("test" in d.lower() or d == "__tests__")]

        for file in files:
            if file.endswith((".ts", ".tsx", ".js", ".jsx")) and not file.endswith((".test.ts", ".test.tsx", ".spec.ts", ".spec.tsx")):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, encoding="utf-8") as f:
                        content = f.read()
                        matches = pattern.findall(content)
                        for match in matches:
                            flags.add(match)
                except Exception as e:
                    print(f"Could not read {filepath}: {e}")

    return sorted(list(flags))


if __name__ == "__main__":
    search_dir = "/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/_audit_claude_code/src"
    found_flags = scan_for_feature_flags(search_dir)
    print(f"Found {len(found_flags)} unique feature flags/gates:\n")
    for flag in found_flags:
        print(f" - {flag}")
