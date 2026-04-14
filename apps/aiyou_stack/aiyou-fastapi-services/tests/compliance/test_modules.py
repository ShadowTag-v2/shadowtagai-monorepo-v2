"""Tests for Individual Compliance Modules
"""

import pytest

from app.compliance.registry import auto_register_modules, get_registry
from app.models.compliance import (
    AssessmentInput,
    RegulationId,
    RiskTier,
)


@pytest.fixture(autouse=True)
def setup_modules():
    """Ensure modules are registered before tests"""
    auto_register_modules()


class TestEUAIActModule:
    """Test cases for EU AI Act module"""

    @pytest.fixture
    def module(self):
        return get_registry().get_module(RegulationId.EU_AI_ACT)

    def test_module_metadata(self, module):
        """Module should have correct metadata"""
        assert module.module_id == RegulationId.EU_AI_ACT
        assert module.metadata.short_name == "EU AI Act"
        assert module.metadata.jurisdiction.value == "eu"

    def test_controls_defined(self, module):
        """Module should have controls defined"""
        assert len(module.controls) > 0
        control_ids = [c.control_id for c in module.controls]
        assert "EU-AI-9.1" in control_ids  # Risk Management
        assert "EU-AI-50.1" in control_ids  # AI Disclosure

    def test_risk_tier_minimal(self, module):
        """Non-AI content should be minimal risk"""
        input_data = AssessmentInput(
            content_type="general_content",
            is_ai_generated=False,
        )
        risk = module.determine_risk_tier(input_data)
        assert risk == RiskTier.MINIMAL

    def test_risk_tier_limited_ai_generated(self, module):
        """AI-generated content should be limited risk"""
        input_data = AssessmentInput(
            content_type="general_content",
            is_ai_generated=True,
        )
        risk = module.determine_risk_tier(input_data)
        assert risk == RiskTier.LIMITED

    def test_risk_tier_high_minors(self, module):
        """Content involving minors should be high risk"""
        input_data = AssessmentInput(
            content_type="education_content",
            user_age=15,
        )
        risk = module.determine_risk_tier(input_data)
        assert risk == RiskTier.HIGH

    @pytest.mark.asyncio
    async def test_assess(self, module):
        """Should run full assessment"""
        input_data = AssessmentInput(
            content_type="ai_chatbot",
            is_ai_generated=True,
            metadata={"ai_disclosure": True},
        )
        result = await module.assess(input_data)

        assert result.module_id == RegulationId.EU_AI_ACT
        assert result.controls_assessed > 0
        assert 0 <= result.compliance_score <= 1


class TestGDPRModule:
    """Test cases for GDPR module"""

    @pytest.fixture
    def module(self):
        return get_registry().get_module(RegulationId.GDPR)

    def test_module_metadata(self, module):
        """Module should have correct metadata"""
        assert module.module_id == RegulationId.GDPR
        assert module.metadata.short_name == "GDPR"

    def test_controls_defined(self, module):
        """Module should have controls defined"""
        control_ids = [c.control_id for c in module.controls]
        assert "GDPR-5.1c" in control_ids  # Data Minimization
        assert "GDPR-6.1" in control_ids  # Lawful Basis

    @pytest.mark.asyncio
    async def test_validation_detects_email(self, module):
        """Should detect email PII in content"""
        content = "Please contact redacted@shadowtag-v4.local for more information."
        violations = await module.validate_content(content)

        assert len(violations) > 0
        assert any(v.rule_id == "GDPR-VAL-001" for v in violations)


class TestCASB243Module:
    """Test cases for CA SB 243 module"""

    @pytest.fixture
    def module(self):
        return get_registry().get_module(RegulationId.CA_SB_243)

    def test_risk_tier_unacceptable_child_no_consent(self, module):
        """Child under 13 without consent should be unacceptable"""
        input_data = AssessmentInput(
            content_type="ai_assistant",
            user_age=10,
            metadata={"parental_consent_obtained": False},
        )
        risk = module.determine_risk_tier(input_data)
        assert risk == RiskTier.UNACCEPTABLE

    def test_risk_tier_high_child_with_consent(self, module):
        """Child under 13 with consent should be high risk"""
        input_data = AssessmentInput(
            content_type="ai_assistant",
            user_age=10,
            metadata={"parental_consent_obtained": True},
        )
        risk = module.determine_risk_tier(input_data)
        assert risk == RiskTier.HIGH

    @pytest.mark.asyncio
    async def test_validation_detects_self_harm(self, module):
        """Should detect self-harm content without resources"""
        content = "I want to hurt myself and end my life."
        violations = await module.validate_content(content)

        assert len(violations) > 0
        assert any(v.severity == "critical" for v in violations)


class TestHIPAAModule:
    """Test cases for HIPAA module"""

    @pytest.fixture
    def module(self):
        return get_registry().get_module(RegulationId.HIPAA)

    def test_risk_tier_high_phi(self, module):
        """PHI should be high risk"""
        input_data = AssessmentInput(
            content_type="medical_record",
            contains_phi=True,
        )
        risk = module.determine_risk_tier(input_data)
        assert risk == RiskTier.HIGH

    @pytest.mark.asyncio
    async def test_validation_detects_ssn(self, module):
        """Should detect SSN in content"""
        content = "Patient SSN: 123-45-6789"
        violations = await module.validate_content(content)

        assert len(violations) > 0
        assert any("PHI" in v.description for v in violations)
