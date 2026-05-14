# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Unit tests for kernel chain components.

Tests cover:
- Base kernel timing, hashing, error isolation
- JudgeSixClassifyKernel feature extraction, classification logic, risk tiers
- AuditCompressKernel compression, decompression, checksum integrity
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch, MagicMock

from app.kernels.base import Kernel, KernelChainError
from app.kernels.audit_compress import AuditCompressKernel
from app.models.kernel import KernelInput, KernelOutput, KernelMetrics
from app.models.decision import (
    Violation,
    ViolationsScanOutput,
    JudgeSixClassification,
    AuditTrail,
    RiskTier,
    DecisionContext,
)

# ─── Skip JudgeSix if torch unavailable ─────────────────────────────────
torch = pytest.importorskip("torch", reason="PyTorch required for JudgeSix tests")
from app.kernels.judge_six import JudgeSixClassifyKernel, JudgeSixModel


# ─── Fixtures ────────────────────────────────────────────────────────────


@pytest.fixture
def violations_empty():
    """ViolationsScanOutput with no violations."""
    return ViolationsScanOutput(violations=[], scan_metadata={"model": "test"})


@pytest.fixture
def violations_minor():
    """ViolationsScanOutput with one minor violation."""
    return ViolationsScanOutput(
        violations=[
            Violation(
                rule_id="ATP-5-19-3.1",
                description="Missing documentation",
                severity="minor",
                context="No justification provided",
                suggested_action="Add justification",
            )
        ],
        scan_metadata={"model": "test"},
    )


@pytest.fixture
def violations_critical():
    """ViolationsScanOutput with critical violations."""
    return ViolationsScanOutput(
        violations=[
            Violation(
                rule_id="ATP-5-19-1.1",
                description="Authority limit exceeded",
                severity="critical",
                context="Decision above $1M without board approval",
                suggested_action="Escalate to board",
            ),
            Violation(
                rule_id="ATP-5-19-6.1",
                description="Undisclosed conflict of interest",
                severity="major",
                context="Decision maker has financial interest",
                suggested_action="Recuse and reassign",
            ),
        ],
        scan_metadata={"model": "test"},
    )


@pytest.fixture
def violations_mixed():
    """ViolationsScanOutput with mixed severity violations."""
    return ViolationsScanOutput(
        violations=[
            Violation(rule_id="ATP-5-19-2.1", description="Late filing", severity="minor"),
            Violation(rule_id="ATP-5-19-3.2", description="Incomplete record", severity="moderate"),
            Violation(rule_id="ATP-5-19-4.1", description="Outside timeframe", severity="major"),
        ],
        scan_metadata={"model": "test"},
    )


@pytest.fixture
def kernel_input_empty(violations_empty):
    return KernelInput(data=violations_empty, trace_id="trace-001")


@pytest.fixture
def kernel_input_minor(violations_minor):
    return KernelInput(data=violations_minor, trace_id="trace-002")


@pytest.fixture
def kernel_input_critical(violations_critical):
    return KernelInput(data=violations_critical, trace_id="trace-003")


@pytest.fixture
def kernel_input_mixed(violations_mixed):
    return KernelInput(data=violations_mixed, trace_id="trace-004")


@pytest.fixture
def judge_kernel():
    """JudgeSixClassifyKernel instance."""
    return JudgeSixClassifyKernel()


@pytest.fixture
def audit_kernel():
    """AuditCompressKernel instance."""
    return AuditCompressKernel()


# ─── Base Kernel Tests ───────────────────────────────────────────────────


class TestBaseKernel:
    """Tests for the base Kernel class."""

    def test_hash_data_string(self):
        """Test SHA256 hashing of string data."""
        result = Kernel._hash_data("test data")
        assert len(result) == 16  # First 16 chars of hex digest
        assert isinstance(result, str)

    def test_hash_data_bytes(self):
        """Test SHA256 hashing of bytes data."""
        result = Kernel._hash_data(b"test data")
        assert len(result) == 16

    def test_hash_data_dict(self):
        """Test SHA256 hashing of dict data."""
        result = Kernel._hash_data({"key": "value"})
        assert len(result) == 16

    def test_hash_data_deterministic(self):
        """Same input produces same hash."""
        hash1 = Kernel._hash_data("same data")
        hash2 = Kernel._hash_data("same data")
        assert hash1 == hash2

    def test_hash_data_different(self):
        """Different input produces different hash."""
        hash1 = Kernel._hash_data("data a")
        hash2 = Kernel._hash_data("data b")
        assert hash1 != hash2

    def test_kernel_chain_error(self):
        """KernelChainError can be raised and caught."""
        with pytest.raises(KernelChainError, match="test error"):
            raise KernelChainError("test error")


# ─── JudgeSixModel Tests ────────────────────────────────────────────────


