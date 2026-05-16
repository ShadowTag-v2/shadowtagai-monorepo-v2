# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Unit tests for Semantic Compression
Tests audit trail compression, decompression, and validation
"""

import pytest
from src.utils.semantic_compression import (
    compress_audit_trail,
    decompress_audit_trail,
    generate_trail_id,
    calculate_compression_ratio,
    validate_semantic_trail,
)
from datetime import datetime


class TestSemanticCompression:
    """Test audit trail semantic compression"""

    def test_basic_compression(self):
        """Test basic compression with all components"""
        context = {
            "amount_usd": 50000,
            "vendor": "VND-12345",
            "vendor_status": "new",
            "purchase_order": None,
        }

        trail = compress_audit_trail(
            action_type="wire_transfer", context=context, decision="BLOCK", risk_level="high", approval_required=True, approval_authority="CFO"
        )

        assert "wire" in trail
        assert "$50K" in trail
        assert "new_vendor" in trail
        assert "no_PO" in trail
        assert "high_risk" in trail
        assert "cfo_gate" in trail
        assert "BLOCK" in trail
        assert "→" in trail

    def test_compression_with_po(self):
        """Test compression when purchase order exists"""
        context = {
            "amount_usd": 25000,
            "vendor_status": "approved",
            "purchase_order": "PO-123456",
        }

        trail = compress_audit_trail(
            action_type="payment_authorization",
            context=context,
            decision="ALLOW",
            risk_level="low",
            approval_required=False,
        )

        assert "PO_PO-123456" in trail
        assert "approved_vendor" in trail
        assert "low_risk" in trail
        assert "auto_gate" in trail
        assert "ALLOW" in trail

    def test_large_amount_formatting(self):
        """Test amount formatting for different scales"""
        # Millions
        context1 = {"amount_usd": 2_500_000}
        trail1 = compress_audit_trail("contract", context1, "ALLOW", "medium", True, "CFO")
        assert "$2.5M" in trail1

        # Thousands
        context2 = {"amount_usd": 75_000}
        trail2 = compress_audit_trail("wire", context2, "BLOCK", "high", True, "CFO")
        assert "$75K" in trail2

        # Under 1K
        context3 = {"amount_usd": 500}
        trail3 = compress_audit_trail("payment", context3, "ALLOW", "low", False)
        assert "$500" in trail3

    def test_fraud_indicators(self):
        """Test compression with fraud scores"""
        context = {
            "amount_usd": 5000,
            "fraud_score": 0.85,
        }

        trail = compress_audit_trail(
            action_type="fraud_check",
            context=context,
            decision="BLOCK",
            risk_level="extremely_high",
            approval_required=True,
            approval_authority="Manual Review",
        )

        assert "fraud_high" in trail
        assert "BLOCK" in trail


class TestSemanticDecompression:
    """Test decompression of semantic trails"""

    def test_basic_decompression(self):
        """Test decompressing a semantic trail"""
        trail = "wire→$75K→new_vendor→no_PO→high_risk→CFO_gate→BLOCK"
        result = decompress_audit_trail(trail)

        assert result["action"] == "wire"
        assert result["decision"] == "BLOCK"
        assert result["risk_level"] == "high"
        assert result["approval_gate"] == "CFO"
        assert result["amount"] == "$75K"
        assert "no_PO" in result["components"]

    def test_decompress_with_po(self):
        """Test decompressing trail with purchase order"""
        trail = "payment→$25K→approved_vendor→PO_123456→low_risk→auto_gate→ALLOW"
        result = decompress_audit_trail(trail)

        assert result["purchase_order"] == "123456"
        assert result["vendor_status"] == "approved"
        assert result["approval_gate"] == "auto"

    def test_decompress_fraud_trail(self):
        """Test decompressing fraud trail"""
        trail = "fraud→$5K→fraud_high→geo_mismatch→EH_risk→manual_review_gate→BLOCK"
        result = decompress_audit_trail(trail)

        assert result["fraud_level"] == "high"
        assert result["decision"] == "BLOCK"
        assert result["risk_level"] == "EH"


class TestTrailIDGeneration:
    """Test trail ID generation"""

    def test_trail_id_format(self):
        """Test trail ID format is correct"""
        trail_id = generate_trail_id(judge_type="FinJudge", request_id="req_20251117_001", timestamp=datetime(2025, 11, 17, 14, 30, 0))

        assert trail_id.startswith("trail_20251117_finj_")
        assert len(trail_id.split("_")) == 4  # trail_date_type_hash

    def test_trail_id_uniqueness(self):
        """Test that different request IDs generate different trail IDs"""
        timestamp = datetime(2025, 11, 17, 14, 30, 0)

        trail_id1 = generate_trail_id("FinJudge", "req_001", timestamp)
        trail_id2 = generate_trail_id("FinJudge", "req_002", timestamp)

        assert trail_id1 != trail_id2

    def test_trail_id_consistency(self):
        """Test that same inputs generate same trail ID"""
        timestamp = datetime(2025, 11, 17, 14, 30, 0)

        trail_id1 = generate_trail_id("FinJudge", "req_001", timestamp)
        trail_id2 = generate_trail_id("FinJudge", "req_001", timestamp)

        assert trail_id1 == trail_id2


class TestCompressionRatio:
    """Test compression ratio calculations"""

    def test_compression_ratio_calculation(self):
        """Test that compression ratio is calculated correctly"""
        original = {
            "amount_usd": 50000,
            "vendor_id": "VND-12345",
            "vendor_name": "Acme Corporation",
            "vendor_status": "new",
            "purchase_order": None,
            "destination_country": "Unknown",
            "destination_bank": "Unknown Bank AG",
            "requested_by": "john.doe@company.com",
            "request_timestamp": "2025-11-17T14:30:00Z",
            "action_type": "wire_transfer",
            "department": "Finance",
            "cost_center": "CC-1234",
        }

        compressed = "wire→$50K→new_vendor→no_PO→high_risk→CFO_gate→BLOCK"

        ratio = calculate_compression_ratio(original, compressed)

        # Should be significant compression (>5:1)
        assert ratio > 5.0
        # Should be less than 20:1 (not magic)
        assert ratio < 20.0

    def test_compression_target_10_to_1(self):
        """Test that we approach 10:1 compression target"""
        # Realistic original context with full wire transfer details
        original = {
            "amount_usd": 75000,
            "vendor_id": "VND-12345",
            "vendor_status": "new",
            "vendor_name": "Example Vendor Inc.",
            "vendor_address": "123 Example Street, Suite 400, New York, NY 10001",
            "purchase_order": None,
            "destination_country": "Unknown",
            "destination_bank": "Unknown International Bank AG",
            "destination_account": "IBAN DE89370400440532013000",
            "requested_by": "user@company.com",
            "requester_department": "Engineering",
            "cost_center": "CC-ENG-4200",
            "timestamp": "2025-11-17T14:30:00Z",
            "approval_chain": ["manager@company.com", "director@company.com"],
            "notes": "Quarterly infrastructure payment for cloud services",
        }

        compressed = compress_audit_trail("wire_transfer", original, "BLOCK", "high", True, "CFO")

        ratio = calculate_compression_ratio(original, compressed)

        # Target is 10:1, accept 7:1 to 15:1 as reasonable
        assert ratio >= 7.0
        assert ratio <= 15.0


class TestTrailValidation:
    """Test semantic trail validation"""

    def test_valid_trails(self):
        """Test that valid trails pass validation"""
        valid_trails = [
            "wire→$75K→new_vendor→no_PO→high_risk→CFO_gate→BLOCK",
            "contract→$2.5M→3yr_term→legal_approved→medium_risk→auto_gate→ALLOW",
            "fraud→fraud_high→geo_mismatch→EH_risk→manual_review_gate→BLOCK",
            "case→$500K→conflict_failed→EH_risk→escalate→BLOCK",
        ]

        for trail in valid_trails:
            assert validate_semantic_trail(trail), f"Failed to validate: {trail}"

    def test_invalid_trails(self):
        """Test that invalid trails fail validation"""
        invalid_trails = [
            "",  # Empty
            "wire→$75K",  # Too short (no risk or decision)
            "action→risk",  # Missing decision
            "action→decision",  # Missing risk indicator
            "→→→",  # Only separators
            "ALLOW",  # Only decision, no context
        ]

        for trail in invalid_trails:
            assert not validate_semantic_trail(trail), f"Should have failed: {trail}"

    def test_trail_must_have_risk_indicator(self):
        """Test that trails must contain risk indicator"""
        no_risk = "wire→$75K→new_vendor→BLOCK"
        assert not validate_semantic_trail(no_risk)

        with_risk = "wire→$75K→new_vendor→high_risk→BLOCK"
        assert validate_semantic_trail(with_risk)

    def test_trail_must_end_with_decision(self):
        """Test that trails must end with ALLOW or BLOCK"""
        no_decision = "wire→$75K→high_risk→CFO_gate"
        assert not validate_semantic_trail(no_decision)

        with_allow = "wire→$75K→high_risk→CFO_gate→ALLOW"
        assert validate_semantic_trail(with_allow)

        with_block = "wire→$75K→high_risk→CFO_gate→BLOCK"
        assert validate_semantic_trail(with_block)

        wrong_decision = "wire→$75K→high_risk→CFO_gate→MAYBE"
        assert not validate_semantic_trail(wrong_decision)


class TestEdgeCases:
    """Test edge cases in semantic compression"""

    def test_empty_context(self):
        """Test compression with minimal context"""
        trail = compress_audit_trail("unknown_action", {}, "BLOCK", "high", True, "Escalate")

        assert "high_risk" in trail
        assert "escalate_gate" in trail
        assert "BLOCK" in trail

    def test_very_long_action_name(self):
        """Test that long action names are abbreviated"""
        trail = compress_audit_trail("very_long_action_name_that_should_be_abbreviated", {"amount_usd": 1000}, "ALLOW", "low", False)

        # Should be abbreviated to ≤10 chars
        action = trail.split("→")[0]
        assert len(action) <= 10

    def test_special_characters_in_context(self):
        """Test handling of special characters"""
        context = {
            "vendor": "Vendor & Co.",
            "note": "Special → characters",
            "amount_usd": 5000,
        }

        trail = compress_audit_trail("payment", context, "ALLOW", "low", False)

        # Should still be valid
        assert validate_semantic_trail(trail)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
