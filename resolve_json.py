# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import re

with open("antigravity-mcp-config.json") as f:
    content = f.read()

pattern = re.compile(r"<<<<<<< HEAD.*?=======\n(.*?)\n>>>>>>> fix-invariants-103-105", re.DOTALL)
resolved_content = pattern.sub(r"\1", content)

with open("antigravity-mcp-config.json", "w") as f:
    f.write(resolved_content)

# print("Conflicts resolved in config JSON")
