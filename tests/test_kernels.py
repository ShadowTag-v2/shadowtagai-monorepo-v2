# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Tests for individual kernel implementations."""

import pytest
from app.models.kernel import KernelInput
from app.models.decision import (
  DecisionContext,
  ViolationsScanOutput,
  JudgeSixClassification,
  AuditTrail,
)
from app.kernels import (
  ATP519ScanKernel,
  JudgeSixClassifyKernel,
  AuditCompressKernel,
)
from app.config import settings


class TestATP519ScanKernel:
  """Tests for kernel_1: ATP 5-19 Violation Scanner."""

  @pytest.mark.asyncio
  @pytest.mark.skipif(
    not settings.gemini_api_key, reason="Gemini API key not configured"
  )
  async def test_scan_with_violations(self, sample_decision_context):
    """Test scanning context with violations."""
    kernel = ATP519ScanKernel()

    decision_context = DecisionContext(content=sample_decision_context)
    kernel_input = KernelInput(data=decision_context)

    output = await kernel(kernel_input)

    assert output.success is True
    assert isinstance(output.data, ViolationsScanOutput)
    assert len(output.data.violations) > 0
    assert (
      output.metrics.latency_ms <= settings.kernel_1_max_latency_ms * 2
    )  # Allow 2x for test

    # Validate token reduction
    assert output.metrics.token_count_output <= settings.kernel_1_max_output_tokens

  @pytest.mark.asyncio
  @pytest.mark.skipif(
    not settings.gemini_api_key, reason="Gemini API key not configured"
  )
  async def test_scan_clean_context(self, sample_clean_context):
    """Test scanning clean context (no violations)."""
    kernel = ATP519ScanKernel()

    decision_context = DecisionContext(content=sample_clean_context)
    kernel_input = KernelInput(data=decision_context)

    output = await kernel(kernel_input)

    assert output.success is True
    assert isinstance(output.data, ViolationsScanOutput)
    assert len(output.data.violations) == 0


class TestJudgeSixClassifyKernel:
  """Tests for kernel_2: Judge #6 Classifier."""

  @pytest.mark.asyncio
  async def test_classify_with_violations(self):
    """Test classification with violations."""
    from app.models.decision import Violation

    kernel = JudgeSixClassifyKernel()

    violations_output = ViolationsScanOutput(
      violations=[
        Violation(
          rule_id="ATP-5-19-1.2",
          description="Authority limit exceeded",
          severity="critical",
        ),
        Violation(
          rule_id="ATP-5-19-2.8",
          description="Required stakeholder not consulted",
          severity="major",
        ),
      ]
    )

    kernel_input = KernelInput(data=violations_output)
    output = await kernel(kernel_input)

    assert output.success is True
    assert isinstance(output.data, JudgeSixClassification)
    assert (
      output.metrics.latency_ms <= settings.kernel_2_max_latency_ms * 5
    )  # Allow 5x for CPU
    assert output.metrics.cost_usd == 0.0  # Local inference

    # Should reject due to critical violation
    assert output.data.decision is False
    assert output.data.confidence >= settings.confidence_threshold

  @pytest.mark.asyncio
  async def test_classify_no_violations(self):
    """Test classification with no violations."""
    kernel = JudgeSixClassifyKernel()

    violations_output = ViolationsScanOutput(violations=[])
    kernel_input = KernelInput(data=violations_output)

    output = await kernel(kernel_input)

    assert output.success is True
    assert isinstance(output.data, JudgeSixClassification)

    # Should approve (no violations)
    assert output.data.decision is True


class TestAuditCompressKernel:
  """Tests for kernel_3: Audit Trail Compression."""

  @pytest.mark.asyncio
  async def test_compress_audit_trail(self):
    """Test audit trail compression."""
    from app.models.decision import RiskTier

    kernel = AuditCompressKernel()

    classification = JudgeSixClassification(
      decision=False,
      confidence=0.92,
      risk_tier=RiskTier.TIER_4_HIGH,
      reasoning="High risk decision rejected",
    )

    # Build a large, repetitive metadata payload to give zstd enough
    # material for meaningful compression (small inputs can't reach 5:1).
    large_metadata = {
      "test": "metadata",
      "audit_rules": [
        {
          "rule_id": f"ATP-5-19-{i}.{j}",
          "description": f"Authority limit check for section {i} paragraph {j}",
          "severity": "critical" if i % 3 == 0 else "major",
          "status": "evaluated",
          "timestamp": "2026-05-14T00:00:00Z",
        }
        for i in range(1, 21)
        for j in range(1, 6)
      ],
      "environment": {
        "runtime": "python-3.14.4",
        "model": "judge-six-v1",
        "trace_context": "sovereign-meridian-test-harness",
      },
    }

    kernel_input = KernelInput(
      data=classification,
      trace_id="test-trace-123",
      metadata=large_metadata,
    )

    output = await kernel(kernel_input)

    assert output.success is True
    assert isinstance(output.data, AuditTrail)
    assert output.data.compression_ratio >= 5.0  # Expect at least 5:1
    assert output.data.compressed_size_bytes < output.data.original_size_bytes
    assert len(output.data.checksum) == 64  # SHA256 hex
    assert output.metrics.cost_usd == 0.0  # Deterministic compression

  @pytest.mark.asyncio
  async def test_decompress_audit_trail(self):
    """Test decompression to verify data integrity."""
    from app.models.decision import RiskTier

    kernel = AuditCompressKernel()

    classification = JudgeSixClassification(
      decision=True,
      confidence=0.95,
      risk_tier=RiskTier.TIER_2_LOW,
    )

    kernel_input = KernelInput(
      data=classification,
      trace_id="test-trace-456",
    )

    output = await kernel(kernel_input)
    audit_trail = output.data

    # Decompress and verify
    decompressed = kernel.decompress(audit_trail)

    assert decompressed["decision"] == classification.decision
    assert decompressed["confidence"] == classification.confidence
    assert decompressed["risk_tier"] == classification.risk_tier
    assert decompressed["trace_id"] == "test-trace-456"
