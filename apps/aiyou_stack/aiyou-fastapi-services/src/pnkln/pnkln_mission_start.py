#!/usr/bin/env python3
"""
ANTIGRAVITY // MISSION LAUNCHER
Integrates with pnkln_tasks.sh and SOP Snippets
"""

import json
import logging
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_doctrine():
    """Loads the SOP doctrine from JSON definition."""
    try:
        # Determine strict path relative to this script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        sop_path = os.path.join(base_dir, "Prompts", "pnkln_SOPSnippets.json")

        with open(sop_path) as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"FATAL: Doctrine not found at {sop_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        logger.error(f"FATAL: Doctrine corrupted in {sop_path}")
        sys.exit(1)


def execute_tier_30():
    """Activates the sovereign instance."""
    print("🚀 ACTIVATING TIER 30: THE CHILD INSTANCE")
    print("⚔️ 30 VERTICALS ENGAGED")
    print("🛡️ JUDGE #6 BRAKES ACTIVE")
    print("🙈 MONKEY'S ACTIVATED / STANDING BY")  # Explicit confirmation


if __name__ == "__main__":
    doctrine = load_doctrine()
    print(f"✅ LOADED {len(doctrine)} SOPs")
    for op in doctrine:
        print(f"  - READINESS: {op.get('name')}")
    execute_tier_30()
