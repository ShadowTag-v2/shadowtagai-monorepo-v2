#!/usr/bin/env python3
"""Scaffolds the directory structure for the 30 Sovereign Verticals."""

import logging
import os

from revenue_engine import BASE_DIR, RevenueEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Scaffolder")


def scaffold():
    engine = RevenueEngine()
    logger.info(f"🏗️ SCAFFOLDING {len(engine.verticals)} VERTICALS...")

    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)

    for v in engine.verticals:
        safe_name = v["name"].lower().replace(" ", "_")
        dir_name = f"{v['id']}_{safe_name}"
        path = os.path.join(BASE_DIR, dir_name)

        if not os.path.exists(path):
            os.makedirs(path)
            # Create a README for each vertical
            with open(os.path.join(path, "README.md"), "w") as f:
                f.write(f"# Vertical {v['id']}: {v['name']}\n\n")
                f.write(f"**Model**: {v['model']}\n")
                f.write(f"**Target**: {v['target']}\n")
                f.write(f"**Status**: {v['status']}\n")
            logger.info(f"✅ Created {path}")
        else:
            logger.info(f"⏭️ Skipped {path} (Exists)")


if __name__ == "__main__":
    scaffold()
