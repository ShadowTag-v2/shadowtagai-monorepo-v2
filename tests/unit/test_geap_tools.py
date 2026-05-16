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

"""Unit tests for GEAP IT Helpdesk tools — CMDB and Knowledge Search.

Tests the Part 2 tool functions independently of the ADK agent runtime.
"""

import importlib.util
from pathlib import Path

import pytest

# Load CMDB module directly (bypass app/__init__.py which requires google.adk)
_geap_app = Path(__file__).resolve().parents[2] / "geap" / "helpdesk-agent" / "app"

_cmdb_spec = importlib.util.spec_from_file_location("cmdb", _geap_app / "cmdb.py")
_cmdb_mod = importlib.util.module_from_spec(_cmdb_spec)
_cmdb_spec.loader.exec_module(_cmdb_mod)

_ks_spec = importlib.util.spec_from_file_location(
  "knowledge_search", _geap_app / "knowledge_search.py"
)
_ks_mod = importlib.util.module_from_spec(_ks_spec)
_ks_spec.loader.exec_module(_ks_mod)


# --- CMDB Imports ---

_assets = _cmdb_mod._assets
_SEED_ASSETS = _cmdb_mod._SEED_ASSETS
cmdb_inventory_summary = _cmdb_mod.cmdb_inventory_summary
cmdb_lookup_asset = _cmdb_mod.cmdb_lookup_asset
cmdb_register_asset = _cmdb_mod.cmdb_register_asset
cmdb_search_assets = _cmdb_mod.cmdb_search_assets
cmdb_update_asset_status = _cmdb_mod.cmdb_update_asset_status


@pytest.fixture(autouse=True)
def reset_cmdb():
  """Reset the in-memory CMDB to seed state before each test."""
  _assets.clear()
  _assets.update({k: dict(v) for k, v in _SEED_ASSETS.items()})
  yield


class TestCMDBLookup:
  """Tests for cmdb_lookup_asset."""

  def test_lookup_existing_asset(self):
    result = cmdb_lookup_asset("LAPTOP-001")
    assert "MacBook Pro M4 Max" in result
    assert "ACTIVE" in result
    assert "Engineering" in result

  def test_lookup_case_insensitive(self):
    result = cmdb_lookup_asset("laptop-001")
    assert "MacBook Pro M4 Max" in result

  def test_lookup_by_serial(self):
    result = cmdb_lookup_asset("C02ZX1ABCDEF")
    assert "LAPTOP-001" in result

  def test_lookup_not_found(self):
    result = cmdb_lookup_asset("NONEXIST-999")
    assert "not found" in result.lower()

  def test_lookup_includes_warranty(self):
    result = cmdb_lookup_asset("LAPTOP-001")
    assert "Warranty" in result
    assert "2028-09-15" in result

  def test_lookup_shows_os_for_laptops(self):
    result = cmdb_lookup_asset("LAPTOP-002")
    assert "Windows 11" in result


class TestCMDBSearch:
  """Tests for cmdb_search_assets."""

  def test_search_by_department(self):
    result = cmdb_search_assets(department="Engineering")
    assert "LAPTOP-001" in result

  def test_search_by_category(self):
    result = cmdb_search_assets(category="server")
    assert "SERVER-001" in result
    assert "PowerEdge" in result

  def test_search_by_status(self):
    result = cmdb_search_assets(status="maintenance")
    assert "PRINTER-001" in result

  def test_search_no_results(self):
    result = cmdb_search_assets(department="Marketing")
    assert "No assets found" in result

  def test_search_combined_filters(self):
    result = cmdb_search_assets(department="Engineering", category="laptop")
    assert "LAPTOP-001" in result
    # Legal laptop should NOT appear
    assert "LAPTOP-002" not in result

  def test_search_all_active(self):
    result = cmdb_search_assets(status="active")
    assert "LAPTOP-001" in result
    assert "SERVER-001" in result
    # Printer is in maintenance, should NOT appear
    assert "PRINTER-001" not in result