class TestJudgeSixModel:
    """Tests for the JudgeSixModel neural network."""

    def test_model_initialization(self):
        """Model initializes with correct architecture."""
        model = JudgeSixModel(input_dim=10)
        assert model is not None

    def test_model_forward_pass(self):
        """Model produces output in [0, 1] range."""
        model = JudgeSixModel(input_dim=10)
        model.eval()
        with torch.no_grad():
            x = torch.randn(1, 10)
            output = model(x)
            assert output.shape == (1, 1)
            assert 0.0 <= output.item() <= 1.0

    def test_model_batch_forward(self):
        """Model handles batch input."""
        model = JudgeSixModel(input_dim=10)
        model.eval()
        with torch.no_grad():
            x = torch.randn(8, 10)
            output = model(x)
            assert output.shape == (8, 1)


# ─── JudgeSixClassifyKernel Tests ───────────────────────────────────────


class TestJudgeSixClassifyKernel:
    """Tests for the JudgeSixClassifyKernel."""

    @pytest.mark.asyncio
    async def test_no_violations_approve(self, judge_kernel, kernel_input_empty):
        """No violations → decision=True (approve)."""
        result = await judge_kernel(kernel_input_empty)
        assert result.success
        assert result.data.decision is True
        assert result.data.confidence >= 0.85
        assert result.data.risk_tier == RiskTier.TIER_1_MINIMAL

    @pytest.mark.asyncio
    async def test_minor_violation_reject(self, judge_kernel, kernel_input_minor):
        """Minor violation → decision=False (reject)."""
        result = await judge_kernel(kernel_input_minor)
        assert result.success
        assert result.data.decision is False

    @pytest.mark.asyncio
    async def test_critical_violation_reject(self, judge_kernel, kernel_input_critical):
        """Critical violations → decision=False, high confidence."""
        result = await judge_kernel(kernel_input_critical)
        assert result.success
        assert result.data.decision is False
        assert result.data.confidence >= 0.7

    @pytest.mark.asyncio
    async def test_risk_tier_critical(self, judge_kernel, kernel_input_critical):
        """Critical violations → high risk tier."""
        result = await judge_kernel(kernel_input_critical)
        assert result.data.risk_tier.value >= RiskTier.TIER_4_HIGH.value

    @pytest.mark.asyncio
    async def test_risk_tier_minimal(self, judge_kernel, kernel_input_empty):
        """No violations → minimal risk tier."""
        result = await judge_kernel(kernel_input_empty)
        assert result.data.risk_tier == RiskTier.TIER_1_MINIMAL

    @pytest.mark.asyncio
    async def test_reasoning_no_violations(self, judge_kernel, kernel_input_empty):
        """Reasoning text for no violations."""
        result = await judge_kernel(kernel_input_empty)
        assert "No ATP 5-19 violations" in result.data.reasoning

    @pytest.mark.asyncio
    async def test_reasoning_with_violations(self, judge_kernel, kernel_input_critical):
        """Reasoning text includes violation counts."""
        result = await judge_kernel(kernel_input_critical)
        assert "2 violation" in result.data.reasoning
        assert "critical" in result.data.reasoning

    @pytest.mark.asyncio
    async def test_metrics_zero_cost(self, judge_kernel, kernel_input_empty):
        """Local inference has zero cost."""
        result = await judge_kernel(kernel_input_empty)
        assert result.metrics.cost_usd == 0.0

    @pytest.mark.asyncio
    async def test_latency_recorded(self, judge_kernel, kernel_input_empty):
        """Latency is recorded in metrics."""
        result = await judge_kernel(kernel_input_empty)
        assert result.metrics.latency_ms > 0

    @pytest.mark.asyncio
    async def test_trace_id_propagated(self, judge_kernel, kernel_input_empty):
        """Trace ID propagates through kernel."""
        result = await judge_kernel(kernel_input_empty)
        assert result.trace_id == "trace-001"

    @pytest.mark.asyncio
    async def test_invalid_input_type(self, judge_kernel):
        """Invalid input type raises KernelChainError."""
        bad_input = KernelInput(data="not a ViolationsScanOutput", trace_id="trace-bad")
        with pytest.raises(KernelChainError, match="Invalid input type"):
            await judge_kernel(bad_input)

    def test_feature_extraction_empty(self, judge_kernel, violations_empty):
        """Feature extraction from empty violations."""
        features = judge_kernel._extract_features(violations_empty)
        assert len(features) == 10
        assert all(f == 0.0 for f in features)

    def test_feature_extraction_critical(self, judge_kernel, violations_critical):
        """Feature extraction includes critical flag."""
        features = judge_kernel._extract_features(violations_critical)
        assert len(features) == 10
        assert features[7] == 1.0  # has_critical flag

    def test_feature_extraction_normalized(self, judge_kernel, violations_mixed):
        """All features are in [0, 1] range."""
        features = judge_kernel._extract_features(violations_mixed)
        assert all(0.0 <= f <= 1.0 for f in features)


# ─── AuditCompressKernel Tests ──────────────────────────────────────────


