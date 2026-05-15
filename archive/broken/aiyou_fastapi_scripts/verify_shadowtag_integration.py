#!/usr/bin/env python3
"""
Verify integration of ShadowTag v2 tools into Flying n-autoresearch/Kosmos/BioAgents.
"""

import os
import sys

# Create dummy CodePMCS module if missing to avoid import error during test
try:
    import codepmcs
except ImportError:
    # Quick mock
    from types import ModuleType

    m = ModuleType("codepmcs")

    class MockCodePMCS:
        def scan_code(self):
            return "scan"

    m.CodePMCS = MockCodePMCS
    sys.modules["codepmcs"] = m

# Add parent dir to path
sys.path.append(os.getcwd())

from agents.autoresearch import n-autoresearch/Kosmos/BioAgents


def verify():
    print("Initializing n-autoresearch/Kosmos/BioAgents...")
    # Initialize without project_id to skip Vertex/GenAI strict checks, just testing tool registry
    fm = n-autoresearch/Kosmos/BioAgents(project_id="test-project")

    print("\nChecking Registered Tools:")
    required_tools = ["maps_query", "bq_query", "gke_ops", "mcarlo_val", "odor_sim", "swiper_plan"]

    missing = []
    for t in required_tools:
        if t in fm.registry._tools:
            print(f"✅ {t}")
        else:
            print(f"❌ {t}")
            missing.append(t)

    if missing:
        print(f"\nFAILED: Missing tools: {missing}")
        sys.exit(1)

    print("\nSUCCESS: All ShadowTag tools registered.")


if __name__ == "__main__":
    verify()
