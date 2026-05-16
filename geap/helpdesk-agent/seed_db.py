#!/usr/bin/env python3
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Seed Firestore with CMDB device data for GEAP Part 2 testing.

Usage:
    uv run python seed_db.py
    # or
    python seed_db.py

Reference: GEAP Tutorial Series Part 2
Project: shadowtag-omega-v4
"""

from google.cloud import firestore

PROJECT_ID = "shadowtag-omega-v4"
db = firestore.Client(project=PROJECT_ID)

DEVICES = {
    "LAPTOP-001": {
        "model": "MacBook Pro M4 Max",
        "status": "Active",
        "warranty": "Valid until 2028-09-15",
        "assigned_to": "Engineering — Jane Smith",
        "department": "Engineering",
        "location": "HQ Floor 4",
        "os": "macOS 16.1",
        "serial": "C02ZX1ABCDEF",
        "category": "laptop",
        "notes": "16-inch, 64GB RAM, 1TB SSD",
    },
    "LAPTOP-002": {
        "model": "ThinkPad X1 Carbon Gen 12",
        "status": "Active",
        "warranty": "Valid until 2028-06-01",
        "assigned_to": "Legal — Mike Johnson",
        "department": "Legal",
        "location": "HQ Floor 2",
        "os": "Windows 11 Enterprise",
        "serial": "PF4XYZGHIJK",
        "category": "laptop",
        "notes": "14-inch, 32GB RAM, 512GB SSD",
    },
    "MONITOR-001": {
        "model": "Dell U2723QE 27-inch 4K",
        "status": "Active",
        "warranty": "Valid until 2028-03-10",
        "assigned_to": "Design — Sarah Lee",
        "department": "Design",
        "location": "HQ Floor 3",
        "serial": "DLLU27MNOPQR",
        "category": "monitor",
        "notes": "USB-C hub, 90W PD, color-calibrated",
    },
    "PRINTER-001": {
        "model": "HP LaserJet Pro MFP M428fdw",
        "status": "Needs Repair",
        "warranty": "Valid until 2027-11-20",
        "assigned_to": "Shared — 3rd Floor",
        "department": "Operations",
        "location": "HQ Floor 3 Print Room",
        "serial": "HPLJ42STUVWX",
        "category": "printer",
        "notes": "Toner replacement scheduled, paper jam cleared 2026-05-10",
    },
    "SERVER-001": {
        "model": "Dell PowerEdge R760",
        "status": "Active",
        "warranty": "Valid until 2030-01-15",
        "assigned_to": "Infrastructure — Ops Team",
        "department": "Infrastructure",
        "location": "Data Center Rack A3",
        "os": "Ubuntu 24.04 LTS",
        "serial": "DLLPE76YZABC",
        "category": "server",
        "notes": "2x Xeon, 512GB RAM, 8x 2TB NVMe RAID-6",
    },
    "PHONE-001": {
        "model": "Cisco IP Phone 8845",
        "status": "Active",
        "warranty": "Valid until 2027-06-01",
        "assigned_to": "Reception — Front Desk",
        "department": "Operations",
        "location": "HQ Floor 1 Lobby",
        "serial": "CISC88DEFGHI",
        "category": "phone",
        "notes": "PoE, 5-line, HD video capable",
    },
}


def main() -> None:
    """Seed the Firestore 'devices' collection."""
    batch = db.batch()

    for device_id, data in DEVICES.items():
        ref = db.collection("devices").document(device_id)
        batch.set(ref, data)
        print(f"  → Seeded {device_id}: {data['model']}")

    batch.commit()
    print(f"\n✅ Successfully seeded {len(DEVICES)} devices into Firestore!")
    print(f"   Project: {PROJECT_ID}")
    print("   Collection: devices")


if __name__ == "__main__":
    main()
