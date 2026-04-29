# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os
import re
import sys


def extract_flags(directory):
    pattern_flag = re.compile(
        r"(?:isOn|getFeatureValue|feature|getFeatureValue_CACHED_MAY_BE_STALE|checkStatsigFeatureGate_CACHED_MAY_BE_STALE|getDynamicConfig_CACHED_MAY_BE_STALE|checkGate_CACHED_OR_BLOCKING|getDynamicConfig_BLOCKS_ON_INIT)\(['\"]([^'\"]+)['\"]"
    )
    flags = set()

    for root, _dirs, files in os.walk(directory):
        for file in files:
            if file.endswith((".ts", ".tsx", ".js", ".jsx")):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, encoding="utf-8") as f:
                        content = f.read()
                        matches = pattern_flag.findall(content)
                        flags.update(matches)
                except Exception:
                    pass

    for flag in sorted(flags):
        print(f"- {flag}")


if __name__ == "__main__":
    extract_flags(sys.argv[1])
