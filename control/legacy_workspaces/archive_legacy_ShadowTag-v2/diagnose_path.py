# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import os
import sys

print(f"DEBUG: sys.path BEFORE insertions:\n{sys.path}")

# Emulate run_jetski.py behavior if possible, or just check current state
try:
    import browser_use

    print(f"✅ browser_use imported from: {browser_use.__file__}")
    print(f"❓ browser_use path: {browser_use.__path__}")
except ImportError as e:
    print(f"❌ browser_use import failed: {e}")

try:
    from browser_use.browser.browser import Browser

    print("✅ browser_use.browser.browser imported successfully")
except ImportError as e:
    print(f"❌ browser_use.browser.browser import failed: {e}")

# Check for shadowing directories
shadows = [
    "src/browser-use",
    "libs/external/browser-use",
    "apps/kosmos/src/browser-use",
]
print("DEBUG: Checking for potential shadowing directories:")
for s in shadows:
    path = os.path.abspath(s)
    if os.path.exists(path):
        print(f"⚠️  Found: {path}")
    else:
        print(f"    Clean: {path} not found")
