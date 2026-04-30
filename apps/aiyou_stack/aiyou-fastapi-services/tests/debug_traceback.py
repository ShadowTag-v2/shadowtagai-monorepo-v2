import os
import sys
import traceback

sys.path.append(os.path.join(os.getcwd(), "src"))

print("Starting debug trace...")
try:
    print("Success importing gemini_integration")
except Exception:
    traceback.print_exc()

try:
    print("Success importing intelligence_api")
except Exception:
    traceback.print_exc()
