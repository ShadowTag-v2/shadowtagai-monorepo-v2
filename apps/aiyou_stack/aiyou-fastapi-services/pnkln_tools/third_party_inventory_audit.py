# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import json
import pathlib
import re
import sys

URL = re.compile(r"https?://([^/]+)/")
ALLOW = {"self", "data:"}
ALLOW_DOMAINS = {"api.pnkln.example", "cdn.pnkln.example"}
found = set()
root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
for p in root.rglob("*"):
    if p.is_file() and p.suffix.lower() in {".html", ".js", ".css"}:
        try:
            s = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for m in URL.finditer(s):
            found.add(m.group(1))
unknown = sorted(set(found) - ALLOW_DOMAINS)
print(json.dumps({"found": sorted(found), "unknown": unknown}, indent=2))
sys.exit(1 if unknown else 0)
