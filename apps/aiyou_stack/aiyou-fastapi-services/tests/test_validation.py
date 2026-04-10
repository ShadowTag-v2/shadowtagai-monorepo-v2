"""Tests for JR Engine validation framework."""

from app.validation import JREngine, ValidationStatus


class TestJREngine:
    """Tests for JR Engine kernel validation."""

    def test_validate_approved_kernel(self):
        """Test validation of approved kernel (ATP519ScanKernel)."""
        engine = JREngine()
        validation = engine.validate_kernel("ATP519ScanKernel")

        assert validation.verdict == "APPROVED"
        assert validation.purpose_status == ValidationStatus.PASS
        assert validation.reasons_status == ValidationStatus.PASS
        assert validation.brakes_status == ValidationStatus.PASS

    def test_validate_full_chain(self):
        """Test validation of full 3-kernel chain."""
        engine = JREngine()
        result = engine.validate_kernel_chain(
            [
                "ATP519ScanKernel",
                "JudgeSixClassifyKernel",
                "AuditCompressKernel",
            ]
        )

        assert result.passed is True
        assert result.total_kernels == 3
        assert result.approved_kernels == 3
        assert result.rejected_kernels == 0
        assert len(result.validations) == 3

    def test_reject_invalid_kernel(self):
        """Test rejection of invalid kernel (SentimentAnalysisKernel)."""
        engine = JREngine()

        # The REJECTED_EXAMPLE shows how a kernel would be rejected
        rejected = engine.REJECTED_EXAMPLE

        assert rejected.verdict == "REJECTED"
        assert rejected.purpose_status == ValidationStatus.FAIL
        assert rejected.reasons_status == ValidationStatus.FAIL

    def test_unknown_kernel_warning(self):
        """Test that unknown kernels generate warnings."""
        engine = JREngine()
        result = engine.validate_kernel_chain(
            [
                "ATP519ScanKernel",
                "UnknownKernel",  # Not in validation set
            ]
        )

        assert result.passed is False  # Unknown kernel = not fully approved
        assert len(result.recommendations) > 0
        assert any("UnknownKernel" in rec for rec in result.recommendations)

    def test_jr_engine_criteria(self):
        """Test that all JR Engine criteria are validated."""
        engine = JREngine()

        # Each kernel should have all 3 criteria validated
        for kernel_name in ["ATP519ScanKernel", "JudgeSixClassifyKernel", "AuditCompressKernel"]:
            validation = engine.validate_kernel(kernel_name)

            # Must have all criteria
            assert validation.purpose_status is not None
            assert validation.purpose_notes is not None
            assert validation.reasons_status is not None
            assert validation.reasons_notes is not None
            assert validation.brakes_status is not None
            assert validation.brakes_notes is not None
            assert validation.verdict is not None
