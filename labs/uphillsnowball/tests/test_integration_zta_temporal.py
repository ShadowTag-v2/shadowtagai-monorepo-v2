# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# labs/uphillsnowball/tests/test_integration_zta_temporal.py
"""Integration test for end-to-end ZTA → Temporal flow (Item 19).

Tests the full chain from J-5 OPORD to J-6 audit receipt,
mocking Temporal's infrastructure with direct function calls.
"""

from __future__ import annotations

import asyncio

import pytest

from src.activities import (
    j1_shadowtag_dct_embed,
    j2_shaping_ops_recon,
    j39_splinter_information_ops,
    j3_decisive_ops_strike,
    j5_draft_opord_and_backbrief,
    j6_sustaining_ops_audit,
)
from src.activities.j3_roc_drill import j3_roc_drill_sandbox


class TestEndToEndCampaignFlow:
    """Integration test that exercises the full activity chain."""

    @pytest.fixture
    def mission(self) -> dict:
        return {
            "case_id": "INT-TEST-001",
            "purpose": "Integration test: validate full campaign pipeline",
            "key_tasks": ["recon", "strike", "audit"],
            "end_state": "All activities return structured results",
        }

    @pytest.mark.asyncio
    async def test_full_campaign_pipeline(self, mission):
        """Walk through the entire campaign activity chain end-to-end."""
        # Phase 1: J-5 Plans
        opord = await j5_draft_opord_and_backbrief(mission)
        assert opord["status"] == "BACKBRIEF_READY"
        assert "OPORD-INT-TEST-001" in opord["opord_id"]

        # Phase 2: J-2 Shaping Operations
        intel = await j2_shaping_ops_recon(opord)
        assert intel["status"] == "RECON_COMPLETE"

        # Phase 3: J-3 Decisive Operations
        assault_data = {"intel": intel, "opord": opord}
        artifact = await j3_decisive_ops_strike(assault_data)
        assert artifact["status"] == "STRIKE_COMPLETE"
        assert artifact["success"] is True

        # Phase 4: ROC Drill (sandbox verification)
        roc_report = await j3_roc_drill_sandbox(artifact)
        assert roc_report["passed"] is True

        # Phase 5: J-1 ShadowTag Watermarking
        watermarked = await j1_shadowtag_dct_embed(artifact)
        assert watermarked["dct_watermarked"] is True
        assert "c2pa_signature" in watermarked

        # Phase 6: J-6 Audit & Certification
        receipt = await j6_sustaining_ops_audit(watermarked)
        assert receipt["status"] == "CERTIFIED"
        assert receipt["compliant"] is True

        # Phase 7: J-39 Information Operations
        io_result = await j39_splinter_information_ops(receipt)
        assert io_result["status"] == "IO_COMPLETE"
        assert io_result["syndicated"] is True

    @pytest.mark.asyncio
    async def test_opord_propagates_case_id(self, mission):
        """OPORD preserves the original case_id through the pipeline."""
        opord = await j5_draft_opord_and_backbrief(mission)
        assert mission["case_id"] in opord["opord_id"]

    @pytest.mark.asyncio
    async def test_pipeline_handles_empty_mission(self):
        """Empty mission dict doesn't crash the pipeline."""
        opord = await j5_draft_opord_and_backbrief({})
        assert opord["status"] == "BACKBRIEF_READY"
        intel = await j2_shaping_ops_recon(opord)
        assert intel["status"] == "RECON_COMPLETE"
