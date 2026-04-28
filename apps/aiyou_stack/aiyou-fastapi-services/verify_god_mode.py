# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.getcwd())

try:
    from libs.agents.gemini_code_assist_proxy import gemini_proxy

    print("✅ Proxy Imported Successfully")
except ImportError as e:
    print(f"❌ Proxy Import Failed: {e}")
    sys.exit(1)

# Test File
TEST_FILE = "god_mode_test.py"

# Trigger Smart Action
print(f"⚡️ Triggering God Mode on {TEST_FILE}...")
result = gemini_proxy.trigger_smart_action(
    action_type="TEST_REFACTOR",
    file_path=TEST_FILE,
    context="Test Context",
)

print(f"📄 Result: {result}")

# Verify File Creation
if result.get("status") == "APPLIED_AUTOMATICALLY":
    if os.path.exists(TEST_FILE):
        print("✅ God Mode Validated: File created automatically.")
        with open(TEST_FILE) as f:
            print(f"   Content: {f.read().strip()}")
        # Cleanup
        os.remove(TEST_FILE)
    else:
        print("❌ God Mode Failed: File not found.")
else:
    print("⚠️ God Mode Bypassed (Preview Mode). Check Judge Logic.")
