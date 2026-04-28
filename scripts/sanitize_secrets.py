#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import json
import os
import subprocess

ROOT = "/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
os.chdir(ROOT)

gitignore_path = ".gitignore"
# Blanket directory exclusions removed per operator override
subprocess.run(["gitleaks", "detect", "--no-git", "-f", "json", "-r", "secrets_report.json"], check=False)

if os.path.exists("secrets_report.json"):
    with open("secrets_report.json") as f:
        try:
            data = json.load(f)
            files_with_secrets = sorted({item.get("File") for item in data if item.get("File")})
            if files_with_secrets:
                with open(gitignore_path, "a") as gf:
                    gf.write("\n# Gitleaks Auto-Ignored Secret Files\n")
                    for file in files_with_secrets:
                        # Ensure relative path
                        rel_path = os.path.relpath(file, ROOT) if os.path.isabs(file) else file
                        gf.write(f"{rel_path}\n")
            else:
                pass
        except Exception:
            pass
else:
    pass
