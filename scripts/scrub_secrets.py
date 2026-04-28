# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os
import re


def scrub_file(filepath) -> None:
    if not os.path.exists(filepath):
        return
    with open(filepath) as f:
        content = f.read()

    # Redact common keys
    content = re.sub(r"AIzaSy[A-Za-z0-9_\-]{33}", "[REDACTED_GCP_KEY]", content)
    content = re.sub(r"sk-[A-Za-z0-9]{20,}", "[REDACTED_SK_KEY]", content)
    content = re.sub(r"-----BEGIN.*?PRIVATE KEY-----", "[REDACTED_PRIVATE_KEY_HEADER]", content)

    # Standardize models
    content = re.sub(r"gemini-2\.5-flash-thinking-exp-\d+-\d+", "gemini-3.1-flash-lite-preview", content)
    content = re.sub(r"gemini-2\.5-flash", "gemini-3.1-flash-lite-preview", content)

    with open(filepath, "w") as f:
        f.write(content)


scrub_file("docs/AUDIT_REPORT.md")
scrub_file("docs/AUDIT_REPORT.json")
scrub_file("docs/SESSION_PACKET.md")
scrub_file("docs/RECOVERY_PACKET.md")
