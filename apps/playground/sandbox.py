# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os
import sys

# Link to Sovereign Core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

try:
    from src.governance.judge import JudgeSix

    print("✅ LINK ESTABLISHED: Sovereign Core is accessible.")

    # TEST ZONE
    print(">>> 🧪 TESTING JUDGE 6 LOGIC...")
    judge = JudgeSix()
    test_code = "print('Hello World')"
    verdict = judge.vet(test_code)
    print(f"    Verdict on safe code: {verdict}")

    test_risk = "os.system('rm -rf /')"
    verdict_risk = judge.vet(test_risk)
    print(f"    Verdict on risky code: {verdict_risk}")
except ImportError as e:
    print(f"❌ LINK FAILED: {e}")
    sys.exit(1)