class TestAuditCompressKernel:
    """Tests for the AuditCompressKernel."""

    @pytest.fixture
    def classification_approve(self):
        return JudgeSixClassification(
            decision=True,
            confidence=0.95,
            risk_tier=RiskTier.TIER_1_MINIMAL,
            reasoning="No violations detected.",
        )

    @pytest.fixture
    def classification_reject(self):
        return JudgeSixClassification(
            decision=False,
            confidence=0.85,
            risk_tier=RiskTier.TIER_4_HIGH,
            reasoning="Critical violations found.",
        )

    @pytest.mark.asyncio
    async def test_compress_approve(self, audit_kernel, classification_approve):
        """Compress an approval decision."""
        ki = KernelInput(data=classification_approve, trace_id="trace-c1")
        result = await audit_kernel(ki)
        assert result.success
        assert isinstance(result.data, AuditTrail)
        assert result.data.compression_ratio > 1.0

    @pytest.mark.asyncio
    async def test_compress_reject(self, audit_kernel, classification_reject):
        """Compress a rejection decision."""
        ki = KernelInput(data=classification_reject, trace_id="trace-c2")
        result = await audit_kernel(ki)
        assert result.success
        assert result.data.compressed_size_bytes > 0
        assert result.data.original_size_bytes > result.data.compressed_size_bytes

    @pytest.mark.asyncio
    async def test_checksum_integrity(self, audit_kernel, classification_approve):
        """Checksum matches compressed data."""
        import hashlib

        ki = KernelInput(data=classification_approve, trace_id="trace-c3")
        result = await audit_kernel(ki)
        expected_checksum = hashlib.sha256(result.data.compressed_data).hexdigest()
        assert result.data.checksum == expected_checksum

    @pytest.mark.asyncio
    async def test_decompress_roundtrip(self, audit_kernel, classification_approve):
        """Compress then decompress returns original data."""
        ki = KernelInput(data=classification_approve, trace_id="trace-c4")
        result = await audit_kernel(ki)
        decompressed = AuditCompressKernel.decompress(result.data)
        assert decompressed["decision"] is True
        assert decompressed["confidence"] == 0.95
        assert decompressed["risk_tier"] == RiskTier.TIER_1_MINIMAL.value

    @pytest.mark.asyncio
    async def test_invalid_input_type(self, audit_kernel):
        """Invalid input raises KernelChainError."""
        bad_input = KernelInput(data="not a classification", trace_id="trace-bad")
        with pytest.raises(KernelChainError, match="Invalid input type"):
            await audit_kernel(bad_input)

    @pytest.mark.asyncio
    async def test_compression_ratio_metadata(self, audit_kernel, classification_reject):
        """Metadata includes compression ratio."""
        ki = KernelInput(data=classification_reject, trace_id="trace-c5")
        result = await audit_kernel(ki)
        assert "compression_ratio" in result.metadata
        assert "size_reduction_pct" in result.metadata
        assert result.metadata["size_reduction_pct"] > 0

    @pytest.mark.asyncio
    async def test_zero_cost(self, audit_kernel, classification_approve):
        """Deterministic compression has zero cost."""
        ki = KernelInput(data=classification_approve, trace_id="trace-c6")
        result = await audit_kernel(ki)
        assert result.metrics.cost_usd == 0.0

    @pytest.mark.asyncio
    async def test_trace_id_propagated(self, audit_kernel, classification_approve):
        """Trace ID propagates through audit kernel."""
        ki = KernelInput(data=classification_approve, trace_id="trace-c7")
        result = await audit_kernel(ki)
        assert result.trace_id == "trace-c7"


# ─── Integration: Kernel Chain Tests ────────────────────────────────────


class TestKernelChainIntegration:
    """Tests for chaining JudgeSix → AuditCompress."""

    @pytest.mark.asyncio
    async def test_full_chain_no_violations(self, judge_kernel, audit_kernel, kernel_input_empty):
        """Full chain: no violations → approve → compress."""
        judge_output = await judge_kernel(kernel_input_empty)
        assert judge_output.data.decision is True

        audit_input = KernelInput(data=judge_output.data, trace_id="chain-001")
        audit_output = await audit_kernel(audit_input)
        assert audit_output.success

        # Roundtrip decompress
        decompressed = AuditCompressKernel.decompress(audit_output.data)
        assert decompressed["decision"] is True

    @pytest.mark.asyncio
    async def test_full_chain_critical(self, judge_kernel, audit_kernel, kernel_input_critical):
        """Full chain: critical violations → reject → compress."""
        judge_output = await judge_kernel(kernel_input_critical)
        assert judge_output.data.decision is False

        audit_input = KernelInput(data=judge_output.data, trace_id="chain-002")
        audit_output = await audit_kernel(audit_input)
        assert audit_output.success

        decompressed = AuditCompressKernel.decompress(audit_output.data)
        assert decompressed["decision"] is False
        assert decompressed["risk_tier"] >= RiskTier.TIER_4_HIGH.value
