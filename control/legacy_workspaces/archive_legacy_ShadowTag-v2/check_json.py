# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import re
import json


def check_file(filepath):
    print(f"Checking {filepath}...")
    try:
        with open(filepath) as f:
            content = f.read()

        # Strip single-line comments
        content = re.sub(r"^\s*//.*$", "", content, flags=re.MULTILINE)
        content = re.sub(r"([^\\])//.*$", r"\1", content, flags=re.MULTILINE)
        # Strip block comments
        content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)

        try:
            json.loads(content)
            print("  Valid JSONC!")
        except json.JSONDecodeError as e:
            print(f"  Error: {e}")
            lines = content.split("\n")
            if e.lineno <= len(lines):
                print(f"  Line {e.lineno}: {lines[e.lineno - 1]}")
    except Exception as e:
        print(f"  Could not read file: {e}")


check_file("/Users/pikeymickey/Library/Application Support/Antigravity/User/settings.json")
check_file("/Users/pikeymickey/Library/Application Support/Code/User/settings.json")
check_file("/Users/pikeymickey/.gemini/settings.json")
