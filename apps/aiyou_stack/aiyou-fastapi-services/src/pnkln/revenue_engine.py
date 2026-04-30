#!/usr/bin/env python3
"""Antigravity Revenue Engine
Manages the lifecycle of the 30 Sovereign Verticals.
"""

import argparse
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

VERTICALS_FILE = "src/pnkln/Docs/pnkln_VerticalsStrategy.md"
BASE_DIR = "src/pnkln/verticals"


class RevenueEngine:
    def __init__(self):
        self.verticals = self._load_verticals()

    def _load_verticals(self) -> list[dict]:
        """Parses the Markdown strategy doc to load verticals."""
        verticals = []
        try:
            with open(VERTICALS_FILE) as f:
                lines = f.readlines()
                in_table = False
                for line in lines:
                    if "| ID | VERTICAL |" in line:
                        in_table = True
                        continue
                    if in_table and line.strip().startswith("|") and "---" not in line:
                        parts = [p.strip() for p in line.split("|") if p.strip()]
                        if len(parts) >= 5:
                            verticals.append(
                                {
                                    "id": parts[0],
                                    "name": parts[1].replace("**", ""),
                                    "model": parts[2],
                                    "target": parts[3],
                                    "status": parts[4],
                                },
                            )
        except FileNotFoundError:
            logger.warning(f"Verticals strategy file not found at {VERTICALS_FILE}")
            # Fallback list for bootstrapping
            return [{"id": "00", "name": "Bootstrap", "status": "ACTIVE"}]
        return verticals

    def ignite(self, vertical_id: str):
        """Activates a specific vertical."""
        target = next((v for v in self.verticals if v["id"] == vertical_id), None)
        if target:
            logger.info(f"🔥 IGNITING VERTICAL {vertical_id}: {target['name']}")
            # Logic to spin up agents or resources would go here
            return True
        logger.error(f"Vertical {vertical_id} not found.")
        return False

    def status(self):
        """Reports status of all verticals."""
        print(f"{'ID':<5} {'NAME':<30} {'STATUS':<10}")
        print("-" * 50)
        for v in self.verticals:
            print(f"{v['id']:<5} {v['name']:<30} {v['status']:<10}")

    def audit(self):
        """Checks if vertical directories exist."""
        print("🔍 AUDITING VERTICALS INFRASTRUCTURE...")
        for v in self.verticals:
            safe_name = v["name"].lower().replace(" ", "_")
            path = os.path.join(BASE_DIR, f"{v['id']}_{safe_name}")
            exists = os.path.exists(path)
            icon = "✅" if exists else "❌"
            print(f"{icon} {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Antigravity Revenue Engine")
    parser.add_argument("action", choices=["status", "audit", "ignite"], help="Action to perform")
    parser.add_argument("--id", help="Vertical ID for ignite action")

    args = parser.parse_args()

    engine = RevenueEngine()

    if args.action == "status":
        engine.status()
    elif args.action == "audit":
        engine.audit()
    elif args.action == "ignite":
        if args.id:
            engine.ignite(args.id)
        else:
            print("Error: --id required for ignite")
