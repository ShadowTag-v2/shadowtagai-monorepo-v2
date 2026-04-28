# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os
import sys

sys.path.append(os.path.join(os.getcwd(), "src"))

print("Importing gemini_integration...")
try:
    print("Success importing gemini_integration")
except Exception as e:
    print(f"Failed importing gemini_integration: {e}")

print("Importing intelligence_api...")
try:
    print("Success importing intelligence_api")
except Exception as e:
    print(f"Failed importing intelligence_api: {e}")