class TestCMDBUpdateStatus:
  """Tests for cmdb_update_asset_status."""

  def test_update_to_maintenance(self):
    result = cmdb_update_asset_status("LAPTOP-001", "maintenance", "Screen repair")
    assert "ACTIVE → MAINTENANCE" in result
    assert _assets["LAPTOP-001"]["status"] == "maintenance"

  def test_update_invalid_status(self):
    result = cmdb_update_asset_status("LAPTOP-001", "broken")
    assert "Invalid status" in result

  def test_update_nonexistent_asset(self):
    result = cmdb_update_asset_status("GHOST-999", "active")
    assert "not found" in result.lower()

  def test_update_appends_notes(self):
    cmdb_update_asset_status("LAPTOP-001", "maintenance", "Repair note 1")
    assert "Repair note 1" in _assets["LAPTOP-001"]["notes"]

  def test_update_preserves_other_fields(self):
    original_name = _assets["LAPTOP-001"]["name"]
    cmdb_update_asset_status("LAPTOP-001", "maintenance")
    assert _assets["LAPTOP-001"]["name"] == original_name


class TestCMDBRegister:
  """Tests for cmdb_register_asset."""

  def test_register_new_laptop(self):
    result = cmdb_register_asset(
      name="Dell XPS 15",
      category="laptop",
      assigned_to="QA - Test User",
      department="QA",
      location="HQ Floor 5",
    )
    assert "registered successfully" in result
    assert "Dell XPS 15" in result
    assert "ACTIVE" in result

  def test_register_invalid_category(self):
    result = cmdb_register_asset(name="Widget", category="spaceship")
    assert "Invalid category" in result

  def test_register_generates_serial(self):
    result = cmdb_register_asset(name="Test Monitor", category="monitor")
    assert "AUTO-" in result

  def test_register_uses_provided_serial(self):
    result = cmdb_register_asset(
      name="Test Phone",
      category="phone",
      serial="CUSTOM-SERIAL-123",
    )
    assert "CUSTOM-SERIAL-123" in result

  def test_register_increments_id(self):
    result1 = cmdb_register_asset(name="Desktop 1", category="desktop")
    result2 = cmdb_register_asset(name="Desktop 2", category="desktop")
    # Both should succeed with different IDs
    assert "DESKTO-001" in result1
    assert "DESKTO-002" in result2


class TestCMDBInventory:
  """Tests for cmdb_inventory_summary."""

  def test_inventory_summary_counts(self):
    result = cmdb_inventory_summary()
    assert "6 total assets" in result
    assert "Laptop" in result
    assert "Server" in result

  def test_inventory_shows_status_breakdown(self):
    result = cmdb_inventory_summary()
    assert "ACTIVE" in result
    assert "MAINTENANCE" in result

  def test_inventory_empty_cmdb(self):
    _assets.clear()
    result = cmdb_inventory_summary()
    assert "empty" in result.lower()


# --- Knowledge Search Tests ---

knowledge_search = _ks_mod.knowledge_search


class TestKnowledgeSearch:
  """Tests for knowledge_search."""

  def test_search_vpn(self):
    result = knowledge_search("vpn connection issues")
    assert "VPN" in result
    assert "Knowledge Base" in result

  def test_search_password(self):
    result = knowledge_search("password reset policy")
    assert "Password" in result

  def test_search_onboarding(self):
    result = knowledge_search("new employee setup")
    assert "Onboarding" in result or "setup" in result.lower()

  def test_search_no_results(self):
    result = knowledge_search("quantum entanglement networking")
    assert "No knowledge base articles" in result

  def test_search_empty_query(self):
    result = knowledge_search("")
    assert "provide a search query" in result.lower()

  def test_search_max_results_respected(self):
    result = knowledge_search("security policy", max_results=1)
    # Should only have 1 numbered result
    assert "1." in result
    # Should NOT have a second result
    assert "\n2." not in result

  def test_search_printer(self):
    result = knowledge_search("printer setup troubleshooting")
    assert "Printer" in result or "printer" in result

  def test_search_remote_work(self):
    result = knowledge_search("remote work guidelines")
    assert "Remote" in result or "remote" in result
