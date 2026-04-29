# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# Copyright 2026 ShadowTag AI. All rights reserved.
"""Tests for JTF Headquarters scaffolds and J-6 → Cor_Claude_Code_6 Bridge.

Tests cover:
- JTF Staff Topology (JP 3-33)
- J-Staff designation lookup
- J-6 → Cor_Claude_Code_6 Bridge authorization
- J-6 augmented validation results
"""

import sys
import os

# Ensure repo root is on path for direct src.headquarters imports
_repo_root = os.path.join(os.path.dirname(__file__), "..", "..")
if _repo_root not in sys.path:
    sys.path.insert(0, os.path.abspath(_repo_root))

import pytest

from src.headquarters.jtf_staff_topology import JStaffDesignation, JTFHeadquarters
from src.headquarters.j6_Cor_Claude_Code_6_bridge import J6Cor_Claude_Code_6Bridge


# ============================================================================
# JTF Staff Topology Tests
# ============================================================================


class TestJStaffDesignation:
    """Tests for JStaffDesignation dataclass."""

    def test_designation_is_frozen(self):
        """Frozen dataclass prevents mutation."""
        d = JStaffDesignation("J-1", "Vault", "Custodian")
        with pytest.raises(AttributeError):
            d.j_code = "J-99"

    def test_designation_fields(self):
        """All three fields are accessible."""
        d = JStaffDesignation("J-6", "Judge 6.1", "ZTA")
        assert d.j_code == "J-6"
        assert d.agent_role == "Judge 6.1"
        assert d.doctrine_mandate == "ZTA"


class TestJTFHeadquarters:
    """Tests for JTFHeadquarters class."""

    def test_staff_has_seven_entries(self):
        """JP 3-33 topology defines 7 J-Staff positions."""
        assert len(JTFHeadquarters.STAFF) == 7

    def test_j_codes_present(self):
        """All expected J-codes exist."""
        expected = {"J1", "J2", "J3", "J4", "J5", "J6", "J9"}
        assert set(JTFHeadquarters.STAFF.keys()) == expected

    def test_get_routing_authority_j6(self):
        """J-6 routing authority returns Judge 6.1."""
        j6 = JTFHeadquarters.get_routing_authority("J6")
        assert j6.j_code == "J-6"
        assert j6.agent_role == "Judge 6.1"
        assert "CSRMC" in j6.doctrine_mandate

    def test_get_routing_authority_invalid(self):
        """Invalid J-code raises KeyError."""
        with pytest.raises(KeyError):
            JTFHeadquarters.get_routing_authority("J99")

    def test_list_staff(self):
        """list_staff returns all designations."""
        staff = JTFHeadquarters.list_staff()
        assert len(staff) == 7
        assert all(isinstance(s, JStaffDesignation) for s in staff)

    def test_j1_vault(self):
        """J-1 maps to Vault role."""
        j1 = JTFHeadquarters.get_routing_authority("J1")
        assert j1.agent_role == "Vault"

    def test_j2_intelligence(self):
        """J-2 maps to Jetski & Literature (intelligence)."""
        j2 = JTFHeadquarters.get_routing_authority("J2")
        assert "Jetski" in j2.agent_role
        assert "ATP 2-01.3" in j2.doctrine_mandate

    def test_j3_operations(self):
        """J-3 maps to Builder & Tester (operations)."""
        j3 = JTFHeadquarters.get_routing_authority("J3")
        assert "Builder" in j3.agent_role
        assert "FM 3-0" in j3.doctrine_mandate

    def test_j5_plans(self):
        """J-5 maps to Architect (plans)."""
        j5 = JTFHeadquarters.get_routing_authority("J5")
        assert j5.agent_role == "Architect"
        assert "ADP 5-0" in j5.doctrine_mandate

    def test_j9_splinter(self):
        """J-9 maps to Splinter Engine (info ops)."""
        j9 = JTFHeadquarters.get_routing_authority("J9")
        assert j9.agent_role == "Splinter Engine"


# ============================================================================
# J-6 → Cor_Claude_Code_6 Bridge Tests
# ============================================================================


class TestJ6Cor_Claude_Code_6Bridge:
    """Tests for J-6 → Cor_Claude_Code_6 Bridge."""

    def test_bridge_init(self):
        """Bridge initializes with correct J-6 designation."""
        bridge = J6Cor_Claude_Code_6Bridge()
        assert bridge.authority_code == "J-6"
        assert bridge.designation.agent_role == "Judge 6.1"

    def test_designation_property(self):
        """Designation property returns JStaffDesignation."""
        bridge = J6Cor_Claude_Code_6Bridge()
        assert isinstance(bridge.designation, JStaffDesignation)

    @pytest.mark.asyncio
    async def test_authorize_validation(self):
        """Authorization pre-flight grants access."""
        bridge = J6Cor_Claude_Code_6Bridge()
        auth = await bridge.authorize_validation({"text": "test request"}, request_id="test_001")
        assert auth["authorized"] is True
        assert auth["authority"] == "J-6"
        assert auth["c2_chain_verified"] is True
        assert auth["zta_posture"] == "continuous"
        assert auth["request_id"] == "test_001"

    @pytest.mark.asyncio
    async def test_authorize_includes_doctrine(self):
        """Authorization result includes doctrine mandate."""
        bridge = J6Cor_Claude_Code_6Bridge()
        auth = await bridge.authorize_validation({"text": "check"})
        assert "CSRMC" in auth["doctrine"]
        assert auth["agent_role"] == "Judge 6.1"
