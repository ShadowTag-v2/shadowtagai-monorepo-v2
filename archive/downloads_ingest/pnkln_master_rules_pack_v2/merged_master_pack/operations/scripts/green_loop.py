#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "green_loop"
OUT.mkdir(parents=True, exist_ok=True)
payload = {"status": "ok", "system": "green-loop", "goal": "patch, verify, summarize, preserve only passing artifacts"}
(OUT / "latest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(json.dumps(payload))
