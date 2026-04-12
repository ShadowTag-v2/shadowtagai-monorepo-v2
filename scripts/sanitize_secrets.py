#!/usr/bin/env python3
import json
import os
import subprocess

ROOT = "/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
os.chdir(ROOT)

gitignore_path = ".gitignore"
# Blanket directory exclusions removed per operator override
print("[sanitize] Running gitleaks...")
subprocess.run(
    ["gitleaks", "detect", "--no-git", "-f", "json", "-r", "secrets_report.json"], check=False
)

if os.path.exists("secrets_report.json"):
    with open("secrets_report.json") as f:
        try:
            data = json.load(f)
            files_with_secrets = sorted(
                list(set([item.get("File") for item in data if item.get("File")]))
            )
            if files_with_secrets:
                with open(gitignore_path, "a") as gf:
                    gf.write("\n# Gitleaks Auto-Ignored Secret Files\n")
                    for file in files_with_secrets:
                        # Ensure relative path
                        rel_path = os.path.relpath(file, ROOT) if os.path.isabs(file) else file
                        gf.write(f"{rel_path}\n")
                print(f"[sanitize] Appended {len(files_with_secrets)} secret files to .gitignore")
            else:
                print("[sanitize] No secret files found in report.")
        except Exception as e:
            print(f"[sanitize] Error reading json: {e}")
else:
    print("[sanitize] No secrets_report.json generated.")
