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

"""CMDB Asset Management Service — GEAP Part 2.

Provides a Firestore-backed Configuration Management Database (CMDB)
for IT asset tracking, inventory management, and lifecycle operations.
Falls back to in-memory store when Firestore is unavailable.

Reference: GEAP Tutorial Series Part 2
Project: shadowtag-omega-v4
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum

log = logging.getLogger(__name__)


class AssetStatus(str, Enum):
    """Valid asset lifecycle states."""

    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    DECOMMISSIONED = "decommissioned"
    LOST = "lost"
    IN_TRANSIT = "in_transit"


class AssetCategory(str, Enum):
    """Hardware asset categories."""

    LAPTOP = "laptop"
    DESKTOP = "desktop"
    MONITOR = "monitor"
    PRINTER = "printer"
    PHONE = "phone"
    TABLET = "tablet"
    SERVER = "server"
    NETWORK = "network"
    PERIPHERAL = "peripheral"
    OTHER = "other"


# --- In-Memory CMDB (Firestore fallback) ---

_SEED_ASSETS: dict[str, dict] = {
    "LAPTOP-001": {
        "asset_id": "LAPTOP-001",
        "name": "MacBook Pro M4 Max",
        "category": "laptop",
        "status": "active",
        "assigned_to": "Engineering — Jane Smith",
        "department": "Engineering",
        "location": "HQ Floor 4",
        "os": "macOS 16.1",
        "serial": "C02ZX1ABCDEF",
        "purchase_date": "2025-09-15",
        "warranty_expires": "2028-09-15",
        "notes": "16-inch, 64GB RAM, 1TB SSD",
    },
    "LAPTOP-002": {
        "asset_id": "LAPTOP-002",
        "name": "ThinkPad X1 Carbon Gen 12",
        "category": "laptop",
        "status": "active",
        "assigned_to": "Legal — Mike Johnson",
        "department": "Legal",
        "location": "HQ Floor 2",
        "os": "Windows 11 Enterprise",
        "serial": "PF4XYZGHIJK",
        "purchase_date": "2025-06-01",
        "warranty_expires": "2028-06-01",
        "notes": "14-inch, 32GB RAM, 512GB SSD",
    },
    "MONITOR-001": {
        "asset_id": "MONITOR-001",
        "name": "Dell U2723QE 27-inch 4K",
        "category": "monitor",
        "status": "active",
        "assigned_to": "Design — Sarah Lee",
        "department": "Design",
        "location": "HQ Floor 3",
        "serial": "DLLU27MNOPQR",
        "purchase_date": "2025-03-10",
        "warranty_expires": "2028-03-10",
        "notes": "USB-C hub, 90W PD, color-calibrated",
    },
    "PRINTER-001": {
        "asset_id": "PRINTER-001",
        "name": "HP LaserJet Pro MFP M428fdw",
        "category": "printer",
        "status": "maintenance",
        "assigned_to": "Shared — 3rd Floor",
        "department": "Operations",
        "location": "HQ Floor 3 Print Room",
        "serial": "HPLJ42STUVWX",
        "purchase_date": "2024-11-20",
        "warranty_expires": "2027-11-20",
        "notes": "Toner replacement scheduled, paper jam cleared 2026-05-10",
    },
    "SERVER-001": {
        "asset_id": "SERVER-001",
        "name": "Dell PowerEdge R760",
        "category": "server",
        "status": "active",
        "assigned_to": "Infrastructure — Ops Team",
        "department": "Infrastructure",
        "location": "Data Center Rack A3",
        "os": "Ubuntu 24.04 LTS",
        "serial": "DLLPE76YZABC",
        "purchase_date": "2025-01-15",
        "warranty_expires": "2030-01-15",
        "notes": "2x Xeon, 512GB RAM, 8x 2TB NVMe RAID-6",
    },
    "PHONE-001": {
        "asset_id": "PHONE-001",
        "name": "Cisco IP Phone 8845",
        "category": "phone",
        "status": "active",
        "assigned_to": "Reception — Front Desk",
        "department": "Operations",
        "location": "HQ Floor 1 Lobby",
        "serial": "CISC88DEFGHI",
        "purchase_date": "2024-06-01",
        "warranty_expires": "2027-06-01",
        "notes": "PoE, 5-line, HD video capable",
    },
}

# Mutable runtime store
_assets: dict[str, dict] = dict(_SEED_ASSETS)


def _firestore_client():
    """Attempt to get a Firestore client. Returns None if unavailable."""
    try:
        from google.cloud import firestore

        return firestore.Client(project="shadowtag-omega-v4")
    except Exception:
        log.debug("Firestore unavailable, using in-memory CMDB")
        return None


# --- CMDB Tool Functions (ADK-compatible) ---


def cmdb_lookup_asset(asset_id: str) -> str:
    """Look up a specific IT asset by its ID in the CMDB.

    Args:
        asset_id: The asset tag (e.g., 'LAPTOP-001') or serial number.

    Returns:
        Detailed asset information including status, assignment, and warranty.
    """
    key = asset_id.upper().strip()

    # Try direct ID match first
    asset = _assets.get(key)

    # Fallback: search by serial number
    if not asset:
        for a in _assets.values():
            if a.get("serial", "").upper() == key:
                asset = a
                break

    if not asset:
        return (
            f"❌ Asset '{asset_id}' not found in CMDB.\n"
            "Please verify the asset tag or serial number.\n"
            "Tip: Use cmdb_search_assets to search by department or category."
        )

    lines = [
        f"📋 Asset Details — {asset['asset_id']}",
        f"  Name: {asset['name']}",
        f"  Category: {asset['category'].title()}",
        f"  Status: {asset['status'].upper()}",
        f"  Assigned To: {asset.get('assigned_to', 'Unassigned')}",
        f"  Department: {asset.get('department', 'N/A')}",
        f"  Location: {asset.get('location', 'N/A')}",
    ]
    if asset.get("os"):
        lines.append(f"  OS: {asset['os']}")
    lines.extend(
        [
            f"  Serial: {asset.get('serial', 'N/A')}",
            f"  Purchased: {asset.get('purchase_date', 'N/A')}",
            f"  Warranty Expires: {asset.get('warranty_expires', 'N/A')}",
        ]
    )
    if asset.get("notes"):
        lines.append(f"  Notes: {asset['notes']}")

    return "\n".join(lines)


def cmdb_search_assets(
    department: str = "",
    category: str = "",
    status: str = "",
) -> str:
    """Search the CMDB for assets matching given criteria.

    Args:
        department: Filter by department (e.g., 'Engineering', 'Legal').
        category: Filter by asset category (e.g., 'laptop', 'server').
        status: Filter by status (e.g., 'active', 'maintenance').

    Returns:
        A list of matching assets or a message if none found.
    """
    results = list(_assets.values())

    if department:
        dept_lower = department.lower()
        results = [a for a in results if dept_lower in a.get("department", "").lower()]

    if category:
        cat_lower = category.lower()
        results = [a for a in results if cat_lower == a.get("category", "").lower()]

    if status:
        stat_lower = status.lower()
        results = [a for a in results if stat_lower == a.get("status", "").lower()]

    if not results:
        filters = []
        if department:
            filters.append(f"department='{department}'")
        if category:
            filters.append(f"category='{category}'")
        if status:
            filters.append(f"status='{status}'")
        return f"No assets found matching: {', '.join(filters) or 'all'}."

    lines = [f"🔍 Found {len(results)} asset(s):"]
    for a in results:
        lines.append(
            f"  • {a['asset_id']} — {a['name']} | "
            f"{a['status'].upper()} | {a.get('assigned_to', 'Unassigned')}"
        )

    return "\n".join(lines)


def cmdb_update_asset_status(
    asset_id: str,
    new_status: str,
    notes: str = "",
) -> str:
    """Update the status of an IT asset in the CMDB.

    Args:
        asset_id: The asset tag to update (e.g., 'LAPTOP-001').
        new_status: New status — active, maintenance, decommissioned, lost.
        notes: Optional notes about the status change.

    Returns:
        Confirmation of the status update or an error message.
    """
    key = asset_id.upper().strip()
    asset = _assets.get(key)

    if not asset:
        return f"❌ Asset '{asset_id}' not found. Cannot update status."

    # Validate status
    valid_statuses = {s.value for s in AssetStatus}
    if new_status.lower() not in valid_statuses:
        return (
            f"❌ Invalid status '{new_status}'. "
            f"Valid options: {', '.join(sorted(valid_statuses))}"
        )

    old_status = asset["status"]
    asset["status"] = new_status.lower()

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    update_note = f"[{timestamp}] Status: {old_status} → {new_status.lower()}"
    if notes:
        update_note += f" — {notes}"

    existing_notes = asset.get("notes", "")
    asset["notes"] = (
        f"{existing_notes}\n{update_note}" if existing_notes else update_note
    )

    return (
        f"✅ Asset {key} status updated: {old_status.upper()} → {new_status.upper()}\n"
        f"Timestamp: {timestamp}\n"
        f"{'Notes: ' + notes if notes else ''}"
    )


def cmdb_register_asset(
    name: str,
    category: str,
    assigned_to: str = "",
    department: str = "",
    location: str = "",
    serial: str = "",
    notes: str = "",
) -> str:
    """Register a new IT asset in the CMDB.

    Args:
        name: Display name of the asset (e.g., 'MacBook Pro M4').
        category: Asset category — laptop, desktop, monitor, printer, etc.
        assigned_to: Person or team the asset is assigned to.
        department: Department that owns the asset.
        location: Physical location of the asset.
        serial: Manufacturer serial number.
        notes: Additional notes.

    Returns:
        Confirmation with the assigned asset ID.
    """
    # Validate category
    valid_categories = {c.value for c in AssetCategory}
    cat_lower = category.lower()
    if cat_lower not in valid_categories:
        return (
            f"❌ Invalid category '{category}'. "
            f"Valid options: {', '.join(sorted(valid_categories))}"
        )

    # Generate asset ID
    prefix = cat_lower.upper()[:6]
    suffix = str(len([a for a in _assets if a.startswith(prefix)]) + 1).zfill(3)
    asset_id = f"{prefix}-{suffix}"

    # Avoid collisions
    while asset_id in _assets:
        suffix = str(int(suffix) + 1).zfill(3)
        asset_id = f"{prefix}-{suffix}"

    asset = {
        "asset_id": asset_id,
        "name": name,
        "category": cat_lower,
        "status": AssetStatus.ACTIVE.value,
        "assigned_to": assigned_to or "Unassigned",
        "department": department or "Unassigned",
        "location": location or "TBD",
        "serial": serial or f"AUTO-{uuid.uuid4().hex[:8].upper()}",
        "purchase_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "warranty_expires": "TBD",
        "notes": notes,
    }

    _assets[asset_id] = asset

    return (
        f"✅ New asset registered successfully!\n"
        f"  Asset ID: {asset_id}\n"
        f"  Name: {name}\n"
        f"  Category: {category}\n"
        f"  Status: ACTIVE\n"
        f"  Assigned To: {asset.get('assigned_to')}\n"
        f"  Serial: {asset['serial']}"
    )


def cmdb_inventory_summary() -> str:
    """Get a high-level summary of all IT assets in the CMDB.

    Returns:
        A formatted summary showing counts by category and status.
    """
    if not _assets:
        return "📊 CMDB is empty. No assets registered."

    # Count by category
    by_category: dict[str, int] = {}
    by_status: dict[str, int] = {}
    for a in _assets.values():
        cat = a.get("category", "other")
        by_category[cat] = by_category.get(cat, 0) + 1
        stat = a.get("status", "unknown")
        by_status[stat] = by_status.get(stat, 0) + 1

    lines = [
        f"📊 CMDB Inventory Summary — {len(_assets)} total assets",
        "",
        "By Category:",
    ]
    for cat, count in sorted(by_category.items(), key=lambda x: -x[1]):
        lines.append(f"  • {cat.title()}: {count}")

    lines.append("\nBy Status:")
    for stat, count in sorted(by_status.items(), key=lambda x: -x[1]):
        lines.append(f"  • {stat.upper()}: {count}")

    return "\n".join(lines)
