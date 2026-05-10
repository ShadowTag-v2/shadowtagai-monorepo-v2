import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

print("--- Checking src.shadowtag-omega-v4.config ---")
try:
  print("src.shadowtag-omega-v4.config loaded successfully")
except Exception as e:
  print(f"Error loading src.shadowtag-omega-v4.config: {e}")

print("\n--- Checking app.config ---")
try:
  print("app.config loaded successfully")
except Exception as e:
  print(f"Error loading app.config: {e}")
