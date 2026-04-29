# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import re

with open("scripts/ai-validate.sh") as f:
    content = f.read()

# Replace block by keeping incoming branch content
pattern = re.compile(r"<{7} HEAD.*?={7}\n(.*?)\n>{7} fix-invariants-103-105", re.DOTALL)
resolved_content = pattern.sub(r"\1", content)

with open("scripts/ai-validate.sh", "w") as f:
    f.write(resolved_content)

# print("Conflicts resolved in ai-validate.sh")
