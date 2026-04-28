# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os
import sys

# Ensure root path is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.atomic_core import initiate_research_omega, monitor_and_capture_omega


def recover_reams():
    print("📜 INITIATING REAM RECOVERY (DRIVE INGESTION)...")

    query = """
    ACCESS GOOGLE DRIVE.

    1. LIST every single file you can find related to 'ShadowTag', 'Omega', 'A2UI', 'Sovereign', or 'n-autoresearch/Kosmos/BioAgents'.
    2. For each file, EXTRACT the key technical constraints or architectural decisions it mandates.
    3. COMPARE this intelligence against the known system state (Atomic Core, Judge 6, Cloud Run).
    4. REPORT the 'Delta': What did we learn from these specific files that changed our code?

    Output a structured manifest of files and their impact.
    """

    try:
        # Dispatch
        interaction_id = initiate_research_omega(query)
        print(f"✅ Recovery Agent Dispatched. Interaction ID: {interaction_id}")

        # Monitor Loop (for the user to see progress in terminal)
        print("🔍 Scanning Drive... (Press Ctrl+C to detach)")
        monitor_and_capture_omega(interaction_id)

    except Exception as e:
        print(f"❌ Recovery Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    recover_reams()
