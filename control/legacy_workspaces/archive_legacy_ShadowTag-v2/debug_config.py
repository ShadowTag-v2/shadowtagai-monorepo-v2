# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

print("--- Checking src.aiyou.config ---")
try:
    print("src.aiyou.config loaded successfully")
except Exception as e:
    print(f"Error loading src.aiyou.config: {e}")

print("\n--- Checking app.config ---")
try:
    print("app.config loaded successfully")
except Exception as e:
    print(f"Error loading app.config: {e}")
